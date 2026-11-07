# 03 — Approccio con ASP (proposta del 6 novembre 2026)

**Natura:** proposta di metodo, nata dalla discussione sull'utilità di approfondire ASP (Answer Set Programming) accanto a LLM e agenti. **Nessun esperimento eseguito.**

## Idea

L'LLM legge la traiettoria e produce **fatti**, ciascuno con il passo che lo sostiene. Un programma ASP, eseguito con clingo, ricava fattori di rischio e intervento e impone i vincoli fra le etichette. È lo schema neuro-simbolico già usato in un lavoro precedente di estrazione con LLM e validazione simbolica deterministica, applicato a un task in cui il componente simbolico decide l'esito ufficiale del subtask 3.

## Dove ASP è adatto

1. **Subtask 3.** La policy d'esempio ha già la forma di un programma logico: regole da dominio, livello e fattore a un intervento, un ordine di priorità e Proceed come default quando nessuna regola scatta (negazione per fallimento). Le 2–3 policy di gara si scrivono come regole senza toccare il resto della pipeline.
   - Sulla sola policy d'esempio basterebbe una funzione Python (`src/agent_risk/policy.py`): ASP rende davvero se le policy di gara useranno autorizzazione, reversibilità o informazione disponibile.
   - L'answer set dice **quale regola è scattata**: il feedback all'agente si genera da lì, e il giudice LLM valuta proprio la coerenza fra feedback, intervento e policy.
   - L'ambiguità dei due domini con un solo livello si può codificare in entrambe le letture e confrontare sul dev.
2. **Subtask 2b**, soprattutto Authorization / Consent Failure e Untrusted / Conflicting Instructions, che insieme coprono 323 etichette del train. L'LLM estrae fatti come provenienza dell'istruzione di agire, scope richiesto dall'utente, autorizzazione presente, tipo di risorsa; le regole ricavano il fattore.
3. **Vincoli fra le etichette**: No Material Harm e No Material Risk sempre insieme, sempre da sole e con livello 1; al massimo due etichette per insieme. Con un punteggio dell'LLM per ogni etichetta, i vincoli deboli (`#minimize`) scelgono la combinazione coerente di punteggio massimo: l'analogo della decodifica vincolata già usata su DiCo-NLI.

## Dove non è adatto

- **Subtask 1, livello di rischio.** È un giudizio graduato su probabilità, gravità, portata, reversibilità: resta all'LLM (o a un modello supervisionato). Le regole possono al più fissare limiti inferiori, da verificare sul train.
- **L'estrazione dei fatti è il collo di bottiglia.** Una deduzione corretta da fatti sbagliati dà un risultato sbagliato.
- **Trappola dell'assunzione di mondo chiuso.** In ASP «nessuna autorizzazione nella traccia» diventa vero anche quando l'estrattore non ha visto un'autorizzazione che c'era. Serve un valore esplicito `unknown`: se una premessa è `unknown` il programma si astiene e decide l'LLM.

## Schizzo dell'encoding (illustrativo, non testato)

```prolog
% Fatti estratti dall'LLM, con il passo che li sostiene
% instruction_source(retrieved, 10).  exceeds_user_scope(18).  discloses_file(18).
% authorization(no) | authorization(yes) | authorization(unknown)

driver(authorization_consent_failure) :-
    discloses_file(A), instruction_source(retrieved, _),
    exceeds_user_scope(A), authorization(no).
abstain(driver) :- authorization(unknown).
```

La parte della policy è già implementata e **testata** in `src/agent_risk/asp/policy_example.lp` (cinque regole, ordine di priorità, default Proceed), con `src/agent_risk/asp/runner.py` e un test che ne verifica l'equivalenza con la versione Python. La parte di estrazione dei fatti (sopra) resta uno schizzo.

## Esperimento

Quello del [pilota](04-pilota.md), con le regole in clingo:

- **A** — LLM diretto sulla traiettoria;
- **B** — LLM sui fatti estratti;
- **C** — regole ASP sugli stessi fatti, con astensione.

Il confronto decisivo è **C contro B**: correzioni, nuovi errori, astensioni, copertura, con soglie fissate prima della valutazione. Si aggiunge un confronto sul subtask 3: intervento calcolato dalla policy sulle etichette predette, contro intervento predetto direttamente (ipotesi H2 in [06](06-decisioni-e-domande-aperte.md)), con interventi di riferimento ottenuti applicando la policy alle etichette gold.

## Vincoli di calendario e riuso

CodaBench apre nella seconda metà di novembre; la valutazione va dal 10 al 31 gennaio 2027. Nel piano generale DiCo-NLI resta l'impegno principale: AgentRisk entrerebbe al posto di ComPartMENT, non in aggiunta.

La stessa architettura coincide con il progetto proposto per il corso *Cognitive Semantics for Artificial Intelligence* (Gangemi, UniBO). Che un lavoro su shared task valga come progetto d'esame va concordato con il docente. Il 6 novembre 2026 Gangemi ha scritto per e-mail che ASP potrebbe servire in uno dei sistemi del suo gruppo e che se ne potrebbe discutere: un prototipo AgentRisk funzionante è un caso concreto da portare in quella discussione.

## Perché ASP ora

Con LLM e agenti che dominano la formazione, ASP è una competenza rara e complementare: dove la policy cambia (come qui, con 2–3 policy annunciate a gennaio) le regole si riscrivono senza riaddestrare nulla, e il programma spiega perché ha deciso. Il valore dipende però dal fatto che la policy di gara sia davvero formale; se fosse vaga, il vantaggio si ridurrebbe.
