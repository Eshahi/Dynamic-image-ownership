# Searched verification: the null belongs to the full algorithm

Author mathematical addendum, Codex agent, 2026-10-25. **Outside the completed WP6/E3 independent reviews.** This note interprets claims; it neither amends the frozen protocol nor requests another experiment. No computation, experiment or download was performed. The authoritative main-checkout STATE was read once.

## 1. Fixed comparisons and searched acceptance

Let X follow a declared negative-source distribution P0. Hold the deployed detector, key, threshold and other fixed state explicit. A comparison j includes an alignment, candidate message/record/owner, key if searched, and any random seed. Let E_j be its acceptance event and p_j=P0(E_j). A verifier accepting if any of M comparisons accepts has

`p_search = P0(union_j E_j) <= min(1, sum_j p_j)`.

This union bound needs **no independence**. The probabilities must refer to the same relevant null population and valid comparison rules. If each p_j<=p, then p_search<=min(1,Mp). Searching G alignments, R records and K keys can supply an upper-bound count M=GRK when all combinations are possible. Correlated or duplicate trials do not invalidate the bound; they may make it loose. An unquantified continuous search has no justified finite M merely because the final output contains one alignment.

For mutually independent events, the exact expression is `1-product_j(1-p_j)`; for equal p it is `1-(1-p)^M`. The corresponding equal-test Sidak allocation `p<=1-(1-alpha)^(1/M)` uses independence here. Bonferroni's `p_j<=alpha/M` does not. Geometry variants of one image and messages compared against one decoded vector generally do not provide independent events. This note assumes no special dependence theorem that would justify a Sidak calculation otherwise.

Some verifiers first select one alignment by an internal confidence score and then test its message. That event need not equal the union, but is contained in the union over all candidates the selector could return, provided each candidate's acceptance rule is represented. Its exact null includes selection. A fair-bit model before confidence selection is not automatically the selected message's distribution. Conversely, selection does not necessarily increase acceptance: this is an accounting requirement, not a claim that every search is harmful.

**Exact example 1: searching messages.** Suppose a negative image decodes to a uniformly random two-bit vector, and acceptance requires exact agreement with a candidate. A fixed candidate has p=1/4. Searching all four candidates accepts every vector: p_search=1. The union bound gives 4/4=1 exactly. Treating the four events as independent would give `1-(3/4)^4=175/256`, which is wrong because these events are disjoint. This example concerns unconstrained candidate enumeration, not legitimate enrollment or a forgery of a predetermined owner.

## 2. Adaptivity, repeated queries and the key distribution

A predetermined finite collection of candidate rules can still be union-bounded when the final candidate is selected after viewing their scores. By contrast, a p-value or null tail for each **fixed** candidate does not automatically bound a newly constructed candidate chosen as a function of the same image or earlier feedback. Example 1 can equivalently be implemented by selecting the decoded vector as the candidate and running one final comparison; counting only that final comparison hides selection.

For an adaptive sequence, a sufficient alternative is a conditional guarantee: at each attempted query t, after its query has been chosen, `P0(E_t | available history, chosen query)<=alpha_t`. Then, for a bounded horizon T, the tower property and union bound give `P0(any acceptance)<=E[sum_(t<=T) alpha_t]`. A fixed error budget with sum alpha_t<=alpha also supports stopping early. A marginal tail under independent ordinary-image sampling does not establish this conditional guarantee for detector-guided images or keys. Repeating an identical deterministic request changes no event; fresh randomness or changed queries can change the event. Unlimited queries cannot inherit a fixed-query guarantee without further assumptions or an appropriate sequential argument.

Distinguish `P_(K,X)(accept)` for a randomly sampled key K from `P_X(accept | K=k)` for the deployed key. A small average over keys does not establish the same bound for every key. For illustration, average risk epsilon only implies that the fraction of keys having risk greater than c is at most epsilon/c, by Markov's inequality. This statement requires the same key and source distributions used to define the average. It says nothing about an attacker choosing a key, a source distribution depending on the key, or searching many keys. Independent negative-source sampling with one frozen key can support a **key-conditional** population statement; it does not certify all keys.

## 3. A fair marginal bit is not an iid bit string

For L iid Bernoulli(1/2) match indicators, the fixed-message score S has

