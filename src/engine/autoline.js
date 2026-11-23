// Line priorities from the board and the set's traits. Pure, no I/O.

// index: { traitsOf: Map(championId -> traits[]), breakpoints: Map(traitName -> minUnits[]) }
export function createSetIndex(setData) {
  const traitsOf = new Map()
  for (const c of setData?.champions ?? []) {
    if (c && typeof c.id === "string" && Array.isArray(c.traits)) traitsOf.set(c.id, c.traits)
  }
  const breakpoints = new Map()
  for (const t of setData?.traits ?? []) {
    if (t && typeof t.name === "string" && Array.isArray(t.breakpoints)) breakpoints.set(t.name, t.breakpoints)
  }
  return { traitsOf, breakpoints }
}

// Map(unit id -> priority 1..5) for shop and bench units that fit the board.
// Units are rated against the board only, so a bench unit that does not fit stays sellable.
export function autoLine(index, state) {
  const out = new Map()
  const board = ids(state.board)
  if (board.size === 0) return out
  const count = new Map()
  for (const id of board) for (const t of index.traitsOf.get(id) ?? []) count.set(t, (count.get(t) ?? 0) + 1)
  rate(out, index, state.shop, board, count)
  rate(out, index, state.bench, board, count)
  return out
}

function rate(out, index, list, board, count) {
  if (!Array.isArray(list)) return
  for (const u of list) {
    const key = unitKey(u)
    if (!key || out.has(key)) continue
    let p = 0
    if (board.has(key)) p = 2
    else {
      for (const t of index.traitsOf.get(key) ?? []) {
        const n = count.get(t) ?? 0
        if (n > 0) p += index.breakpoints.get(t)?.includes(n + 1) ? 2 : 1
      }
    }
    if (p > 0) out.set(key, p > 5 ? 5 : p)
  }
}

// Units on shop, bench or board that the auto line cannot rate: keys the set file does not know,
// and units with neither id nor championName. A board that is not an array (the live and RAM sources
// send none) is reported as boardMissing. The auto line skips all of these silently, so the coach reports them.
export function unknownIds(index, state) {
  const unknown = new Set()
  let missingId = 0
  for (const list of [state.shop, state.bench, state.board]) {
    if (!Array.isArray(list)) continue
    for (const u of list) {
      if (!u || typeof u !== "object") continue
      const key = unitKey(u)
      if (!key) missingId += 1
      else if (!index.traitsOf.has(key)) unknown.add(key)
    }
  }
  return { ids: [...unknown].sort(), missingId, boardMissing: !Array.isArray(state.board) }
}

// The live HUD and the standalone source give the board as championName; shop and bench carry id.
// A unit's key is its id when it has one, else its championName. Only this module reads that fallback.
function unitKey(u) {
  if (!u || typeof u !== "object") return null
  if (typeof u.id === "string") return u.id
  if (typeof u.championName === "string") return u.championName
  return null
}

function ids(list) {
  const set = new Set()
  if (Array.isArray(list)) for (const u of list) {
    const key = unitKey(u)
    if (key) set.add(key)
  }
  return set
}
