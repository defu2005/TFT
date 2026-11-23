import { CHAMPS_PER_COST, POOL_COPIES, SHOP_ODDS } from "../data/rules.js"

// Chance a 5-slot shop shows a specific champion at least once.
// Slot rolls are treated as independent, which matches the usual TFT calculator.
export function hitChance(level, cost, copiesLeft, champsAtCost = CHAMPS_PER_COST[cost] ?? 1) {
  if (level < 1 || level >= SHOP_ODDS.length) return 0
  if (cost < 1 || cost > 5 || copiesLeft <= 0) return 0
  const pCost = SHOP_ODDS[level][cost - 1]
  if (pCost <= 0) return 0
  const pool = POOL_COPIES[cost]
  const others = Math.max(0, champsAtCost - 1) * pool
  const total = copiesLeft + others
  if (total <= 0) return 0
  const pSlot = pCost * (copiesLeft / total)
  const miss = 1 - pSlot
  return 1 - miss * miss * miss * miss * miss
}

// Chance of hitting the champion at least once in `rolls` independent shops.
export function hitChanceOverRolls(level, cost, copiesLeft, champsAtCost, rolls) {
  if (!(rolls > 0)) return 0
  return 1 - Math.pow(1 - hitChance(level, cost, copiesLeft, champsAtCost), rolls)
}

export function interestGold(gold) {
  const stacks = (gold / 10) | 0
  return stacks > 5 ? 5 : stacks
}