`P0(S>=h) = 2^(-L) * sum_(k=h)^L binom(L,k)`.

The inclusive/strict threshold must match implementation. Fair marginal bits alone do not establish this binomial law. Correlations, unequal biases, structured content-derived words, repeated code bits, learned decoder behavior and selection can change its tail. Effective message length cannot be inferred from the number of carrier chips. Passing average bit-balance checks also would not prove the needed joint law.

**Exact example 2: correlated fair bits.** Let every decoded bit equal the same fair random bit B, and fix the candidate to the all-zero word of length L. Each match indicator is marginally fair, but S is L with probability 1/2 and zero with probability 1/2. Exact-match acceptance is therefore 1/2, whereas the iid calculation gives 2^(-L). This is a counterexample to the inference from marginal fairness, not a diagnosis of any named implementation.

Randomizing the candidate independently and uniformly across all L-bit strings can make its match indicators iid conditional on a fixed decoded vector. That is a different experiment from a fixed deployed candidate, a structured owner code, or a candidate selected using the decoded vector. State which randomness supports the null.

## 4. Finite negative evidence and source clusters

Let Z_i indicate **any** acceptance across the prespecified negative calls for source group i. Under independent identically distributed source groups, a frozen algorithm and complete observation, n zero-event groups give the exact one-sided confidence upper bound

`u = 1 - alpha^(1/n)`

for their source-any acceptance probability. Dependence within each source is unrestricted. Independence/exchangeability of individual calls must not be inferred from repeated seeds, candidate queries or transformations of the same source; exchangeability of source groups alone also does not imply the independent binomial model. Related images may require a broader grouping unit. Fixed-corpus evidence remains evidence about that corpus unless a population-sampling interpretation is justified.

At n=200 and alpha=.05, u=.014867. For eight simultaneous source-any bounds, Bonferroni uses alpha=.05/8 and gives u=.025057 without independence between strata. These are the values and eight strata already specified in [the final protocol, section 6](../07-final-experiment.md). They do not become smaller by relabeling thousands of within-source calls as independent negatives. A particular included call's acceptance probability is bounded by the source-any probability under the same population, but the source-any estimand is not an estimated universal per-query rate. Future added alignments, messages or queries lie outside the frozen bundle. Unresolved calls prevent the zero-complete-event certificate; the protocol already makes them a gate failure.

Likewise, zero events in 50,000 genuinely independent trials would give about 5.99e-5 at 95% confidence, not an empirical certificate of 1e-6. This arithmetic neither invalidates a separately justified theoretical null nor verifies its assumptions.

## 5. Accidental acceptance and malicious forgery

Ordinary-image FPR integrates over a specified non-adversarial negative distribution. Malicious forgery instead involves an attacker, information/access rules, a query/computation budget and a success event: for example, acceptance under a predetermined victim's identity on unauthorized content. Choosing a matching label, copying a watermark, estimating a residual, and falsifying a signed enrollment record are different success events. A small ordinary-image FPR does not by itself bound adaptive forgery; a high attack success rate does not directly estimate ordinary-image FPR. Message recovery, presence, content binding, attribution and lawful ownership must remain distinct. None of the arguments above is a universal impossibility or security result.

## 6. Literature connection and reusable wording

The existing [GROW access-closure card](../literature/grow-access-closure.md) records geometry search in the inspected submission supplement; its accepted-version coverage remains partial. It does not supply a calibrated search-null distribution. **No actual GROW search FPR is inferred here.** The [TraceMark card](../literature/tracemark-2026-primary.md) records an assumed iid fair-bit tail, and the [residual-transferability card](../literature/residual-transferability-2026-primary.md) separates model-based tails, negative counts and attack success. These are links to the previously inspected primary-source receipts, not claims of fresh primary-paper inspection by this author. The mathematical arguments above are local derivations; no source is summarized at length.

Reusable caveat: “The reported analytical tail applies to the stated fixed comparison under its assumed null. Verification with alignment, candidate or key selection is a different algorithm whose null includes that selection. Empirical specificity is reported at the prespecified independent source-group unit, with repeated calls collapsed and missing calls disclosed. These statements concern accidental acceptance under the declared negative population and do not establish adaptive unforgeability.”
