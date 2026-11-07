# Assignment 4 — analysis

## Environment and commands

- Language/runtime: Python 3.13 (CPython 3.13.7, 64-bit, MSC v.1944).
- OS / CPU / RAM: Windows 11 (10.0.26300) / AMD Ryzen 7 7735HS with Radeon Graphics, 3.20 GHz / 32 GB RAM (4800 MT/s).
- Source: `Python/source/algorithms.py` (launcher `main.py` unchanged). `submission.json` has `"language": "Python"`.
- Build: none (interpreted).
- Setup check: `py -3.13 tools/run.py --setup` → `PASS setup: ping`.
- Public checks: `py -3.13 tools/run.py --check` → all 44 public cases and the repeated mixed batch (state reset) print `PASS`.
- Own tests: `py -3.13 tests/student/test_student.py` → all cases `PASS`.
- Benchmark: `py -3.13 tests/student/bench_search.py`.
- The final commit URL (full 40-character SHA) is recorded in Moodle.

All numbers below are real measurements from the commands above. Complexities are stated after JSON parsing.

## Algorithm explanations

Notation: n, m are sizes, z is the number of reported starts.

### lcs

- **State.** `dp[i][j]` = length of an LCS of the prefixes `a[:i]` and `b[:j]`; `i` counts characters taken from `a`, `j` from `b`.
- **Transition / base.** `dp[i][j] = dp[i-1][j-1] + 1` if `a[i-1] == b[j-1]`, otherwise `max(dp[i-1][j], dp[i][j-1])`. Base: `dp[0][*] = dp[*][0] = 0`.
- **Order.** Rows increase with i and columns with j, so the three cells used (diagonal, up, left) are already computed.
- **Correctness.** If the last characters match, some optimal LCS can use them (exchange argument), so the answer is the diagonal value plus 1. If they differ, at most one of them is the last character of the LCS, so dropping one of them loses nothing and the best of the two options is optimal.
- **Reconstruction.** Start at `(n, m)`. On a match, emit the character and move diagonally; otherwise move to the neighbour with the larger value (ties: move up). The emitted characters are reversed. Any tie choice yields an optimal sequence.
- **Cost.** O(nm) time and O(nm) memory (table of (n+1)(m+1) integers); output O(min(n, m)). Empty inputs return length 0 and "" without a table.
- **Boundary test.** `a="tea_time", b="team"` → length 4, "team": detects confusing subsequence with substring.

### merge

- **State.** `cost[l][r]` = minimum total cost to merge the original blocks `l..r` into one block.
- **Transition / base.** `cost[l][r] = min over k in [l, r-1] of cost[l][k] + cost[k+1][r] + sum(sizes[l..r])`; the sum comes from prefix sums in O(1). Base: `cost[i][i] = 0`. `split[l][r]` stores the best k (the last merge).
- **Order.** Intervals by increasing length, so both sub-intervals are ready.
- **Correctness.** The final merge of any plan joins two adjacent blocks `[l,k]` and `[k+1,r]`, each built independently, so the problem has optimal substructure; trying all k covers every plan, and adjacency is built in.
- **Reconstruction.** An explicit stack performs a post-order walk from `(0, n-1)`: the children `(l,k)` and `(k+1,r)` are emitted first, then `[l,k,r]`. Hence the plan is chronological and has n-1 merges. Ties take the first minimal k.
- **Cost.** O(n^3) time, O(n^2) auxiliary memory; n ≤ 200. Python integers avoid overflow (sums up to 2·10^11).
- **Boundary test.** `sizes=[]` and `[7]` → cost 0, plan `[]`; `[2,3,4]` → 14 (merging blocks 0 and 1 first costs 5+9; merging blocks 1 and 2 first costs 7+9=16).

### tree

- **State.** For vertex v: `take[v]` = best total weight in the subtree of v when v is selected; `skip[v]` = best when v is not selected.
- **Transition / base.** `take[v] = w[v] + sum skip[c]`, `skip[v] = sum max(take[c], skip[c])` over children c. A leaf has `take = w`, `skip = 0`. The answer is `max(take[root], skip[root])`.
- **Order.** BFS from vertex 0 gives a vertex order in which every parent precedes its children; processing it in reverse is a post-order where children are finished before the parent. No recursion is used, so a chain of 100000 vertices is safe.
- **Correctness.** Subtrees of different children are independent once the state of v is fixed; selecting v forbids all its children, skipping v leaves them free. Since the empty set is allowed, `skip` of a leaf is 0 and an all-negative tree gives 0.
- **Reconstruction.** Top-down in BFS order: the root is selected if `take > skip`; a child is selected only if its parent is not selected and `take[c] > skip[c]`. The selected vertices are listed once each.
- **Cost.** O(n) time and memory (adjacency lists, parent and DP arrays); n=0 returns immediately.
- **Boundary test.** All-negative weights `[-1,-2,-3]` → weight 0, selected `[]`; detects forcing at least one vertex.

