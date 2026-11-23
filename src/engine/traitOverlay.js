// Adds traits to champions in a set index, from an explicit overlay file (TFT_TRAIT_OVERLAY).
// Add-only: an overlay can give a champion a trait, never remove one, because the patch notes
// that use it state the new trait and do not say whether the old one stays. Pure, no I/O.
//
// overlay: { set, verified, note, champions: { "<champion id>": { add: ["<trait name>", ...] } } }

const OVERLAY_KEYS = ["set", "verified", "note", "champions"]
const ENTRY_KEYS = ["add"]

export function applyTraitOverlay(index, overlay) {
  if (!overlay || typeof overlay !== "object" || Array.isArray(overlay)) throw new Error("trait overlay phải là một object")
  for (const key of Object.keys(overlay)) {
    if (!OVERLAY_KEYS.includes(key)) throw new Error(`trait overlay: trường không rõ "${key}"`)
  }
  if (typeof overlay.set !== "string") throw new Error("trait overlay cần trường set")
  if (typeof overlay.verified !== "boolean") throw new Error("trait overlay cần verified (true|false)")
  if (overlay.champions === undefined || typeof overlay.champions !== "object" || Array.isArray(overlay.champions)) {
    throw new Error("trait overlay cần champions là object")
  }

  const traitsOf = new Map()
  for (const [id, traits] of index.traitsOf) traitsOf.set(id, [...traits])
  let applied = 0
  for (const [id, entry] of Object.entries(overlay.champions)) {
    if (!traitsOf.has(id)) throw new Error(`trait overlay: tướng "${id}" không có trong file set`)
    if (!entry || typeof entry !== "object") throw new Error(`trait overlay: mục của "${id}" phải là object`)
    for (const key of Object.keys(entry)) {
      if (!ENTRY_KEYS.includes(key)) throw new Error(`trait overlay: "${id}" có trường không rõ "${key}"`)
    }
    if (entry.add !== undefined && !Array.isArray(entry.add)) throw new Error(`trait overlay: add của "${id}" phải là mảng`)
    for (const trait of entry.add ?? []) {
      if (typeof trait !== "string" || !index.breakpoints.has(trait)) {
        throw new Error(`trait overlay: tộc "${trait}" của "${id}" không có trong file set`)
      }
      if (!traitsOf.get(id).includes(trait)) {
        traitsOf.get(id).push(trait)
        applied += 1
      }
    }
  }
  return { traitsOf, breakpoints: index.breakpoints, applied, set: overlay.set, verified: overlay.verified, note: overlay.note ?? "" }
}
