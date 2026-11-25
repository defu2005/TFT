import re, sys
ALIAS = '/tmp/claude-0/-home-user-TFT/91722103-108d-57a1-a27d-f308a4301820/scratchpad/alias_map_PRIVATE.txt'
STOP = {'streamer', 'planning', 'combat', 'shared', 'arena', 'frame', 'player', 'alias', 'name'}
names = set()
for line in open(ALIAS, encoding='utf-8'):
    for tok in re.split(r'[^A-Za-z0-9_]+', line):
        if len(tok) >= 4 and tok.lower() not in STOP and not re.fullmatch(r'P\d', tok):
            names.add(tok)
bad = []
for f in sys.argv[1:]:
    txt = open(f, encoding='utf-8').read()
    for n in names:
        if re.search(r'\b' + re.escape(n) + r'\b', txt): bad.append((f, n))
if bad:
    print('PRIVATE NAME HITS:', len(bad)); sys.exit(1)
print('guard ok')
