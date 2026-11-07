# 05 — Ambiente

## Gestione con uv

- Python 3.12 (`.python-version`), pacchetto `agent-risk` in layout `src/`, build con `uv_build`.
- `uv sync` installa le dipendenze di base e il gruppo `dev` (`default-groups = ["dev"]`). `uv sync --group ml` aggiunge il gruppo dei modelli locali. `uv.lock` fissa tutte le versioni, compresi i gruppi non installati.
- Aggiungere una libreria: `uv add nome` (di base) oppure `uv add --group dev nome`.
- Comando installato: `agent-risk` (`stats`, `baselines`), definito in `src/agent_risk/cli.py`.

## Perché queste librerie

| Libreria | Uso |
|---|---|
| `huggingface-hub`, `datasets`, `pandas`, `pyarrow` | scaricare, caricare e analizzare il dataset |
| `scikit-learn`, `scipy`, `numpy` | metriche, validazione incrociata per gruppi (`GroupKFold`), classificatori classici (baseline lessicali, regressione) |
| **`clingo`** | ASP: policy, regole sui fattori, vincoli fra etichette (vedi [03](03-approccio-asp.md)) |
| `anthropic`, `tenacity` | LLM via API (estrazione dei fatti, baseline zero-shot), con ripetizioni sugli errori |
| `pydantic` | schema dei fatti estratti dall'LLM e validazione dell'output strutturato |
| `typer`, `rich`, `tqdm`, `python-dotenv`, `pyyaml` | riga di comando, tabelle, avanzamento, chiavi API, configurazioni |
| `pytest`, `ruff` | test e lint |
| `jupyterlab`, `ipykernel`, `matplotlib`, `seaborn` | esplorazione e grafici |
| gruppo `ml`: `torch`, `transformers`, `accelerate`, `peft`, `sentence-transformers`, `mapie` | modelli locali, fine-tuning leggero (LoRA), embedding, calibrazione con conformal prediction |

## Modelli locali e GPU

La mediana delle traiettorie supera i 512 token e arriva a circa 3.000: con **8 GB di GPU** servono encoder a contesto lungo o LLM piccoli quantizzati. Su Windows `torch` dal PyPI predefinito può installare la versione solo CPU; per CUDA aggiungere l'indice PyTorch adatto alla propria versione di CUDA in `pyproject.toml` (sezione `[tool.uv.sources]` e `[[tool.uv.index]]`). Il gruppo `ml` è pensato per essere configurato quando si arriva a quel punto; non è stato installato né provato.

## Chiavi e dati

- `.env` (ignorato) con `ANTHROPIC_API_KEY`; modello in `.env.example`.
- `data/raw/` ignorato da git; `scripts/download_data.py` lo ricostruisce alla revisione indicata (`--revision SHA`).
- `runs/` per predizioni e log degli esperimenti, anch'essa ignorata.

## Verifiche fatte il 7 novembre 2026

- `uv sync` ha installato 186 pacchetti risolti (gruppo `ml` incluso nel lockfile, non installato).
- `uv run pytest`: 9 test passati (metriche, scomposizione dei passi, equivalenza fra policy Python e ASP, forma del dataset, baseline costanti, vincolo congiunto delle etichette).
- `uv run agent-risk baselines`: MAE 1,217; Jaccard 0,455 e 0,455, come atteso.
- `ruff check`: nessun avviso.
