"""Benchmark naive / KMP / exact Rabin-Karp on identical inputs.
Run from repo root:  py -3.13 tests/student/bench_search.py
Prints environment info and a markdown table to paste into ANALYSIS.md."""
import glob, os, platform, random, statistics, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
src = glob.glob(os.path.join(ROOT, "Python", "**", "algorithms.py"), recursive=True)
sys.path.insert(0, os.path.dirname(src[0]))
import algorithms as A

ALGS = [("naive", A.naive), ("kmp", A.kmp), ("rk", A.rk)]
SIZES = [(500, 50), (1500, 150), (3000, 300)]   # (n, m), inside the common domain n, m <= 3000
SEED = 2026
RUNS = 3

def gen_random(n, m, rng):
    text = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(n))
    start = rng.randrange(0, n - m + 1)
    return text, text[start:start + m]          # pattern copied from text: at least one match

def gen_repetitive(n, m, rng):
    return "a" * n, "a" * (m - 1) + "b"         # almost matches everywhere, never matches (worst case for naive)

CASES = [("random", gen_random, "random a-z text, pattern = random substring of text"),
         ("repetitive", gen_repetitive, "text a^n, pattern a^(m-1)b")]

print("Python:", sys.version.replace("\n", " "))
print("Platform:", platform.platform(), "|", platform.processor() or platform.machine())
print("Timing scope: one call of the algorithm function on a pre-built dict (no JSON parsing, no process start); time.perf_counter; no warm-up needed (CPython, no JIT) but one untimed call is made first.")
print("Runs per cell:", RUNS, "| seed:", SEED, "\n")
print("|Case|n|m|Seed/generator|Algorithm|Run 1 (ms)|Run 2 (ms)|Run 3 (ms)|Median (ms)|Correct outputs checked|")
print("|---|---:|---:|---|---|---:|---:|---:|---:|---|")

def reference(text, pat):
    return [i for i in range(len(text) - len(pat) + 1) if text[i:i + len(pat)] == pat]

for cname, gen, desc in CASES:
    for n, m in SIZES:
        rng = random.Random(SEED + n)
        text, pat = gen(n, m, rng)
        req = {"text": text, "pattern": pat}
        ref = reference(text, pat)
        outs = {name: fn(req)["positions"] for name, fn in ALGS}       # untimed warm-up call + correctness
        ok = all(o == ref for o in outs.values())
        for name, fn in ALGS:
            times = []
            for _ in range(RUNS):
                t0 = time.perf_counter()
                fn(req)
                times.append((time.perf_counter() - t0) * 1000)
            print("|%s|%d|%d|seed %d, %s|%s|%.3f|%.3f|%.3f|%.3f|%s (%d starts)|" % (
                cname, n, m, SEED + n, desc, name, times[0], times[1], times[2], statistics.median(times),
                "yes, equals reference" if ok else "NO - MISMATCH", len(ref)))
