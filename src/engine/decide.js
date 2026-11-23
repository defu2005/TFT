import { BUY_XP_COST, LEVEL_BY_STAGE, POOL_COPIES, REROLL_COST } from "../data/rules.js"
import { hitChance, interestGold } from "./odds.js"

export const HOLD = 0
export const BUY = 1
export const XP = 2
export const ROLL = 3

const ACTION_NAME = ["hold", "buy", "xp", "roll"]

export function actionName(code) {
  return ACTION_NAME[code] ?? "hold"
}

// Fills `out` and returns it. No network, no model call.
// state.shop is a 5-slot array of { id, cost, copiesOwned, priority, poolCopies? } or null.
// priority > 0 means the unit is in the line we are playing.
//
// When `trace` is an array, every candidate considered is pushed into it with the
// numbers behind its score. The hot path passes no trace and allocates nothing extra.
export function decide(state, out, trace = null) {
  out.action = HOLD
  out.slot = -1
  out.score = 0
  out.hit = 0

  const level = state.level | 0
  const gold = state.gold | 0
  const hp = state.hp | 0
  const stage = state.stage | 0
  const shop = state.shop
  const target = state.target
  const urgent = hp <= 30

  let bestBuy = 0
  let bestSlot = -1
  let bestHit = 0

  if (shop) {
    for (let i = 0; i < 5; i++) {
      const unit = shop[i]
      if (!unit) {
        if (trace) trace.push({ action: "buy", slot: i, score: 0, note: "ô trống" })
        continue
      }
      if (unit.priority <= 0) {
        if (trace) trace.push({ action: "buy", slot: i, unit: unit.id, cost: unit.cost, score: 0, note: "không nằm trong line (priority 0)" })
        continue
      }
      if (gold < unit.cost) {
        if (trace) trace.push({ action: "buy", slot: i, unit: unit.id, cost: unit.cost, score: 0, note: `thiếu vàng (cần ${unit.cost}, có ${gold})` })
        continue
      }
      // The target's copy count applies only to the target unit itself.
      const isTarget = !!target && target.id != null && unit.id === target.id
      const copiesFromTarget = isTarget ? target.copiesLeft ?? 0 : 0
      const copiesSource = copiesFromTarget > 0 ? "target" : unit.poolCopies != null ? "poolCopies" : "pool - copiesOwned (ước lượng)"
      const copiesLeft = Math.max(0, copiesFromTarget || (POOL_FALLBACK(unit) - (unit.copiesOwned | 0)))
      const champsAtCost = unit.champsAtCost
      const hit = hitChance(level, unit.cost, copiesLeft, champsAtCost)
      const interestLoss = interestGold(gold) - interestGold(gold - unit.cost)
      let score = unit.priority * (1 + (unit.copiesOwned | 0)) * (0.4 + hit)
      if (!urgent) score -= interestLoss * 0.35
      if (unit.copiesOwned >= 2) score += 1.5
      if (trace) {
        trace.push({
          action: "buy",
          slot: i,
          unit: unit.id,
          cost: unit.cost,
          score,
          hit,
          copiesLeft,
          copiesSource,
          interestLoss,
          priority: unit.priority,
          copiesOwned: unit.copiesOwned | 0,
        })
      }
      if (score > bestBuy) {
        bestBuy = score
        bestSlot = i
        bestHit = hit
      }
    }
  }

  const wanted = LEVEL_BY_STAGE[stage] ?? LEVEL_BY_STAGE[LEVEL_BY_STAGE.length - 1]
  let xpScore = 0
  const xpAffordable = gold >= 50 && gold >= BUY_XP_COST
  if (level < wanted && xpAffordable) {
    xpScore = (wanted - level) * (urgent ? 0.6 : 1.1)
  }
  if (trace) {
    trace.push({
      action: "xp",
      score: xpScore,
      level,
      wanted,
      stage,
      note: level >= wanted ? `level ${level} đã đạt mục tiêu ${wanted}` : !xpAffordable ? `chưa đủ điều kiện (vàng ${gold}, cần 50 và ${BUY_XP_COST})` : "",
    })
  }

  let rollScore = 0
  const rollAffordable = !!target?.cost && gold >= REROLL_COST + (urgent ? 0 : 10)
  let rollHit = 0
  if (target && target.cost && rollAffordable) {
    rollHit = hitChance(level, target.cost, target.copiesLeft, target.champsAtCost)
    rollScore = rollHit * target.priority * (urgent ? 2 : 0.8)
    if (!urgent) rollScore -= 0.5
  }
  if (trace) {
    trace.push({
      action: "roll",
      score: rollScore,
      hit: rollHit,
      note: !target ? "không có mục tiêu (set_target chưa được gọi)" : !rollAffordable ? `thiếu vàng để roll (cần ${REROLL_COST + (urgent ? 0 : 10)})` : "",
    })
  }

  if (bestBuy >= xpScore && bestBuy >= rollScore && bestBuy > 0) {
    out.action = BUY
    out.slot = bestSlot
    out.score = bestBuy
    out.hit = bestHit
    return out
  }
  if (xpScore >= rollScore && xpScore > 0.5) {
    out.action = XP
    out.score = xpScore
    return out
  }
  if (rollScore > 0.45) {
    out.action = ROLL
    out.score = rollScore
    out.hit = rollHit
    return out
  }
  out.score = bestBuy
  return out
}

function POOL_FALLBACK(unit) {
  return unit.poolCopies ?? POOL_COPIES[unit.cost] ?? 0
}