### naive

- **Invariant.** For start i, the inner loop has verified `text[i..i+j-1] == pattern[0..j-1]`; a full match is j = m.
- **Cases.** Empty pattern → starts `0..n` (n+1 boundaries). `m > n` → `[]`. Otherwise i runs over `0..n-m`, so the last valid start n-m is included and overlaps are kept because i always advances by one.
- **Correctness.** Every start is tested independently by direct comparison.
- **Cost.** O(nm) time worst case (e.g. `a^n` against `a^(m-1)b`), O(1) auxiliary memory, O(z) output.
- **Boundary test.** `text="aaaaa", pattern="aaa"` → `[0,1,2]`; detects skipping overlaps.

### kmp

- **Definition.** `pi[i]` = length of the longest proper prefix of `pattern[:i+1]` that is also its suffix.
- **Building pi.** Keep k = pi of the previous position; while `pattern[k]` differs from the new character, fall back `k = pi[k-1]`; on equality k += 1. Base `pi[0] = 0`.
- **Search.** The same fallback is used on the text: k is the length of the pattern prefix matched ending at the current text position. On a mismatch fall back; on a match advance. When k = m a start `i-m+1` is reported and `k = pi[m-1]` (fallback after a full match), so overlapping matches are still found.
- **Correctness.** `pi` lists exactly the borders of the matched prefix; falling back to the longest border never skips a possible alignment.
- **Cost.** O(n+m+z) time (each step increases k by at most 1, and falls back decrease it, so total fallbacks ≤ n+m); O(m) auxiliary memory; output O(z). Empty pattern returns `0..n` before any indexing.
- **Boundary test.** `"abababa"`, `"aba"` → `[0,2,4]`; detects forgetting the fallback after a full match.

### rk

- **Hash.** Polynomial rolling hash with base 31 and modulus 101 on ASCII codes; the leftmost character has the highest power: `h = sum text[i+j]·31^(m-1-j) mod 101`.
- **Rolling update.** `h' = ((h - code(text[i])·31^(m-1)) · 31 + code(text[i+m])) mod 101`. Python's `%` always returns a non-negative value, so negative remainders are normalised.
- **Verification.** Equal hashes are only candidates: the characters of the window are compared with the pattern (`text[i:i+m] == pattern`, a direct character comparison, not a search function) before a start is reported.
- **Cases.** Empty pattern → `0..n`; `m > n` → `[]`, both handled before any window is built.
- **Cost.** For 1 ≤ m ≤ n: O(n + m + c·m) time where c is the number of equal-hash candidate windows; this is candidate-sensitive and can reach O(nm) (with modulus 101 many windows collide, and for `a^n` vs `a^m` every window is a real match). Linear worst-case time is not claimed. Auxiliary memory O(1) beyond output.
- **Boundary test.** `text="abdj", pattern="ab"`: `dj` also hashes to 75, so the hash alone would report a false start 2; verification rejects it → `[0]`.

### suffix

- **Prefix doubling.** `rank[i]` is the rank of the first k characters of suffix i (initially the character code). In each round suffixes are sorted by the pair `(rank[i], rank[i+k])`, where a missing second part counts as smaller than any character; equal pairs get equal new ranks; then k is doubled. The loop stops when all ranks are distinct (at most about log2 n rounds), and the sort order is then the suffix array. Pairs are packed into one integer key. Comparison sorting gives O(n log^2 n) time, O(n) memory.
- **Kasai.** `lcp[i]` is the longest common prefix of `sa[i-1]` and `sa[i]`. Processing suffixes in text order i = 0..n-1 and keeping h, the previous LCP, we start the next comparison with `h-1`: if suffix i shares h characters with its predecessor in sorted order, suffix i+1 shares at least h-1 with its own predecessor. Thus h increases at most 2n times in total and the loop is O(n). `lcp[0] = 0`.
- **Repeated substring.** A substring occurring twice is a common prefix of two suffixes; the longest such common prefix is attained by suffixes adjacent in sorted order, so the answer has length `max(lcp)` and starts at `sa[i]` for the maximizing i. Overlaps are allowed (`banana` → `ana`). No repeat → `""`.
- **Cases.** Empty text → `sa=[]`, `lcp=[]`, `repeated=""`. No sentinel and no empty suffix.
- **Boundary test.** `"aaaa"` → `sa=[3,2,1,0]`, `lcp=[0,1,2,3]`; detects wrong handling of equal ranks and the missing-second-part rule.

