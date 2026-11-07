"""Own tests for Assignment 4. Run from repo root:  py -3.13 tests/student/test_student.py
Prints PASS/FAIL per case and a markdown table that can be pasted into ANALYSIS.md."""
import glob, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
src = glob.glob(os.path.join(ROOT, "Python", "**", "algorithms.py"), recursive=True)
sys.path.insert(0, os.path.dirname(src[0]))
import algorithms as A

def subseq(s, t):
    it = iter(t)
    return all(c in it for c in s)

def occ(t, p):
    return [i for i in range(len(t) + 1) if i + len(p) <= len(t) and t.startswith(p, i)]

def check_lcs(req, out, length):
    return out["length"] == length == len(out["sequence"]) and subseq(out["sequence"], req["a"]) and subseq(out["sequence"], req["b"])

def check_merge(req, out, cost):
    sz = req["sizes"]; n = len(sz)
    if out["cost"] != cost: return False
    if n <= 1: return out["plan"] == []
    blocks = {(i, i) for i in range(n)}; total = 0
    if len(out["plan"]) != n - 1: return False
    for l, k, r in out["plan"]:
        if (l, k) not in blocks or (k + 1, r) not in blocks: return False
        blocks -= {(l, k), (k + 1, r)}; blocks.add((l, r)); total += sum(sz[l:r + 1])
    return total == cost and blocks == {(0, n - 1)}

def check_tree(req, out, weight):
    S = set(out["selected"])
    if len(S) != len(out["selected"]) or out["weight"] != weight: return False
    if sum(req["weights"][i] for i in S) != weight: return False
    return all(not (u in S and v in S) for u, v in req["edges"])

def pos(expected):
    return lambda req, out, _=None: out["positions"] == expected

cases = []  # (name, function, request, checker, what it checks)
def add(name, fn, req, chk, why): cases.append((name, fn, req, chk, why))

add("lcs-example", A.lcs, {"a": "tea_time", "b": "team"}, lambda r, o: check_lcs(r, o, 4), "subsequence is not substring")
add("lcs-empty-a", A.lcs, {"a": "", "b": "abc"}, lambda r, o: check_lcs(r, o, 0), "empty input gives length 0")
add("lcs-no-common", A.lcs, {"a": "abc", "b": "xyz"}, lambda r, o: check_lcs(r, o, 0), "zero row/column propagate")
add("lcs-identical", A.lcs, {"a": "hello world", "b": "hello world"}, lambda r, o: check_lcs(r, o, 11), "diagonal-only reconstruction, spaces")
add("lcs-case", A.lcs, {"a": "AbC", "b": "abc"}, lambda r, o: check_lcs(r, o, 1), "case sensitivity")
add("merge-example", A.merge, {"sizes": [2, 3, 4]}, lambda r, o: check_merge(r, o, 14), "optimal order differs from greedy")
add("merge-empty", A.merge, {"sizes": []}, lambda r, o: check_merge(r, o, 0), "n=0")
add("merge-one", A.merge, {"sizes": [7]}, lambda r, o: check_merge(r, o, 0), "n=1 has no merges")
add("merge-adjacent", A.merge, {"sizes": [1, 100, 1, 100]}, lambda r, o: check_merge(r, o, r_cost(r["sizes"])), "adjacency constraint (optimum cross-checked by brute-force DP)")
add("merge-64bit", A.merge, {"sizes": [10**9] * 200}, lambda r, o: o["cost"] > 2**31 and len(o["plan"]) == 199, "totals beyond 32 bits")
add("tree-example", A.tree, {"n": 3, "weights": [4, 9, 6], "edges": [[0, 1], [1, 2]]}, lambda r, o: check_tree(r, o, 10), "take/skip basic")
add("tree-empty", A.tree, {"n": 0, "weights": [], "edges": []}, lambda r, o: o == {"weight": 0, "selected": []}, "n=0")
add("tree-negative", A.tree, {"n": 3, "weights": [-1, -2, -3], "edges": [[0, 1], [1, 2]]}, lambda r, o: check_tree(r, o, 0), "empty set allowed")
add("tree-single", A.tree, {"n": 1, "weights": [5], "edges": []}, lambda r, o: check_tree(r, o, 5), "single vertex")
add("tree-deep-chain", A.tree, {"n": 100000, "weights": [1] * 100000, "edges": [[i, i + 1] for i in range(99999)]}, lambda r, o: check_tree(r, o, 50000), "no recursion failure on deep chain")
add("tree-star", A.tree, {"n": 5, "weights": [10, 3, 3, 3, 3], "edges": [[0, 1], [0, 2], [0, 3], [0, 4]]}, lambda r, o: check_tree(r, o, 12), "leaves beat centre")
for nm, fn in (("naive", A.naive), ("kmp", A.kmp), ("rk", A.rk)):
    add(nm + "-overlap", fn, {"text": "aaaaa", "pattern": "aaa"}, lambda r, o: o["positions"] == [0, 1, 2], "overlapping starts")
    add(nm + "-empty-pattern", fn, {"text": "abc", "pattern": ""}, lambda r, o: o["positions"] == [0, 1, 2, 3], "n+1 boundaries")
    add(nm + "-both-empty", fn, {"text": "", "pattern": ""}, lambda r, o: o["positions"] == [0], "boundary 0 in empty text")
    add(nm + "-long-pattern", fn, {"text": "ab", "pattern": "abc"}, lambda r, o: o["positions"] == [], "pattern longer than text")
    add(nm + "-last-start", fn, {"text": "xxabc", "pattern": "abc"}, lambda r, o: o["positions"] == [2], "last valid start n-m")
    add(nm + "-case-space", fn, {"text": "a A a", "pattern": "A a"}, lambda r, o: o["positions"] == [2], "case and spaces")
