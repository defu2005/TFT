import json
SRC = 'data/hud-audit/match01_full.json'
OUT = 'docs/sim/match01-rounds.md'
d = json.load(open(SRC, encoding='utf-8'))
rounds = d['rounds']

def unpack(v):
    if isinstance(v, dict) and 'tag' in v:
        return v.get('value'), v.get('tag')
    return v, 'read'

def mark(val, tag):
    if val in (None, '', [], {}):
        return '—[u]' if tag in (None, 'unresolved') else f'—[{tag}]'
    if tag == 'derived':
        return f'{val} [d]'
    if tag == 'n/a':
        return '—[n]'
    if tag == 'unresolved':
        return '—[u]'
    return str(val)

def plan(r, key):
    p = r.get('planning') or {}
    v = p.get('value') or {}
    return v.get(key) if isinstance(v, dict) else None

def pl_tag(r, key):
    v = plan(r, key)
    if isinstance(v, dict) and 'tag' in v:
        return v.get('value'), v.get('tag')
    return v, 'read' if v is not None else 'unresolved'

L = []
L.append('# Dữ liệu trận 01 (Set 18) theo vòng')
L.append('')
L.append('Nguồn: `data/hud-audit/match01_full.json`, xuất bằng `data/hud-audit/export_sim_md.py`. Một trận, 38 vòng. Mục tiêu theo `workstream_sim`: HP, stage/round, timer, streak, bàn và bàn chờ, sao, trang bị, augment, kết quả combat, thứ hạng, HP đối thủ.')
L.append('')
L.append('Chú thích: không đánh dấu = đọc trực tiếp (`read`); `[d]` = suy ra (`derived`); `[u]` = chưa giải (`unresolved`); `[n]` = không áp dụng (`n/a`). Đối thủ dùng mã P, không dùng tên người chơi.')
L.append('')
L.append('## 1. Bảng theo vòng')
L.append('')
L.append('| Vòng | t kế hoạch (s) | Timer | Cấp | XP | Vàng | Streak | HP P1..P8 | Kết quả | Loại | Đối thủ | Bàn (số, tướng) | Bàn chờ | Sao | Trang bị | Augment |')
L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for r in rounds:
    rid = r['round']
    t = r.get('t_planning_s')
    timer = pl_tag(r, 'timer'); level = pl_tag(r, 'level'); xp = pl_tag(r, 'xp')
    gold = pl_tag(r, 'gold'); streak = pl_tag(r, 'streak')
    hp = r.get('hp') or {}
    hpv = hp.get('value') if isinstance(hp, dict) else None
    hp_cell = '/'.join('—' if x is None else str(x) for x in hpv) if isinstance(hpv, list) else '—[u]'
    res = r.get('result') or {}
    rv = res.get('value'); outcome = rv.get('outcome') if isinstance(rv, dict) else None
    res_cell = mark(outcome, res.get('tag'))
    rtype = r.get('round_type') or {}
    rt = mark(rtype.get('value'), rtype.get('tag'))
    op = r.get('opponent') or {}
    opc = mark(op.get('value'), op.get('tag'))
    bu = r.get('board_units') or {}
    buv = bu.get('value')
    bu_cell = (f"{len(buv)}: " + ', '.join(buv)) if isinstance(buv, list) and buv else mark(None, bu.get('tag'))
    if bu_cell and isinstance(buv, list) and bu.get('tag') == 'derived':
        bu_cell += ' [d]'
    bn = r.get('bench_units') or {}
    bnv = bn.get('value')
    bn_cell = mark(bnv, bn.get('tag') if isinstance(bnv, int) else bn.get('tag'))
    if isinstance(bnv, int) and bn.get('tag') == 'read':
        bn_cell = str(bnv)
    st = r.get('stars') or {}
    st_cell = mark(st.get('value'), st.get('tag'))
    it = r.get('items') or {}
    it_cell = mark(it.get('value'), it.get('tag'))
    au = r.get('augment') or {}
    av = au.get('value')
    au_cell = mark(av if au.get('tag') != 'n/a' else None, au.get('tag'))
    def c(x):
        if isinstance(x, tuple):
            val, tag = x
            return mark(val, tag)
        return str(x)
    L.append('| ' + ' | '.join([rid, '—' if t is None else str(t), c(timer), c(level), c(xp), c(gold), c(streak),
                                  hp_cell, res_cell, rt, opc, bu_cell, bn_cell, st_cell, it_cell, au_cell]) + ' |')