### aho

- **Automaton.** One trie per request (dictionary of child maps); each pattern ends in a terminal state and `term_of[idx]` stores it, so duplicate patterns share one state and get equal counts.
- **Failure links.** Computed by BFS: for state v reached from u by character c, follow failure links of u until a state with a child c is found; that child is `fail[v]` (root if none). The BFS order guarantees that `fail[v]` (shallower) is ready.
- **Suffix patterns.** For every state `tl[v]` is the nearest terminal state on its failure chain, v included, and `out_link[v]` is the same for the proper chain. Reading a text, each position adds 1 to the visit counter of `tl[state]` only. After the text, counters are propagated along `out_link` from deeper terminal states to shallower ones, so a pattern like `he` receives the visits of `she`. This is the "reverse failure propagation" and avoids listing every individual match.
- **Independent texts.** The state starts at the root for each text and the counters are reset after each text (only the terminal states are touched), so no counts leak between texts. A row has one entry per dictionary position (original order); empty dictionary → an empty row per text, no texts → `[]`.
- **Cost.** Construction O(L + S) with maps (L total pattern length, S trie states); per text O(|text| + T + p) with T ≤ p terminal states (amortized matching with fallbacks), auxiliary memory O(S + p); output O(q·p).
- **Boundary test.** patterns `["he","she","he"]`, text `"sheshe"` → `[2,2,2]`: detects missing suffix-pattern counts or duplicates.

## Own tests

The script `tests/student/test_student.py` runs about 48 checks; each output is validated by a checker (subsequence and optimal length for LCS, adjacency/plan replay for merge, independence and weight for tree, reference occurrences for the searches). Representative rows:

|Command|Input or fixture path|Expected result|Actual result / log|What it checks|
|---|---|---|---|---|
|`py -3.13 tests/student/test_student.py`|lcs-example, lcs-empty-a, lcs-no-common, lcs-identical, lcs-case|valid LCS of the optimal length|PASS|subsequence vs substring, empty input, case sensitivity|
|same|merge-example, merge-empty, merge-one, merge-adjacent, merge-64bit|optimal cost, valid chronological plan|PASS|adjacency, n≤1, totals beyond 32 bits|
|same|tree-example, tree-empty, tree-negative, tree-single, tree-star|optimal weight, independent set|PASS|empty set allowed, n=0, star|
|same|tree-deep-chain (n=100000 chain)|weight 50000|PASS|no recursion failure on deep chains|
|same|naive/kmp/rk: overlap, empty-pattern, both-empty, long-pattern, last-start, case-space|equal to reference starts|PASS|overlaps, n+1 boundaries, m>n, last start n-m, case and spaces|
|same|rk-collision (`abdj`/`ab`)|`[0]`|PASS|equal hash (75) rejected by verification|
|same|rk-all-candidates (`a^300`, `a^100`)|`[0..200]`|PASS|every window is a candidate and a true match|
|same|kmp-fallback (`abababa`/`aba`)|`[0,2,4]`|PASS|fallback after a full match|
|same|suffix-banana, suffix-empty, suffix-one, suffix-all-same, suffix-no-repeat|exact sa/lcp/repeated|PASS|known array, n=0, n=1, many doubling rounds, no repeat|
|same|aho-example, aho-empty-dict, aho-no-texts, aho-overlap, aho-nested|exact counts|PASS|suffix patterns, duplicates, reset, empty cases, chained failure links|
|same|2000 random small texts/patterns (seed 2026)|naive = kmp = rk = reference|PASS|cross-check of the three searches|
|`py -3.13 tools/run.py --check`|44 public cases + repeated mixed batch|all PASS|all PASS|official public checks and state reset|

## Search comparison

Same inputs for naive, KMP and RK. Common domain: n, m ≤ 3000. Sizes (n, m) = (500, 50), (1500, 150), (3000, 300). Cases measured separately:

- **random:** text of n random lowercase letters (`random.Random(2026+n)`), pattern is a random substring of the text (at least one true match);
- **repetitive:** text `a^n`, pattern `a^(m-1)b` (near-matches at every start, no true match; the worst case for naive).

Correctness was verified first: for every case the three outputs were compared with a reference built from slice comparison (column "Correct outputs checked"). Timing scope: one call of the algorithm function on an already parsed dict, `time.perf_counter`, 3 measured runs per algorithm/size/case after one untimed call (CPython has no JIT, so no further warm-up); no JSON parsing, no process start, no compilation. Command: `py -3.13 tests/student/bench_search.py`. Times are in milliseconds.

