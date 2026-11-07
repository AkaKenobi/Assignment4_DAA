"""Implement algorithm bodies. See docs/guide/CONTRACTS.md; inputs and outputs are dictionaries."""

def lcs(request):
    """Compare two versions of a sequence while preserving the order of shared characters."""
    a = request["a"]
    b = request["b"]
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return {"length": 0, "sequence": ""}

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        row = dp[i]
        prev = dp[i - 1]
        ai = a[i - 1]
        for j in range(1, m + 1):
            if ai == b[j - 1]:
                row[j] = prev[j - 1] + 1
            else:
                up = prev[j]
                left = row[j - 1]
                row[j] = up if up >= left else left

    out = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    out.reverse()
    return {"length": dp[n][m], "sequence": "".join(out)}

 #Part 2:interval DP
def merge(request):
    """Plan the cheapest sequence of adjacent block merges when the original order must be preserved."""
    sizes = request["sizes"]
    n = len(sizes)
    if n <= 1:
        return {"cost": 0, "plan": []}

    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + sizes[i]

    INF = float("inf")
    cost = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for l in range(0, n - length + 1):
            r = l + length - 1
            best = None
            best_k = l
            cl = cost[l]
            for k in range(l, r):
                c = cl[k] + cost[k + 1][r]
                if best is None or c < best:
                    best = c
                    best_k = k
            cost[l][r] = best + pre[r + 1] - pre[l]
            split[l][r] = best_k

    plan = []
    stack = [(0, n - 1, False)]
    while stack:
        l, r, done = stack.pop()
        if l == r:
            continue
        k = split[l][r]
        if done:
            plan.append([l, k, r])
        else:
            stack.append((l, r, True))
            stack.append((k + 1, r, False))
            stack.append((l, k, False))
    return {"cost": cost[0][n - 1], "plan": plan}


#Part 3:tree DP
def tree(request):
    """Choose a maximum-value set when neighbouring vertices are incompatible and conflicts form a tree."""
    n = request["n"]
    if n == 0:
        return {"weight": 0, "selected": []}
    w = request["weights"]
    adj = [[] for _ in range(n)]
    for u, v in request["edges"]:
        adj[u].append(v)
        adj[v].append(u)

    parent = [-1] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    for v in order:
        for c in adj[v]:
            if not seen[c]:
                seen[c] = True
                parent[c] = v
                order.append(c)

    take = [0] * n
    skip = [0] * n
    for v in range(n):
        take[v] = w[v]
    for v in reversed(order):
        p = parent[v]
        if p >= 0:
            take[p] += skip[v]
            skip[p] += take[v] if take[v] > skip[v] else skip[v]

    chosen = [False] * n
    selected = []
    for v in order:
        p = parent[v]
        if p < 0:
            chosen[v] = take[v] > skip[v]
        else:
            chosen[v] = (not chosen[p]) and take[v] > skip[v]
        if chosen[v]:
            selected.append(v)
    best = take[0] if take[0] > skip[0] else skip[0]
    return {"weight": best, "selected": selected}


#Part 4:search
def naive(request):
    """Establish a simple exact-search baseline against which the other two searches can be checked."""
    text = request["text"]
    pat = request["pattern"]
    n, m = len(text), len(pat)
    if m == 0:
        return {"positions": list(range(n + 1))}
    res = []
    for i in range(n - m + 1):
        j = 0
        while j < m and text[i + j] == pat[j]:
            j += 1
        if j == m:
            res.append(i)
    return {"positions": res}


def kmp(request):
    """Reuse information about matched prefixes to avoid restarting the search after every mismatch."""
    text = request["text"]
    pat = request["pattern"]
    n, m = len(text), len(pat)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}

    pi = [0] * m
    k = 0
    for i in range(1, m):
        c = pat[i]
        while k > 0 and pat[k] != c:
            k = pi[k - 1]
        if pat[k] == c:
            k += 1
        pi[i] = k

    res = []
    k = 0
    for i in range(n):
        c = text[i]
        while k > 0 and pat[k] != c:
            k = pi[k - 1]
        if pat[k] == c:
            k += 1
        if k == m:
            res.append(i - m + 1)
            k = pi[k - 1] 
    return {"positions": res}


