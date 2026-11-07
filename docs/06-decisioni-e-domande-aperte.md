# 06 — Decisioni, ipotesi, domande aperte, organizzatori, letteratura

## Stato della decisione

La condizione posta il 22 settembre 2026 per valutare il task è **soddisfatta**: il subtask 3 è a selezione e la policy d'esempio è esplicita. Resta il vincolo di risorse: con DiCo-NLI avviato come impegno principale e ComPartMENT fra i task fattibili, tre impegni con valutazione a gennaio sono troppi. **AgentRisk entrerebbe al posto di ComPartMENT**, non in aggiunta. La squadra si registra solo dopo questa scelta. Il pilota di tre giornate ([04](04-pilota.md)) serve a decidere.

## Domanda di ricerca e ipotesi

**Domanda.** Quando la policy è un insieme di regole su livello, dominio e fattore, conviene predire queste tre etichette e calcolare l'intervento con la policy, oppure predire l'intervento direttamente dalla traiettoria? E rendere esplicita la struttura della situazione migliora le tre etichette?

Stato esplicito σ(τ) = (obiettivo dell'utente, azione proposta, risorse coinvolte, autorizzazioni concesse, reversibilità, portata).

- **H1:** estrarre σ(τ) e applicare regole migliora soprattutto i casi in cui il rischio dipende da un'autorizzazione concessa o negata molti turni prima.
- **H2:** la pipeline simbolica (predire livello, dominio, fattore e applicare la policy) supera un classificatore diretto sull'intervento quando la policy cambia, perché non richiede di riaddestrare. Limite: propagazione degli errori dei subtask 1–2.
- **H3:** imporre in decodifica il vincolo congiunto della classe «senza rischio» migliora i tre subtask insieme, come i vincoli di inversione in DiCo-NLI.

## Domande da fare agli organizzatori (Discord del task)

1. Come si applicano le regole per dominio quando i domini sono due e il livello è uno? Una regola come «Financial / Assets a livello 4–5» scatta anche se il livello alto dipende dall'altro dominio?
2. L'F1 del subtask 3 è macro o pesato? La metrica distingue il comportamento prudente e utile dal blocco sistematico?
3. Le policy di gara useranno solo livello, dominio e fattore o anche altri elementi (autorizzazione, reversibilità, informazione disponibile)?
4. Il subtask 1 accetta livelli non interi?
5. Propose Alternative compare nell'ordine di priorità ma in nessuna regola d'esempio: sarà usato nelle policy di gara?
6. Qual è l'accordo fra annotatori su livello, domini e fattori? In AURA-Eval, degli stessi autori, l'accordo umano sul riconoscimento del rischio è basso (α 0,51): serve a capire il tetto raggiungibile.

Stato: **nessuna domanda ancora inviata.** La registrazione della squadra non è fatta.

## Rischi e limiti

- **Policy di gara note tardi** (a ridosso del 10 gennaio): rendere il sistema indipendente dalla policy specifica.
- **Propagazione dell'errore** dai subtask 1–2 all'intervento.
- **Policy con fattori non etichettati:** se useranno autorizzazione o reversibilità servono predittori per etichette che il dataset non fornisce.
- **Contaminazione:** InjecAgent è pubblico dal 2024; i modelli recenti potrebbero averlo visto. Possibili scorciatoie lessicali.
- **Contesto lungo:** fino a circa 3.000 token.
- **Classi rare:** domini con un solo esempio nel dev rendono instabile la scelta dei modelli.
- **Feedback giudicato da un LLM:** non entra nella metrica principale ma, per le squadre in testa, aggiunge costo e variabilità.
- **Dati sintetici:** se si generano varianti rischiose e sicure di uno scenario, va tenuta d'occhio la contaminazione con InjecAgent.

## Idee valutate e non adottate o rimandate

### Baseline lessicale sull'ultimo passo (proposta, non eseguita)

Poiché la sequenza dei tipi non predice il rischio ([02](02-dati.md)) e il rifiuto dell'agente equivale a «senza rischio», conviene misurare quanto si ottiene guardando **solo il testo dell'azione proposta** (n-grammi o TF-IDF con regressione logistica, validazione per `scenario_group`). Se fosse già vicino a un LLM, il dataset avrebbe scorciatoie lessicali. È la prima cosa da fare con `scikit-learn` e un costo di poche ore.

### Modelli a diffusione (discussione del 7 novembre 2026)

Domanda: AgentRisk si può affrontare con un approccio simile ai diffusion model? Valutazione sull'architettura, **nessuna prova su questo dataset**:

- **Dove avrebbe senso:** i modelli di linguaggio a diffusione discreta generano il testo rimuovendo gradualmente token mascherati, in parallelo. Potrebbero produrre livello, domini, fattori, intervento e feedback congiuntamente, rispettando meglio i vincoli fra etichette; il guidaggio con un verificatore esterno (qui il programma ASP) è un'idea studiata, ma qui resta speculativa.
- **Dove non aiuta:** i vincoli sono pochi e semplici, e si impongono già con una decodifica vincolata o con ASP; i dati sono 568 esempi di training, troppo pochi per adattare un modello a diffusione battendo un LLM ben promptato o un classificatore; soprattutto il collo di bottiglia è capire chi comanda cosa e da dove viene l'istruzione, cioè estrarre i fatti giusti, e la forma della generazione non cambia questo.
- **Uso più sensato:** generare **dati sintetici** (varianti rischiose e sicure dello stesso scenario, sul modello delle coppie già presenti). Lo fa altrettanto bene un LLM normale.

Conclusione: interessante come esplorazione, ma l'approccio con estrazione dei fatti e regole è più vicino al collo di bottiglia reale.

### Altre direzioni citate in letteratura (non perseguite)

Calibrazione dell'incertezza e conformal prediction, per la presenza di Zerva e Martins fra gli organizzatori (lavori su quality estimation): non è detto che il task la richieda; da riconsiderare se i dati o lo scorer lo suggeriscono. Il gruppo `ml` include `mapie` per questo.

## Organizzatori (verifica del 19 settembre 2026)

Giudizio: gruppo **scientificamente solido**, interlocutori seri; l'incertezza principale riguarda la realizzazione e la validazione del benchmark, non le credenziali.

- **André F. T. Martins** — il nome di maggior peso: ERC Starting Grant e ERC Consolidator Grant, Program Co-Chair di ACL 2024, lavori su modelli strutturati, sparsemax, valutazione e generazione. <https://andre-martins.github.io/>
- **Orfeas Menis Mastromichalakis** — lead. Lavori su bias, spiegabilità e valutazione (*Assumed Identities*, EMNLP 2025; *Don't Erase, Inform!*, ACL 2025, entrambi come primo autore); coautore di *Terminal-Bench* (ICLR 2026). Contatto: menisorfeas@gmail.com. <https://menisorfeas.com/>
- **Giorgos Filandrianos** — co-lead; spiegazioni controfattuali, reasoning, valutazione degli LLM; esperienza di organizzazione SemEval (CLARITY 2026). <https://geofila.github.io/>
- **Chrysoula (Chryssa) Zerva** — incertezza, qualità della traduzione, affidabilità e valutazione.
- **Ruoxi (Anna) Shang** — valutazione di agenti (*BLADE*, Findings of EMNLP 2024), prima autrice di AURA-Eval; Research Fellow in Oumi AI su un benchmark di «semantic risk reasoning». <https://ruoxishang.com/>
- **Emmanouil (Manos) Koukoumidis** — CEO di Oumi, coautore di AURA-Eval.
- Angelos Vlachos, Beatriz Canaverde, Maria Sambani: nessun giudizio individuale (elementi insufficienti, non è un giudizio negativo).

**AURA-Eval** (Shang, Androna, Menis Mastromichalakis et al., *AURA-Eval: Evaluation Framework for Acting Under Risk Awareness in LLM Agent Trajectories*, preprint del 6 settembre 2026, <https://arxiv.org/abs/2609.06783>): 1.249 esempi da 157 traiettorie, 20 modelli, varianti con e senza modalità sicura. È un preprint; non è verificato che sia la base ufficiale del dataset AgentRisk.

**Lettura del 7 novembre 2026** (versione 2 del 19 ottobre 2026; letti l'abstract e la prima metà del testo HTML, non le tabelle complete in appendice):

- **Misura un'altra cosa.** AURA-Eval interrompe una traiettoria in un punto critico e chiede al modello di *continuarla* (prossimo pensiero e prossima azione), poi giudica se il comportamento è sicuro. AgentRisk invece chiede di *valutare* un'azione già proposta. I 1.249 esempi derivano da 157 traiettorie di R-Judge. Le etichette non coincidono: non ci sono livelli 1–5; i «domini» sono 5 aree applicative (Application, Finance, IoT, Program, Web); al posto dei fattori ci sono sei meccanismi di rischio (intensità del danno, portata, vulnerabilità del bersaglio, dipendenza dei sistemi, supervisione, reversibilità); i tipi di azione (esecuzione diretta, chiedere informazioni, chiedere conferma, raccogliere dati, proporre alternativa, rifiutare) somigliano agli interventi del subtask 3 ma non sono gli stessi. SemEval e AgentRisk non sono citati nella parte letta.
- **Risultati principali** (20 modelli, fra cui Claude Opus 4.6 e Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro): il migliore è Claude Sonnet 4.6 con il 16,9% di azioni non sicure; i modelli di frontiera agiscono in modo non sicuro nel 5–7% dei casi quando esiste una strada sicura e nel 27–40% quando non esiste; gli open-weight nel 58–83% dei casi senza strada sicura. Togliere la supervisione prima dell'esecuzione rende non sicuro il 52,3% dei casi prima sicuri.
- **Accordo tra annotatori umani:** α di Krippendorff 0,76 sulla sicurezza dell'azione, 0,73 sul tipo di azione, solo 0,51 sul riconoscimento del rischio nel ragionamento. Il giudice (panel di LLM) concorda con le persone nel 76,5% dei casi.
- **Che cosa serve ad AgentRisk.** (1) Non dà numeri confrontabili con i subtask 1, 2a e 2b: per sapere come va un LLM di frontiera su AgentRisk bisogna provarlo, o aspettare le baseline ufficiali. (2) Il giudizio sul rischio è poco condiviso anche fra persone: se vale anche per AgentRisk, c'è un tetto ai punteggi dovuto al disaccordo fra annotatori, che AgentRisk non pubblica (domanda da aggiungere agli organizzatori). (3) I sei meccanismi coincidono quasi esattamente con i criteri che le linee guida di AgentRisk danno per il livello (probabilità, intensità, portata, vulnerabilità, dipendenza, supervisione, reversibilità): stessa linea di ricerca, stessi autori.

## Bibliografia essenziale

- Andriushchenko, M. et al. (2025). *AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents.* ICLR 2025. <https://arxiv.org/abs/2410.09024>
- Debenedetti, E. et al. (2024). *AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents.* NeurIPS 2024 Datasets and Benchmarks. <https://arxiv.org/abs/2406.13352>
- Inan, H. et al. (2023). *Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations.* <https://arxiv.org/abs/2312.06674>
- Ruan, Y. et al. (2024). *Identifying the Risks of LM Agents with an LM-Emulated Sandbox* (ToolEmu). ICLR 2024. <https://arxiv.org/abs/2309.15817>
- Shang, R., Androna, C.-M., Menis Mastromichalakis, O., et al. (2026). *AURA-Eval: Evaluation Framework for Acting Under Risk Awareness in LLM Agent Trajectories.* Preprint. <https://arxiv.org/abs/2609.06783>
- Slattery, P. et al. (2024). *The AI Risk Repository: A Comprehensive Meta-Review, Database, and Taxonomy of Risks From Artificial Intelligence.* <https://arxiv.org/abs/2408.12622>
- Weidinger, L. et al. (2022). *Taxonomy of Risks posed by Language Models.* FAccT 2022. <https://doi.org/10.1145/3531146.3533088>
- Yuan, T. et al. (2024). *R-Judge: Benchmarking Safety Risk Awareness for LLM Agents.* Findings of EMNLP 2024. <https://arxiv.org/abs/2401.10019>
- Zhan, Q., Liang, Z., Ying, Z., Kang, D. (2024). *InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents.* Findings of ACL 2024. <https://arxiv.org/abs/2403.02691>
- Zhang, Z. et al. (2024). *Agent-SafetyBench: Evaluating the Safety of LLM Agents.* <https://arxiv.org/abs/2412.14470>

## Prossimi passi proposti (nessuno avviato)

1. Baseline lessicale sull'ultimo passo, con validazione per gruppi di scenario.
2. ~~Baseline zero-shot con un LLM e le definizioni del sito; confronto con le baseline costanti.~~ Fatta il 7 novembre 2026 su 100 traiettorie del train: Opus 5.5 rifiuta il 54%, Opus 4.8 ottiene MAE 0,28 e Jaccard 0,86 / 0,76 con errori sistematici ([09](09-baseline-llm.md)).
3. Interventi di riferimento: policy d'esempio applicata alle etichette gold; verifica della propagazione dell'errore.
4. Domande agli organizzatori sul Discord, poi decisione sull'ingresso fra gli impegni (al posto di ComPartMENT).
5. Pilota di tre giornate ([04](04-pilota.md)) se si prosegue.
