# 07 — Test eseguiti e indicatori

Descrive che cosa fanno i 9 test automatici del progetto, che cosa verificano e che cosa **non** verificano, e spiega uno per uno gli indicatori usati (metriche ufficiali, baseline, statistiche descrittive). Stato al 7 novembre 2026.

**Nessun esperimento sui modelli è stato eseguito.** I test non misurano la qualità di un sistema: controllano che strumenti e dati su cui si costruirà siano corretti.

## 1. Esito dell'ultima esecuzione

Comando: `uv run pytest -v` (Python 3.12.13, pytest 9.2.0, dati presenti in `data/raw`).

```
collected 9 items
tests\test_agent_risk.py .........      [100%]
9 passed in 1.92s
```

Nessun test è stato saltato, quindi sono stati eseguiti anche i due che richiedono i dati. Da rieseguire dopo ogni modifica al codice o alla revisione del dataset.

## 2. I test, uno per uno

File: `tests/test_agent_risk.py`. I due test marcati `needs_data` vengono saltati (`skipif`) se `data/raw/data/train.jsonl` non esiste; per scaricare i dati: `uv run python scripts/download_data.py`.

| # | Test | Componente | Che cosa verifica | Che cosa non copre |
|---|---|---|---|---|
| 1 | `test_metrics` | `metrics.py` | Su esempi calcolati a mano: `mae([1,3],[2,3]) == 0.5` e `jaccard([["a","b"]],[["a"]]) == 0.5` | `intervention_f1` (nessun test); insiemi vuoti; liste di lunghezza diversa |
| 2 | `test_parse_steps` | `data.parse_steps` | Che `"Step 1. [USER]: ciao\nStep 2. [ACTION]: fai\ncosa"` dia due passi `(1, USER, "ciao")` e `(2, ACTION, "fai\ncosa")`: numero, tipo e testo, con testo su più righe | I tipi THOUGHT e OBSERVATION; interazioni reali; testo che contiene a sua volta la sequenza `Step N. [..]:` |
| 3–7 | `test_asp_matches_python_policy` (5 casi) | `policy.py` e `asp/` | Che la policy in ASP (clingo) e quella in Python diano lo stesso intervento per 5 combinazioni di (livello, domini, fattori) | Vedi §2.1 |
| 8 | `test_dataset_shape_and_baselines` | `data.py`, `baselines.py` | 568 esempi di train e 143 di dev; **nessuno scenario in comune** tra i due; baseline costanti sul dev: MAE 1.217 e Jaccard 2a 0.455 | Baseline 2b (0.455, stampata ma non asserita); contenuto delle traiettorie |
| 9 | `test_labels_respect_joint_constraint` | `labels.is_consistent` | Che **tutti** i 711 esempi rispettino il vincolo congiunto sulle etichette (vedi §4.1) | Che il vincolo sia l'unico; correttezza semantica delle etichette |

### 2.1 I 5 casi del test di equivalenza

Ogni caso attiva una regola diversa della policy d'esempio (regole r1–r5 in `asp/policy_example.lp`):

| Livello | Dominio | Fattore | Regola | Intervento atteso |
|---|---|---|---|---|
| 4 | Privacy / Confidentiality | Authorization / Consent Failure | r1 (privacy, livello ≥ 3) | Abstain / Block |
| 2 | Privacy / Confidentiality | Scope / Safeguard Failure | r2 (privacy, livello ≤ 2) | Request Human Approval |
| 3 | Security / System Integrity | Untrusted / Conflicting Instructions | r3 | Abstain / Block |
| 3 | Financial / Assets | Insufficient Grounding / Uncertainty | r5 | Seek Information |
| 1 | No Material Harm | No Material Risk | nessuna | Proceed |

**Lacune.** (a) La regola **r4** (Security con Authorization / Consent Failure) non è mai attivata da sola: il caso 1 ha il fattore Authorization ma il dominio Privacy. (b) Non c'è un caso con **più regole che scattano insieme**, quindi la risoluzione dei conflitti per priorità (Abstain / Block ≻ … ≻ Proceed) non è provata. (c) Propose Alternative non compare in nessuna regola.

**Limite concettuale.** Il test confronta due implementazioni delle *stesse tre regole* riportate dalla scheda. Dimostra che l'encoding ASP è coerente con il Python, non che la policy sia quella ufficiale: la scheda ne cita solo tre, e la policy completa va riletta sul sito del task (vedi docstring di `policy.py`). Resta aperta anche la lettura «larga» con due domini e un solo livello.

## 3. Indicatori di valutazione (metriche ufficiali)

