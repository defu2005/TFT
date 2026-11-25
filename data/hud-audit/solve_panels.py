import json, sys, collections
SET = json.load(open('src/data/set18.json'))
CH = [c for c in SET['champions'] if c['traits']]
BP = {t['name']: t['breakpoints'] for t in SET['traits']}
def solve(panel, n, hidden_k):
    panel = {t: c for t, c in panel.items() if isinstance(c, int)}
    visible = set(panel)
    # champions whose traits all lie in visible or could be hidden
    cands = [c for c in CH if all(t in visible for t in c['traits']) or hidden_k > 0]
    sols = []
    def dfs(i, chosen, counts, hidden_used):
        if len(chosen) == n:
            if all(counts.get(t, 0) == panel[t] for t in visible):
                sols.append(tuple(sorted(c['name'] for c in chosen)))
            return
        if len(sols) > 200: return
        for j in range(i, len(cands)):
            c = cands[j]
            new_hidden = {t for t in c['traits'] if t not in visible}
            hu = hidden_used | new_hidden
            if len(hu) > hidden_k: continue
            if any(counts.get(t, 0) + 1 > panel[t] for t in c['traits'] if t in visible): continue
            for t in c['traits']: counts[t] = counts.get(t, 0) + 1
            dfs(j + 1, chosen + [c], counts, hu)
            for t in c['traits']: counts[t] -= 1
    dfs(0, [], {}, set())
    return sols
if __name__ == '__main__':
    panel = json.loads(sys.argv[1]); n = int(sys.argv[2]); k = int(sys.argv[3])
    s = solve(panel, n, k)
    print(len(s), s[:5])
