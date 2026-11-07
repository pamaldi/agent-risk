# agent-risk

Progetto di lavoro per **SemEval 2027, Task 10 — AgentRisk**: valutazione del rischio e intervento guidato da policy su traiettorie di agenti LLM. Creato il 7 novembre 2026 dall'archivio `ai-resources` (cartella `lavori/2026-09_semeval-2027`), dove restano le schede di valutazione complete.

**Stato:** nessun esperimento eseguito. Il progetto contiene i dati, gli strumenti di base (caricamento, metriche ufficiali, baseline costanti, policy d'esempio in Python e in ASP) e la documentazione di tutto ciò che si è stabilito finora. La decisione di partecipare non è presa: vedi [docs/06-decisioni-e-domande-aperte.md](docs/06-decisioni-e-domande-aperte.md).

## Avvio in PyCharm

1. **File → Open** e scegliere `C:\svi\agent-risk`.
2. PyCharm riconosce `pyproject.toml` e `uv.lock`. Se non crea da solo l'interprete: **Settings → Project → Python Interpreter → Add Interpreter → Add Local Interpreter**, tipo **uv**, ambiente esistente `.venv` del progetto.
3. Per i notebook il kernel è quello di `.venv` (`ipykernel` è già nel gruppo `dev`).
4. Marcare `src` come *Sources Root* e `tests` come *Test Sources Root* (tasto destro sulla cartella → *Mark Directory as*), se PyCharm non lo fa.

Da terminale, nella cartella del progetto:

```bash
uv sync
```

```bash
uv run python scripts/download_data.py
```

```bash
uv run pytest
```

```bash
uv run agent-risk stats
```

```bash
uv run agent-risk baselines
```

`uv sync` crea `.venv` con le librerie di base e di sviluppo; `download_data.py` scarica il dataset in `data/raw` (già fatto) e fissa la revisione; `pytest` esegue 9 test; gli ultimi due comandi stampano le statistiche di train e dev e le baseline costanti sul dev.

## Contenuto

| Percorso | Che cosa |
|---|---|
| [docs/](docs/) | documentazione: task, dati, approccio con ASP, pilota, ambiente, decisioni e domande aperte |
| `data/raw/` | dataset ufficiale `AgentRisk/agentrisk-data-2027` (train 568, dev 143, manifest degli scenari). Revisione fissata in `data/raw/REVISION.txt`. **Non è versionato** in git: la scheda del dataset non dichiara una licenza |
| `src/agent_risk/labels.py` | tassonomie (livelli, 11 domini, 7 fattori, 5 interventi) e vincolo congiunto della classe «senza rischio» |
| `src/agent_risk/data.py` | caricamento di train, dev e gruppi di scenario; scomposizione della traiettoria in passi |
| `src/agent_risk/metrics.py` | MAE, Jaccard medio, F1 dell'intervento |
| `src/agent_risk/baselines.py` | baseline costanti |
| `src/agent_risk/policy.py` e `asp/` | policy d'esempio in Python e in ASP (clingo), con test di equivalenza |
| `scripts/download_data.py` | scarica il dataset e registra la revisione |
| `notebooks/` | esplorazione (vuota) |
| `runs/` | predizioni e log degli esperimenti (ignorata da git) |

## Librerie

Di base: `huggingface-hub`, `datasets`, `pandas`, `pyarrow`, `numpy`, `pydantic`, `scikit-learn`, `scipy`, **`clingo`** (ASP), `anthropic` con `tenacity`, `typer`, `rich`, `tqdm`, `python-dotenv`, `pyyaml`. Gruppo `dev` (installato di default): `pytest`, `ruff`, `ipykernel`, `jupyterlab`, `matplotlib`, `seaborn`. Gruppo `ml` (non installato di default, `uv sync --group ml`): `torch`, `transformers`, `accelerate`, `peft`, `sentence-transformers`, `mapie`. Dettagli e note sulla GPU in [docs/05-ambiente.md](docs/05-ambiente.md).

La chiave API per i modelli Anthropic va messa in `.env` (modello in `.env.example`); il file è ignorato da git.