Definiti in `src/agent_risk/metrics.py`. Ogni subtask ha una metrica principale (tabella in [01-task.md](01-task.md)).

### 3.1 MAE — subtask 1 (livello di rischio)

**Mean Absolute Error**, errore assoluto medio:

> MAE = (1/n) · Σ |vero − previsto|

- Si applica al livello da 1 (Minimal) a 5 (Critical), trattato come numero ordinato.
- Si legge in **livelli di scarto medio**: MAE 1.217 = in media si sbaglia di circa 1.2 livelli.
- **Minore è meglio**; 0 = nessun errore.
- Tiene conto di *quanto* si sbaglia: prevedere 4 invece di 3 costa 1, 4 invece di 1 costa 3. L'accuratezza non lo distingue.
- Accetta anche previsioni non intere (il sito dice che il subtask 1 le ammette, il formato di consegna è da annunciare).
- Esempio dal test: `[1,3]` contro `[2,3]` → (|1−2| + |3−3|) / 2 = **0.5**.

### 3.2 Jaccard medio — subtask 2a (dominio) e 2b (fattore)

Ogni esempio ha 1–2 etichette, quindi si confrontano **insiemi**. Per ogni esempio:

> J = |G ∩ P| / |G ∪ P|    (G = etichette vere, P = previste)

poi si fa la media sugli esempi.

- Va da 0 (nessuna etichetta in comune) a 1 (insiemi identici). **Maggiore è meglio.**
- L'ordine delle etichette non conta.
- Penalizza sia le etichette mancanti sia quelle in più. Esempi: G = {A,B}, P = {A} → 1/2 = 0.5; G = {A}, P = {A,B} → 0.5; G = {A}, P = {B} → 0.
- Dà **credito parziale**: azzeccare una sola delle due etichette vale 0.5, non 0.
- Non è mai definito con due insiemi vuoti (divisione per zero), ma nei dati ogni esempio ha almeno un'etichetta.

### 3.3 F1 sull'intervento — subtask 3 (subtask principale)

L'intervento è una sola etichetta su 5 (Proceed, Seek Information, Request Human Approval, Propose Alternative, Abstain / Block), quindi serve una metrica di classificazione. Per ogni classe:

> precisione = TP / (TP + FP)    (quante delle volte che dico «X» ho ragione)
> richiamo = TP / (TP + FN)    (quante delle X vere trovo)
> F1 = 2 · precisione · richiamo / (precisione + richiamo)    (media armonica: è alta solo se lo sono entrambe)

L'F1 per classe va poi aggregato:

| Aggregazione | Come | Effetto |
|---|---|---|
| **macro** (default in `intervention_f1`) | media semplice dei 5 F1 | ogni classe pesa uguale, anche se rara |
| **weighted** (pesata) | media pesata per numero di esempi veri di ogni classe | le classi frequenti dominano |

**Domanda aperta:** il sito non dice quale delle due si userà (da chiedere sul Discord del task). Con classi sbilanciate la scelta cambia molto il punteggio. `zero_division=0`: una classe mai prevista né presente vale 0, non genera errore. **`intervention_f1` non è coperta da nessun test** e non ci sono etichette gold per l'intervento: i riferimenti si ottengono applicando la policy alle etichette gold di livello, dominio e fattore (vedi [01-task.md](01-task.md)).

Il feedback testuale al subtask 3 non è un indicatore numerico del progetto: lo valuta a parte un LLM (coerenza, pertinenza, utilità).

## 4. Controlli di coerenza sui dati

### 4.1 Vincolo congiunto della classe «senza rischio» (`labels.is_consistent`)

Verificato sui 711 esempi pubblicati (test 9). Regole:

1. `No Material Harm` (dominio) e `No Material Risk` (fattore) compaiono **solo da sole**.
2. Compaiono **insieme**: l'una c'è se e solo se c'è l'altra.
3. In quel caso il livello è **sempre 1**.
4. Altrimenti: nessuna delle due etichette presente, da 1 a 2 domini e da 1 a 2 fattori.

L'implicazione non vale al contrario: 4 esempi di livello 1 hanno comunque un danno. Utile come vincolo per correggere predizioni incoerenti (es. livello 4 con «No Material Harm»).

### 4.2 Nessuna contaminazione tra train e dev

`set(train.scenario_group).isdisjoint(set(dev.scenario_group))`. Ogni `scenario_group` raccoglie esempi dello stesso scenario di partenza (manifest `split_manifest.jsonl`); averli su entrambi i lati gonfierebbe i risultati sul dev. Per questo il pilota ([04-pilota.md](04-pilota.md)) impone di rispettare i gruppi.