add("rk-collision", A.rk, {"text": "abdj", "pattern": "ab"}, lambda r, o: o["positions"] == [0], "dj has the same hash (75) as ab; verification rejects it")
add("rk-all-candidates", A.rk, {"text": "a" * 300, "pattern": "a" * 100}, lambda r, o: o["positions"] == list(range(201)), "every window is an actual match")
add("kmp-fallback", A.kmp, {"text": "abababa", "pattern": "aba"}, lambda r, o: o["positions"] == [0, 2, 4], "fallback after full match")
add("suffix-banana", A.suffix, {"text": "banana"}, lambda r, o: o["sa"] == [5, 3, 1, 0, 4, 2] and o["lcp"] == [0, 1, 3, 0, 0, 2] and o["repeated"] == "ana", "known SA/LCP, overlapping repeat")
add("suffix-empty", A.suffix, {"text": ""}, lambda r, o: o == {"sa": [], "lcp": [], "repeated": ""}, "n=0")
add("suffix-one", A.suffix, {"text": "x"}, lambda r, o: o == {"sa": [0], "lcp": [0], "repeated": ""}, "n=1")
add("suffix-all-same", A.suffix, {"text": "aaaa"}, lambda r, o: o["sa"] == [3, 2, 1, 0] and o["lcp"] == [0, 1, 2, 3] and o["repeated"] == "aaa", "many doubling rounds")
add("suffix-no-repeat", A.suffix, {"text": "abc"}, lambda r, o: o["repeated"] == "" and o["lcp"] == [0, 0, 0], "no repeated substring")
add("aho-example", A.aho, {"patterns": ["he", "she", "he"], "texts": ["sheshe", "sheshe", ""]}, lambda r, o: o["counts"] == [[2, 2, 2], [2, 2, 2], [0, 0, 0]], "suffix patterns, duplicates, reset")
add("aho-empty-dict", A.aho, {"patterns": [], "texts": ["ab", ""]}, lambda r, o: o["counts"] == [[], []], "one empty row per text")
add("aho-no-texts", A.aho, {"patterns": ["a"], "texts": []}, lambda r, o: o["counts"] == [], "empty texts array")
add("aho-overlap", A.aho, {"patterns": ["aa", "a"], "texts": ["aaaa"]}, lambda r, o: o["counts"] == [[3, 4]], "overlapping occurrences")
add("aho-nested", A.aho, {"patterns": ["abc", "bc", "c", "b"], "texts": ["abcabc"]}, lambda r, o: o["counts"] == [[2, 2, 2, 2]], "chain of suffix links")

def r_cost(sz):
    sz = tuple(sz)
    from functools import lru_cache
    @lru_cache(None)
    def f(l, r):
        return 0 if l == r else min(f(l, k) + f(k + 1, r) for k in range(l, r)) + sum(sz[l:r + 1])
    return f(0, len(sz) - 1)

failed = 0
rows = []
for name, fn, req, chk, why in cases:
    try:
        out = fn(req)
        ok = bool(chk(req, out))
    except Exception as e:
        ok, out = False, repr(e)
    failed += not ok
    print(("PASS " if ok else "FAIL ") + name)
    rows.append("|py -3.13 tests/student/test_student.py|%s (inline in script)|checker accepts output|%s|%s|" % (name, "PASS" if ok else "FAIL", why))

# randomized cross-check of the three searches against a reference
import random
random.seed(2026)
bad = 0
for _ in range(2000):
    al = random.choice(["ab", "abc", " aA"])
    t = "".join(random.choice(al) for _ in range(random.randint(0, 30)))
    p = "".join(random.choice(al) for _ in range(random.randint(0, 5)))
    e = occ(t, p)
    req = {"text": t, "pattern": p}
    if not (A.naive(req)["positions"] == A.kmp(req)["positions"] == A.rk(req)["positions"] == e):
        bad += 1
print("random naive/kmp/rk cross-check:", "PASS" if bad == 0 else "FAIL (%d)" % bad)
failed += bad > 0
rows.append("|py -3.13 tests/student/test_student.py|2000 random small texts/patterns (seed 2026)|all three equal reference|%s|cross-check of the three searches|" % ("PASS" if bad == 0 else "FAIL"))

print("\nMarkdown rows for ANALYSIS.md:")
print("\n".join(rows))
sys.exit(1 if failed else 0)
