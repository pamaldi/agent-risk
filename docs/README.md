# Documentazione

Riassume tutto ciò che è stato discusso e stabilito su AgentRisk fino al 7 novembre 2026. Le fonti originali restano nell'archivio `ai-resources`, cartella `lavori/2026-09_semeval-2027` (schede, valutazione scientifica, autori, pilota).

| File | Contenuto |
|---|---|
| [01-task.md](01-task.md) | che cos'è il task, input e output, subtask, etichette, policy, metriche, calendario, premi |
| [02-dati.md](02-dati.md) | dataset, statistiche, proprietà verificate, due record reali commentati, che cosa dice (e non dice) la struttura |
| [03-approccio-asp.md](03-approccio-asp.md) | proposta LLM + ASP: dove è adatta, dove no, schizzo dell'encoding |
| [04-pilota.md](04-pilota.md) | pilota di tre giornate, confronto A/B/C, criteri di decisione |
| [05-ambiente.md](05-ambiente.md) | librerie, gruppi uv, GPU, riproducibilità |
| [06-decisioni-e-domande-aperte.md](06-decisioni-e-domande-aperte.md) | decisioni, ipotesi, domande agli organizzatori, organizzatori e letteratura, idee scartate o rimandate (diffusion model, baseline lessicale) |
| [07-test-e-indicatori.md](07-test-e-indicatori.md) | i 9 test automatici (che cosa verificano e che cosa no), spiegazione di MAE, Jaccard, F1, baseline e statistiche sui dati |
| [08-policy.md](08-policy.md) | la policy del subtask 3 da zero: regole, priorità, default, una policy alternativa a confronto, due record reali del dataset con la policy applicata regola per regola |
| [09-baseline-llm.md](09-baseline-llm.md) | baseline zero-shot con Claude Opus 5.5, 4.8 e 4.6 su 100 traiettorie: rifiuti di Opus 5.5, risultati di Opus 4.8, errori sistematici, costi |

Convenzione: ciò che è **verificato sui dati o sul sito** è scritto come fatto; ciò che è **proposta o ipotesi** è dichiarato tale. L'unico esperimento eseguito finora è la baseline zero-shot con LLM del 7 novembre 2026 ([09](09-baseline-llm.md)); il pilota ([04](04-pilota.md)) non è ancora stato fatto.