|Case|n|m|Seed/generator|Algorithm|Run 1 (ms)|Run 2 (ms)|Run 3 (ms)|Median (ms)|Correct outputs checked|
|---|---:|---:|---|---|---:|---:|---:|---:|---|
|random|500|50|seed 2526, random a-z text, pattern = random substring of text|naive|0.052|0.067|0.226|0.067|yes, equals reference (1 starts)|
|random|500|50|seed 2526, random a-z text, pattern = random substring of text|kmp|0.044|0.035|0.034|0.035|yes, equals reference (1 starts)|
|random|500|50|seed 2526, random a-z text, pattern = random substring of text|rk|0.114|0.108|0.106|0.108|yes, equals reference (1 starts)|
|random|1500|150|seed 3526, random a-z text, pattern = random substring of text|naive|0.105|0.104|0.102|0.104|yes, equals reference (1 starts)|
|random|1500|150|seed 3526, random a-z text, pattern = random substring of text|kmp|0.110|0.103|0.102|0.103|yes, equals reference (1 starts)|
|random|1500|150|seed 3526, random a-z text, pattern = random substring of text|rk|0.225|0.222|0.221|0.222|yes, equals reference (1 starts)|
|random|3000|300|seed 5026, random a-z text, pattern = random substring of text|naive|0.273|0.305|0.305|0.305|yes, equals reference (1 starts)|
|random|3000|300|seed 5026, random a-z text, pattern = random substring of text|kmp|0.314|0.228|0.208|0.228|yes, equals reference (1 starts)|
|random|3000|300|seed 5026, random a-z text, pattern = random substring of text|rk|0.454|0.449|0.446|0.449|yes, equals reference (1 starts)|
|repetitive|500|50|seed 2526, text a^n, pattern a^(m-1)b|naive|1.280|1.438|1.162|1.280|yes, equals reference (0 starts)|
|repetitive|500|50|seed 2526, text a^n, pattern a^(m-1)b|kmp|0.071|0.068|0.067|0.068|yes, equals reference (0 starts)|
|repetitive|500|50|seed 2526, text a^n, pattern a^(m-1)b|rk|0.073|0.071|0.070|0.071|yes, equals reference (0 starts)|
|repetitive|1500|150|seed 3526, text a^n, pattern a^(m-1)b|naive|10.912|10.902|10.880|10.902|yes, equals reference (0 starts)|
|repetitive|1500|150|seed 3526, text a^n, pattern a^(m-1)b|kmp|0.319|0.311|0.312|0.312|yes, equals reference (0 starts)|
|repetitive|1500|150|seed 3526, text a^n, pattern a^(m-1)b|rk|0.337|0.310|0.216|0.310|yes, equals reference (0 starts)|
|repetitive|3000|300|seed 5026, text a^n, pattern a^(m-1)b|naive|43.952|43.495|43.292|43.495|yes, equals reference (0 starts)|
|repetitive|3000|300|seed 5026, text a^n, pattern a^(m-1)b|kmp|0.661|0.630|0.588|0.630|yes, equals reference (0 starts)|
|repetitive|3000|300|seed 5026, text a^n, pattern a^(m-1)b|rk|0.417|0.417|0.559|0.417|yes, equals reference (0 starts)|

Observations:

- On random text all three algorithms are close (median 0.305 ms naive, 0.228 ms KMP at n=3000), because a mismatch usually appears at the first compared character, so naive is near linear. RK is about twice as slow (0.449 ms), since it updates the hash for every window.
- On the repetitive case naive grows roughly with n·m: medians 1.280, 10.902 and 43.495 ms for n·m = 25 000, 225 000 and 900 000 (about 8.5× and 4× when n·m grows 9× and 4×). KMP (0.068, 0.312, 0.630 ms) and RK (0.071, 0.310, 0.417 ms) grow roughly with n+m instead, and at n=3000 are about 70–100× faster than naive.
- These measurements are small, from one machine, and are not a proof of asymptotic complexity; they only illustrate the difference between the bounds O(nm), O(n+m) and the candidate-sensitive O(n+m+c·m).
- With the deliberately small modulus 101, RK has many false candidates in general (about 1 in 101 windows on random text), each costing an O(m) verification, and on `a^n` every window is a candidate. This is specific to modulus 101 and does not describe production hashes with a large modulus. The known collision `ab`/`dj` is included as the correctness test `rk-collision`.

## Sources and AI assistance

- Course materials of Design and Analysis of Algorithms (weeks 8–10), the assignment specification and `docs/guide/CONTRACTS.md`.
- AI Assistance: AI helped write the implementation in
  algorithms.py, the scripts tests/student/test_student.py and bench_search.py,
  and a first draft of this file, based on the assignment contracts. I ran the
  44 public checks (all PASS), my own tests and the benchmark on my machine; the
  numbers above come from those runs.