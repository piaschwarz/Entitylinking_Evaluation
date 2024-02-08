## Evaluation of Entity Linker OpenTapioca, Spacyfishing, and DBpedia Spotlight

### Comparison results on HIPE-data-v1.4-test-de

| Model | F1 | P | R | TP | FP | FN |
|---|---|---|---|---|---|---|
| Spacyfishing | 0.28 | 0.351 | 0.233 | 234 | 432 | 772 |
| DBpedia Spotlight | 0.29 | 0.192 | 0.557 | 675 | 2837 | 536 |
| OpenTapioca | 0.421 | 0.407 | 0.437 | 497 | 724 | 641 |
| HIPE Task 2022 team2[^1] | 0.464 | 0.462 | 0.466 | 535 | 623 | 612 |

- Evaluated using the "fuzzy regime" as in HIPE 2022: counted as TP if token boundaries do not match exactly but entity type (Q-item) is the same
- DBpedia Spotlight Q-item retrieved through DBpedia-Wikidata interlinking, in 33 cases a DBpedia entity was found but no corresponding Q-item was interlinked, e.g.:

`Laffaux	B-loc	O	B-loc.adm.town	O	O	O	Q842559	_	LED0.00	WIKIDATA-Q-ITEM-NOT-FOUND-FOR:http://de.dbpedia.org/resource/Laffaux`

[^1]: Best scores on the Task End-to-end EL hipe2020 German relaxed @1 (literal sense) from Team "L3i" from La Rochelle University, La Rochelle, France, https://hipe-eval.github.io/HIPE-2022/results#hipe-2022-track-evaluation-results)
