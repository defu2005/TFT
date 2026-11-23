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
    if (!u || typeof u.id !== "string" || out.has(u.id)) continue
    let p = 0
    if (board.has(u.id)) p = 2
    else {
      for (const t of index.traitsOf.get(u.id) ?? []) {
        const n = count.get(t) ?? 0
        if (n > 0) p += index.breakpoints.get(t)?.includes(n + 1) ? 2 : 1
      }
    }
    if (p > 0) out.set(u.id, p > 5 ? 5 : p)
  }
}

// Units on shop, bench or board that the auto line cannot rate: ids the set file does not know,
// and units with no id at all (the live HUD gives only a name). The auto line skips both silently,
// so the coach reports them. Returns { ids: sorted unique unknown ids, missingId: count }.
export function unknownIds(index, state) {
  const unknown = new Set()
  let missingId = 0
  for (const list of [state.shop, state.bench, state.board]) {
    if (!Array.isArray(list)) continue
    for (const u of list) {
      if (!u || typeof u !== "object") continue
      if (typeof u.id !== "string") missingId += 1
      else if (!index.traitsOf.has(u.id)) unknown.add(u.id)
    }
  }
  return { ids: [...unknown].sort(), missingId }
}

function ids(list) {
  const set = new Set()
  if (Array.isArray(list)) for (const u of list) if (u && typeof u.id === "string") set.add(u.id)
  return set
}
