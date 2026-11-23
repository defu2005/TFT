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

export function interestGold(gold) {
  const stacks = (gold / 10) | 0
  return stacks > 5 ? 5 : stacks
}
