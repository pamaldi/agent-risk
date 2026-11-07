% Policy d'esempio (le regole note) in ASP. Input attesi, come fatti:
%   level(L).  domain(D).  driver(F).
% Output: intervention(I).  e le regole scattate fires(I, R).
% Vedi docs/03-approccio-asp.md per limiti e idee di estensione (fatti estratti dall'LLM, valore unknown).

fires("Abstain / Block", r1)        :- domain("Privacy / Confidentiality"), level(L), L >= 3.
fires("Request Human Approval", r2) :- domain("Privacy / Confidentiality"), level(L), L <= 2.
fires("Abstain / Block", r3)        :- domain("Security / System Integrity"), driver("Untrusted / Conflicting Instructions").
fires("Abstain / Block", r4)        :- domain("Security / System Integrity"), driver("Authorization / Consent Failure").
fires("Seek Information", r5)       :- domain("Financial / Assets"), driver("Insufficient Grounding / Uncertainty").

rank("Abstain / Block", 5). rank("Propose Alternative", 4). rank("Request Human Approval", 3).
rank("Seek Information", 2). rank("Proceed", 1).

fired(I)        :- fires(I, _).
beaten(R)       :- fired(J), rank(J, S), rank(_, R), S > R.
intervention(I) :- fired(I), rank(I, R), not beaten(R).
intervention("Proceed") :- not fired(_).

#show intervention/1.
#show fires/2.