def rk(request):
    """Reject windows with unequal fingerprints and verify every equal-hash candidate."""
    text = request["text"]
    pat = request["pattern"]
    n, m = len(text), len(pat)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}

    B, MOD = 31, 101
    high = 1  
    for _ in range(m - 1):
        high = (high * B) % MOD

    hp = 0
    hw = 0
    for i in range(m):
        hp = (hp * B + ord(pat[i])) % MOD
        hw = (hw * B + ord(text[i])) % MOD

    res = []
    for i in range(n - m + 1):
        if hw == hp and text[i:i + m] == pat:  # candidate verified char by char
            res.append(i)
        if i + m < n:
            hw = ((hw - ord(text[i]) * high) * B + ord(text[i + m])) % MOD
    return {"positions": res}


#Part 5:suffix array + Kasai
def suffix(request):
    """Order the text suffixes and use adjacent common prefixes to find repeated substrings."""
    text = request["text"]
    n = len(text)
    if n == 0:
        return {"sa": [], "lcp": [], "repeated": ""}

    rank = [ord(c) for c in text]
    sa = list(range(n))
    mult = max(n, 128) + 2
    k = 1
    while True:
        rk_ = rank
        kk = k
        keys = [rk_[i] * mult + (rk_[i + kk] + 1 if i + kk < n else 0) for i in range(n)]
        sa.sort(key=keys.__getitem__)
        new_rank = [0] * n
        r = 0
        for idx in range(1, n):
            if keys[sa[idx]] != keys[sa[idx - 1]]:
                r += 1
            new_rank[sa[idx]] = r
        rank = new_rank
        if r == n - 1:
            break
        k <<= 1

    lcp = [0] * n
    h = 0
    for i in range(n):
        ri = rank[i]
        if ri > 0:
            j = sa[ri - 1]
            while i + h < n and j + h < n and text[i + h] == text[j + h]:
                h += 1
            lcp[ri] = h
            if h > 0:
                h -= 1
        else:
            h = 0

    best = 0
    pos = 0
    for i in range(1, n):
        if lcp[i] > best:
            best = lcp[i]
            pos = sa[i]
    repeated = text[pos:pos + best] if best > 0 else ""
    return {"sa": sa, "lcp": lcp, "repeated": repeated}


#Part 6:Aho-Corasick
def aho(request):
    """Build one dictionary automaton and count its patterns in several independent texts."""
    patterns = request["patterns"]
    texts = request["texts"]
    p = len(patterns)

    # trie
    go = [{}]
    term_of = [0] * p
    is_term = [False]
    for idx, pat in enumerate(patterns):
        s = 0
        for c in pat:
            nxt = go[s].get(c)
            if nxt is None:
                nxt = len(go)
                go[s][c] = nxt
                go.append({})
                is_term.append(False)
            s = nxt
        is_term[s] = True
        term_of[idx] = s 
    S = len(go)

    fail = [0] * S
    order = []
    for c, v in go[0].items():
        order.append(v)
    qi = 0
    while qi < len(order):
        u = order[qi]
        qi += 1
        for c, v in go[u].items():
            f = fail[u]
            while f and c not in go[f]:
                f = fail[f]
            t = go[f].get(c, 0)
            fail[v] = t if t != v else 0
            order.append(v)

    tl = [-1] * S
    out_link = [-1] * S
    for v in order:
        out_link[v] = tl[fail[v]]
        tl[v] = v if is_term[v] else tl[fail[v]]
    terminals = [v for v in order if is_term[v]]  

    counts = []
    cnt = [0] * S
    for text in texts:
        state = 0
        for ch in text:
            while True:
                nxt = go[state].get(ch)
                if nxt is not None:
                    state = nxt
                    break
                if state == 0:
                    break
                state = fail[state]
            t = tl[state]
            if t >= 0:
                cnt[t] += 1
        for v in reversed(terminals):
            o = out_link[v]
            if o >= 0:
                cnt[o] += cnt[v]
        counts.append([cnt[term_of[i]] for i in range(p)])
        for v in terminals:
            cnt[v] = 0
    return {"counts": counts}
