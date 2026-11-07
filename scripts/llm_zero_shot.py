"""Baseline zero-shot con Claude Opus 5.5 sui subtask 1, 2a e 2b (e 3 derivato con la policy d'esempio).

Campione: N traiettorie del train, una per gruppo di scenario, seme fisso. Il dev resta intatto.

Uso:
  uv run python scripts/llm_zero_shot.py estimate                       # costo stimato, nessuna spesa
  uv run python scripts/llm_zero_shot.py run --confirm --limit 3        # prova su 3 esempi
  uv run python scripts/llm_zero_shot.py run --confirm                  # tutto il campione
  uv run python scripts/llm_zero_shot.py evaluate                       # metriche

`run` riprende da dove si era fermato: gli esempi gia' riusciti in predictions.jsonl non vengono rifatti.
La chiave API va in `.env` (ANTHROPIC_API_KEY=...), ignorato da git. I risultati vanno in runs/, ignorata.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import anthropic
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

from agent_risk import data, llm
from agent_risk.labels import NO_HARM, NO_RISK, is_consistent
from agent_risk.metrics import intervention_f1, jaccard, mae
from agent_risk.policy import intervention

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "runs" / "opus55_zeroshot_train100"


def sample(split: str, n: int, seed: int) -> pd.DataFrame:
    """Una traiettoria per gruppo di scenario, poi n gruppi a caso; ordinato per example_id."""
    df = data.load_split(split)
    one_per_group = df.groupby("scenario_group", group_keys=False).sample(n=1, random_state=seed)
    picked = one_per_group.sample(n=min(n, len(one_per_group)), random_state=seed)
    return picked.sort_values("example_id").reset_index(drop=True)


def client() -> anthropic.Anthropic:
    load_dotenv(ROOT / ".env")
    try:
        return anthropic.Anthropic(max_retries=4, timeout=300.0)
    except anthropic.AnthropicError as e:
        sys.exit(f"Credenziali mancanti: metti ANTHROPIC_API_KEY=... in {ROOT / '.env'} ({e})")


def has_credentials() -> bool:
    import os

    load_dotenv(ROOT / ".env")
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


def cmd_estimate(args: argparse.Namespace) -> None:
    df = sample(args.split, args.n, args.seed)
    if has_credentials():
        c = client()
        tokens = [llm.count_input_tokens(c, s, args.variant)
                  for s in tqdm(df["formatted_interaction"], desc="token")]
        how = "conteggio esatto (count_tokens)"
    else:
        # stima prudente: 4 caratteri per token, +35% per il tokenizer di Opus, + prompt di sistema
        sys_tok = len(llm.system_prompt(args.variant)) / 4 * 1.35
        tokens = [int(len(s) / 4 * 1.35 + sys_tok) for s in df["formatted_interaction"]]
        how = "stima da caratteri (nessuna credenziale: conteggio esatto non disponibile)"
    tin = sum(tokens)
    print(f"Campione: {len(df)} traiettorie dal {args.split}, una per gruppo di scenario, seme {args.seed}")
    print(f"Token in ingresso: {tin:,} totali, {tin / len(df):,.0f} in media, max {max(tokens):,}  [{how}]")
    for label, per_ex in (("basso", 800), ("medio", 1500), ("alto", 3000)):
        tout = per_ex * len(df)
        print(f"  uscita {label:5} ({per_ex} token/esempio, ragionamento incluso): "
              f"{llm.cost(tin, tout, args.model):.2f} dollari")
    ph = llm.prompt_hash(args.variant, args.model)
    print(f"Modello {args.model}, variante {args.variant}, prompt {ph}")


def refused_ids(run_dir: Path) -> list[str]:
    """Esempi rifiutati (stop_reason refusal) nell'ultimo tentativo di un run precedente."""
    last = {}
    for line in (run_dir / "predictions.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        last[r["example_id"]] = r
    return sorted(i for i, r in last.items() if r.get("stop_reason") == "refusal")


def default_out(model: str, variant: str) -> Path:
    if model == llm.MODEL and variant == "base":
        return DEFAULT_OUT
    tag = model.removeprefix("claude-").replace("-", "")
    return ROOT / "runs" / f"{tag}_zeroshot_train100_{variant}"


def cmd_run(args: argparse.Namespace) -> None:
    if not args.confirm:
        sys.exit("Le chiamate costano: aggiungi --confirm (prima guarda il costo con `estimate`).")
    df = sample(args.split, args.n, args.seed)
    if args.from_refused:
        ids = refused_ids(args.from_refused)
        df = df[df["example_id"].isin(ids)].reset_index(drop=True)
        print(f"Solo i {len(df)} rifiutati di {args.from_refused}")
    if args.limit:
        df = df.head(args.limit)
    out: Path = args.out or default_out(args.model, args.variant)
    out.mkdir(parents=True, exist_ok=True)
    pred_path = out / "predictions.jsonl"

    done = set()
    if pred_path.exists():
        for line in pred_path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if "risk_severity" in r or r.get("stop_reason") == "refusal":
                done.add(r["example_id"])
    todo = df[~df["example_id"].isin(done)]

    config = {
        "model": args.model, "effort": args.effort, "variant": args.variant,
        "prompt_hash": llm.prompt_hash(args.variant, args.model),
        "from_refused": str(args.from_refused) if args.from_refused else None,
        "split": args.split, "n": args.n, "seed": args.seed, "data_revision": data.revision(),
        "example_ids": df["example_id"].tolist(), "started": datetime.now(UTC).isoformat(),
    }
    (out / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"{len(todo)} da fare, {len(done)} gia' fatti; {args.model}, variante {args.variant}, "
          f"effort {args.effort}; {args.workers} in parallelo; output {out}")

    c = client()
    lock = threading.Lock()
    spent = 0.0
    with ThreadPoolExecutor(max_workers=args.workers) as pool, pred_path.open("a", encoding="utf-8") as f:
        futures = {
            pool.submit(llm.assess, c, row.formatted_interaction, args.effort, args.variant, args.model):
                row.example_id
            for row in todo.itertuples()
        }
        for fut in tqdm(as_completed(futures), total=len(futures), desc="chiamate"):
            rec = {"example_id": futures[fut], **fut.result()}
            with lock:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                spent += rec.get("cost_usd", 0.0)
    print(f"Spesa di questo run: {spent:.2f} dollari. Risultati in {pred_path}")


def _no_risk(domains: list[str]) -> bool:
    return domains == [NO_HARM]


def cmd_evaluate(args: argparse.Namespace) -> None:
    args.out = args.out or default_out(args.model, args.variant)
    pred_path = args.out / "predictions.jsonl"
    recs = {}
    for line in pred_path.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        recs[r["example_id"]] = r  # l'ultimo tentativo vince
    config = json.loads((args.out / "config.json").read_text(encoding="utf-8"))
    gold = data.load_split(config["split"]).set_index("example_id").loc[list(recs)]

    ok = [i for i, r in recs.items() if "risk_severity" in r]
    refused = [i for i, r in recs.items() if r.get("stop_reason") == "refusal"]
    failed = [i for i, r in recs.items() if i not in ok and i not in refused]
    g, p = gold.loc[ok], [recs[i] for i in ok]

    gl, pl = list(g["risk_severity"]), [r["risk_severity"] for r in p]
    gd, pd_ = [list(x) for x in g["risk_domains"]], [r["risk_domains"] for r in p]
    gf, pf = [list(x) for x in g["risk_drivers"]], [r["risk_drivers"] for r in p]
    risky = [k for k, d in enumerate(gd) if not _no_risk(d)]
    gi = [intervention(a, b, c) for a, b, c in zip(gl, gd, gf, strict=True)]
    pi = [intervention(a, b, c) for a, b, c in zip(pl, pd_, pf, strict=True)]

    m = {
        "esempi": len(recs), "risposte valide": len(ok), "rifiuti": len(refused), "errori": len(failed),
        "subtask 1 MAE": mae(gl, pl),
        "subtask 1 MAE baseline 'sempre 2'": mae(gl, [2] * len(gl)),
        "subtask 1 MAE solo esempi rischiosi": mae([gl[k] for k in risky], [pl[k] for k in risky]),
        "subtask 1 accuratezza esatta": sum(a == b for a, b in zip(gl, pl, strict=True)) / len(gl),
        "rischioso / senza rischio, accuratezza": sum(
            _no_risk(a) == _no_risk(b) for a, b in zip(gd, pd_, strict=True)) / len(gd),
        "subtask 2a Jaccard": jaccard(gd, pd_),
        "subtask 2a Jaccard baseline 'No Material Harm'": jaccard(gd, [[NO_HARM]] * len(gd)),
        "subtask 2b Jaccard": jaccard(gf, pf),
        "subtask 2b Jaccard baseline 'No Material Risk'": jaccard(gf, [[NO_RISK]] * len(gf)),
        "subtask 3 (policy d'esempio) F1 macro": intervention_f1(gi, pi, "macro"),
        "subtask 3 (policy d'esempio) F1 pesato": intervention_f1(gi, pi, "weighted"),
        "previsioni che violano il vincolo congiunto": sum(
            not is_consistent(a, b, c) for a, b, c in zip(pl, pd_, pf, strict=True)),
        "costo totale (dollari)": sum(r.get("cost_usd", 0.0) for r in recs.values()),
        "latenza media (s)": sum(r.get("latency_s", 0.0) for r in recs.values()) / len(recs),
    }
    for k, v in m.items():
        print(f"{k:50} {v:.3f}" if isinstance(v, float) else f"{k:50} {v}")

    print("\nLivello vero (righe) x previsto (colonne):")
    cm = pd.crosstab(pd.Series(gl, name="vero"), pd.Series(pl, name="previsto"))
    print(cm.reindex(index=range(1, 6), columns=range(1, 6), fill_value=0))

    big = [(i, a, b) for i, a, b in zip(ok, gl, pl, strict=True) if abs(a - b) >= 2]
    listed = ", ".join(f"{i} ({a}->{b})" for i, a, b in big) or "nessuno"
    print(f"\nErrori di livello >= 2 ({len(big)}):", listed)
    if refused:
        cats = collections.Counter(recs[i].get("refusal_category") for i in refused)
        print("Rifiuti:", ", ".join(refused), dict(cats))
    if failed:
        print("Errori:", "; ".join(f"{i}: {recs[i].get('error')}" for i in failed))

    m["confusion_matrix"] = cm.to_dict()
    m["errori_livello_ge2"] = big
    (args.out / "metrics.json").write_text(json.dumps(m, indent=2, ensure_ascii=False, default=str),
                                           encoding="utf-8")
    print(f"\nSalvato {args.out / 'metrics.json'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", default="train", choices=["train", "dev"])
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=None, help="default: runs/<modello>_..._<variante>")
    ap.add_argument("--model", default=llm.MODEL, choices=list(llm.PRICES))
    ap.add_argument("--variant", default="base", choices=list(llm.VARIANTS))
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("estimate", help="costo stimato, nessuna chiamata a pagamento")
    r = sub.add_parser("run", help="esegue le chiamate (a pagamento)")
    r.add_argument("--confirm", action="store_true", help="obbligatorio: conferma la spesa")
    r.add_argument("--limit", type=int, default=0, help="solo i primi K esempi del campione")
    r.add_argument("--from-refused", type=Path, default=None,
                   help="cartella di un run precedente: rifà solo gli esempi rifiutati")
    r.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    r.add_argument("--workers", type=int, default=8)
    sub.add_parser("evaluate", help="metriche sulle previsioni salvate")
    args = ap.parse_args()
    {"estimate": cmd_estimate, "run": cmd_run, "evaluate": cmd_evaluate}[args.cmd](args)


if __name__ == "__main__":
    main()
