import { DEFAULT_PROFILE } from "../data/profile.js"

// Chance a 5-slot shop shows a specific champion at least once.
// Slot rolls are treated as independent, which matches the usual TFT calculator.
export function hitChance(level, cost, copiesLeft, champsAtCost, profile) {
  const p = profile || DEFAULT_PROFILE
  const champs = champsAtCost === undefined ? (p.champsPerCost[cost] ?? 1) : champsAtCost
  if (level < 1 || level >= p.shopOdds.length) return 0
  if (cost < 1 || cost > p.maxCost || copiesLeft <= 0) return 0
  const pCost = p.shopOdds[level][cost - 1]
  if (pCost <= 0) return 0
  const pool = p.poolCopies[cost]
  const others = Math.max(0, champs - 1) * pool
  const total = copiesLeft + others
  if (total <= 0) return 0
  const pSlot = pCost * (copiesLeft / total)
  const miss = 1 - pSlot
  return 1 - miss * miss * miss * miss * miss
}

// Chance of hitting the champion at least once in `rolls` independent shops.
export function hitChanceOverRolls(level, cost, copiesLeft, champsAtCost, rolls, profile) {
  if (!(rolls > 0)) return 0
  return 1 - Math.pow(1 - hitChance(level, cost, copiesLeft, champsAtCost, profile), rolls)
}

// Chance of at least k hits among n independent slots, each hitting with per-slot chance p.
// Binomial tail: 1 - sum_{j<k} C(n,j) p^j (1-p)^(n-j), computed term by term to stay stable for large n.
export function atLeastKOfSlots(p, n, k) {
  if (!(k >= 1) || !(n >= 0)) return 0
  if (p <= 0) return 0
  if (p >= 1) return n >= k ? 1 : 0
  if (k > n) return 0
  let term = Math.pow(1 - p, n)
  let cum = term
  for (let j = 0; j < k - 1; j++) {
    term = (term * (n - j) / (j + 1)) * (p / (1 - p))
    cum += term
  }
  return Math.max(0, 1 - cum)
}

// Per-slot chance of the target, as in hitChance (before the 5-slot combination).
export function slotChance(level, cost, copiesLeft, champsAtCost, profile) {
  const p = profile || DEFAULT_PROFILE
  const champs = champsAtCost === undefined ? (p.champsPerCost[cost] ?? 1) : champsAtCost
  if (level < 1 || level >= p.shopOdds.length) return 0
  if (cost < 1 || cost > p.maxCost || copiesLeft <= 0) return 0
  const pCost = p.shopOdds[level][cost - 1]
  if (pCost <= 0) return 0
  const pool = p.poolCopies[cost]
  const total = copiesLeft + Math.max(0, champs - 1) * pool
  if (total <= 0) return 0
  return pCost * (copiesLeft / total)
}

// Chance of at least k copies within `rolls` shops of SHOP_SLOTS slots each (independent slots).
export const SHOP_SLOTS = 5
export function hitAtLeastKOverRolls(level, cost, copiesLeft, champsAtCost, k, rolls, profile) {
  if (!(rolls > 0)) return 0
  // k copies of one unit need k copies in the pool; the independent-slot model cannot see that.
  if (copiesLeft < k) return 0
  return atLeastKOfSlots(slotChance(level, cost, copiesLeft, champsAtCost, profile), SHOP_SLOTS * Math.floor(rolls), k)
}

export function interestGold(gold) {
  const stacks = (gold / 10) | 0
  return stacks > 5 ? 5 : stacks
}