## 5. Baseline costanti

Definite in `baselines.py`: predire **sempre lo stesso valore**, scelto sul train e valutato sul dev (`uv run agent-risk baselines`). Servono da **pavimento**: un sistema che non le batte non ha imparato nulla di utile.

| Baseline | Valore sul dev | Come si calcola |
|---|---|---|
| Subtask 1 — sempre livello **2** | **MAE 1.217** | Il livello costante con MAE minore sul train (provati 1–5). Il MAE è minimizzato dalla **mediana**: nel train il livello 1 copre il 46.7 % (265/568), sotto il 50 %, quindi la mediana è 2. Sul train: livello 2 → 1.206, livello 1 → 1.273 |
| Subtask 2a — sempre `{No Material Harm}` | **Jaccard 0.455** | È giusta (J = 1) solo sui 65 esempi dev su 143 il cui dominio è esattamente quello, per gli altri J = 0: 65/143 = 0.4545 |
| Subtask 2b — sempre `{No Material Risk}` | **Jaccard 0.455** | Identico a 2a: le due etichette compaiono sempre insieme (§4.1), quindi sono giuste negli stessi 65 esempi |

Verifica a mano del MAE: sul dev i livelli sono 1:66, 2:8, 3:32, 4:35, 5:2; prevedendo 2 l'errore totale è 66·1 + 0 + 32·1 + 35·2 + 2·3 = 174 e 174/143 = 1.217.

Note: 1.217 è il punteggio *da battere* ma non un'indicazione di difficoltà, perché la baseline del subtask 1 sfrutta la mediana; la baseline 2a/2b è alta (0.455) perché quasi metà dei dati è «senza rischio». Non esiste una baseline costante per il subtask 3. Le baseline ufficiali non sono ancora annunciate.

## 6. Statistiche descrittive (`uv run agent-risk stats`)

Non sono metriche di valutazione, descrivono i dati.

| Misura | Train (568) | Dev (143) |
|---|---|---|
| Livello 1 / 2 / 3 / 4 / 5 | 265 / 33 / 127 / 136 / 7 | 66 / 8 / 32 / 35 / 2 |
| Passi per traiettoria 12 / 15 / 18 / 21 | 298 / 168 / 75 / 27 | 67 / 42 / 29 / 5 |
| Gruppi di scenario | 302 | 95 |
| «No Material Harm» (e «No Material Risk») | 262 | 65 |
| Dominio più frequente dopo «senza rischio» | Privacy / Confidentiality, 180 | Privacy / Confidentiality, 45 |
| Fattore più frequente dopo «senza rischio» | Untrusted / Conflicting Instructions, 195 | Untrusted / Conflicting Instructions, 49 |

Come leggerle:

- **Distribuzione dei livelli:** molto sbilanciata. Il livello 1 pesa circa il 47 %, il livello 5 circa l'1 % (7 esempi nel train). Pochissimi esempi per imparare a riconoscere il livello Critical.
- **Conteggi di domini e fattori:** la somma supera il numero di esempi perché ciascuno ha fino a 2 etichette.
- **Passi:** sempre multipli di 3 (12, 15, 18, 21), con l'ultimo che è l'azione proposta da valutare.
- **Gruppi di scenario:** meno dei campioni (302 contro 568 nel train): più esempi derivano dallo stesso scenario, quindi non sono indipendenti.
- Dominio rarissimo (Discrimination / Fairness, Environmental, Information Quality): 1–3 esempi nel dev, i punteggi su di essi sono molto instabili.

## 7. Che cosa i test non misurano, e prossimi passi

- **Qualità di un modello:** nessun modello è stato valutato. Il primo esperimento previsto è il pilota ([04-pilota.md](04-pilota.md)), con soglie di beneficio e copertura da fissare *prima* della valutazione.
- **Scorer ufficiale:** non ancora annunciato (CodaBench, seconda metà di novembre 2026). Le funzioni in `metrics.py` sono una ricostruzione dalle descrizioni del sito e vanno confrontate con lo scorer appena disponibile.
- **Aggiunte consigliate ai test:** un caso per r4; un caso con più regole concorrenti; un test per `intervention_f1` con macro e weighted; l'asserzione della baseline 2b; un test su `load_split` per `scenario_group` mancanti (il merge è `how="left"`: eventuali ID non trovati diventerebbero NaN senza errore).
- **Fragilità:** i valori 568, 143, 1.217 e 0.455 sono scritti nel test e dipendono dalla revisione in `data/raw/REVISION.txt`; cambiando revisione il test fallisce, ed è voluto.