L.append('')
L.append('## 2. Thứ hạng cuối trận')
L.append('')
pl = d.get('placements') or {}
for k in ['1', '2', '3', '4', '5', '6', '7', '8']:
    L.append(f'- {k}: {pl.get(k, "[u]")}')
L.append('')
L.append('## 3. Trạng thái theo trường (số vòng)')
L.append('')
L.append('| Trường | Đọc | Suy ra | Chưa giải | n/a |')
L.append('|---|---|---|---|---|')
def tally(getter):
    c = {'read': 0, 'derived': 0, 'unresolved': 0, 'n/a': 0}
    for r in rounds:
        tag = getter(r)
        c[tag if tag in c else 'unresolved'] = c.get(tag if tag in c else 'unresolved', 0) + 1
    return c
fields = {
    'HP 8 người': lambda r: (r.get('hp') or {}).get('tag', 'unresolved'),
    'Stage/round': lambda r: 'read' if r.get('round') else 'unresolved',
    'Timer': lambda r: pl_tag(r, 'timer')[1] if pl_tag(r, 'timer')[0] is not None else 'unresolved',
    'Streak': lambda r: pl_tag(r, 'streak')[1] if pl_tag(r, 'streak')[0] is not None else 'unresolved',
    'Bàn': lambda r: (r.get('board_units') or {}).get('tag', 'unresolved'),
    'Bàn chờ': lambda r: (r.get('bench_units') or {}).get('tag', 'unresolved'),
    'Sao': lambda r: (r.get('stars') or {}).get('tag', 'unresolved'),
    'Trang bị': lambda r: (r.get('items') or {}).get('tag', 'unresolved'),
    'Augment': lambda r: (r.get('augment') or {}).get('tag', 'unresolved'),
    'Kết quả': lambda r: (r.get('result') or {}).get('tag', 'unresolved'),
    'Đối thủ': lambda r: (r.get('opponent') or {}).get('tag', 'unresolved'),
}
for name, g in fields.items():
    c = tally(g)
    L.append(f"| {name} | {c['read']} | {c['derived']} | {c['unresolved']} | {c['n/a']} |")
L.append('')
L.append('## 4. Tỉ lệ đúng đã đo')
L.append('')
L.append('- Đọc lại mù trong mẫu (10 vòng): vàng 10/10, chuỗi thắng 9/10, cấp 10/10, XP 10/10 (crop đã tinh chỉnh sau khi xem mẫu).')
L.append('- Ngoài mẫu (19 vòng có khung kế hoạch, `data/hud-audit/blind_oos28_rates.json`): vàng 13/16, chuỗi thắng 4/14, cấp 11/15, XP 13/14.')
L.append('- HP, bàn, bàn chờ, kết quả, thứ hạng, HP đối thủ: chưa đo tỉ lệ đúng.')
L.append('')
L.append('## 5. Khoảng trống')
L.append('')
L.append('- Sao và trang bị: phần lớn chưa giải; nguồn 720p không đủ để đọc. Có một đối chứng 1080p, chưa đọc thử.')
L.append('- Augment: chỉ có trong vòng có màn chọn augment.')
L.append('- Chỉ có một trận; workstream sim cần nhiều trận và log set thứ hai.')
L.append('')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('wrote', OUT, len(L), 'lines')
