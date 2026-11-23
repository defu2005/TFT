import { BUY_XP_COST, LEVEL_BY_STAGE, POOL_COPIES, REROLL_COST } from "../data/rules.js"
import { hitChance, interestGold } from "./odds.js"

export const HOLD = 0
export const BUY = 1
export const XP = 2
export const ROLL = 3
export const SELL = 4

const ACTION_NAME = ["hold", "buy", "xp", "roll", "sell"]

export function actionName(code) {
  return ACTION_NAME[code] ?? "hold"
}

// Fills `out` and returns it. No network, no model call.
// state.shop is a 5-slot array of { id, cost, copiesOwned, priority, poolCopies?, takenByOthers? } or null.
// state.board, state.bench (fixed length, null = empty) and state.freeRolls are optional; absent means unknown.
// state.bench units may carry sellValue; a sell needs it.
// priority > 0 means the unit is in the line we are playing.
//
// When `trace` is an array, every candidate considered is pushed into it with the
// numbers behind its score. The hot path passes no trace and allocates nothing extra.
export function decide(state, out, trace = null) {
  out.action = HOLD
  out.slot = -1
  out.score = 0
  out.hit = 0
  out.bench = -1

  const level = state.level | 0
  const gold = state.gold | 0
  const hp = state.hp | 0
  const stage = state.stage | 0
  const shop = state.shop
  const target = state.target
  const urgent = hp <= 30
  const freeRolls = state.freeRolls > 0 ? state.freeRolls | 0 : 0
  const rollNeeds = freeRolls > 0 ? 0 : REROLL_COST + (urgent ? 0 : 10)

  let bestBuy = 0
  let bestSlot = -1
  let bestHit = 0
  let targetInShop = false
  let keepBuy = 0
  let keepSlot = -1
  let keepHit = 0
  // Fixed-length array, null = empty slot. Absent or empty means unknown.
  const bench = Array.isArray(state.bench) && state.bench.length > 0 ? state.bench : null
  let benchFull = !!bench
  if (bench) for (let j = 0; j < bench.length; j++) if (!bench[j]) benchFull = false
  let blockedBuy = 0
  let blockedUnit = null

  if (shop) {
    for (let i = 0; i < 5; i++) {
      const unit = shop[i]
      if (!unit) {
        if (trace) trace.push({ action: "buy", slot: i, score: 0, note: "ô trống" })
        continue
      }
      const isTarget = !!target && target.id != null && unit.id === target.id
      if (isTarget) targetInShop = true
      const priority = isTarget ? Math.max(unit.priority || 0, target.priority || 0) : unit.priority || 0
      if (!(priority > 0)) {
        if (trace) trace.push({ action: "buy", slot: i, unit: unit.id, cost: unit.cost, score: 0, note: "không nằm trong line (priority 0)" })
        continue
      }
      if (!(unit.cost >= 1)) {
        if (trace) trace.push({ action: "buy", slot: i, unit: unit.id, score: 0, note: "thiếu cost" })
        continue
      }
      if (gold < unit.cost) {
        if (trace) trace.push({ action: "buy", slot: i, unit: unit.id, cost: unit.cost, score: 0, note: `thiếu vàng (cần ${unit.cost}, có ${gold})` })
        continue
      }
      const owned = Math.max(unit.copiesOwned | 0, countCopies(state.board, unit.id) + countCopies(state.bench, unit.id))
      const taken = unit.takenByOthers == null ? 0 : unit.takenByOthers | 0
      if (owned >= 9) {
        if (trace) trace.push({ action: "buy", slot: i, unit: unit.id, cost: unit.cost, score: 0, note: "đã đủ 9 bản (3 sao)" })
        continue
      }
      // The target's copy count applies only to the target unit itself.
      const copiesFromTarget = isTarget ? target.copiesLeft ?? 0 : 0
      const copiesSource = copiesFromTarget > 0 ? "target" : unit.poolCopies != null ? "poolCopies" : unit.takenByOthers != null ? "pool - copiesOwned - takenByOthers" : "pool - copiesOwned (ước lượng)"
      const copiesLeft = Math.max(0, copiesFromTarget || (POOL_FALLBACK(unit) - owned - taken))
      const champsAtCost = unit.champsAtCost
      const hit = hitChance(level, unit.cost, copiesLeft, champsAtCost)
      const interestLoss = interestGold(gold) - interestGold(gold - unit.cost)
      let score = priority * (1 + owned) * (0.4 + hit)
      if (!urgent) score -= interestLoss * 0.35
      if (owned % 3 === 2) score += 1.5
      const blocked = benchFull && owned % 3 !== 2
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
          priority,
          copiesOwned: owned,
          takenByOthers: taken,
          note: blocked ? "bench đầy, lượt mua không hoàn thành sao" : "",
        })
      }
      if (blocked) {
        if (score > blockedBuy) {
          blockedBuy = score
          blockedUnit = unit.id
        }
      } else if (score > bestBuy) {
        bestBuy = score
        bestSlot = i
        bestHit = hit
      }
      if (!blocked && score > keepBuy && gold - unit.cost >= rollNeeds) {
        keepBuy = score
        keepSlot = i
        keepHit = hit
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
  const rollAffordable = !!target?.cost && gold >= rollNeeds
  let rollHit = 0
  if (target && target.cost && rollAffordable && !targetInShop) {
    rollHit = hitChance(level, target.cost, target.copiesLeft, target.champsAtCost)
    rollScore = rollHit * target.priority * (urgent ? 2 : 0.8)
    if (!urgent && freeRolls === 0) rollScore -= 0.5
  }
  if (trace) {
    trace.push({
      action: "roll",
      score: rollScore,
      hit: rollHit,
      needs: rollNeeds,
      free: freeRolls,
      note: !target ? "không có mục tiêu (set_target chưa được gọi)" : targetInShop ? "mục tiêu đang có trong shop" : !rollAffordable ? `thiếu vàng để roll (cần ${rollNeeds})` : "",
    })
  }

  const xpLive = xpScore > 0.5 ? xpScore : 0
  const rollLive = rollScore > 0.45 ? rollScore : 0

  let sellScore = 0
  let sellBench = -1
  let sellGold = -1
  if (bench) {
    for (let j = 0; j < bench.length; j++) {
      const u = bench[j]
      if (!u) continue
      const inLine = u.priority > 0 || (!!target && target.id != null && u.id === target.id) || wantedInShop(shop, u.id)
      const value = typeof u.sellValue === "number" ? u.sellValue : -1
      const score = !inLine && value >= 0 ? blockedBuy : 0
      if (trace) {
        trace.push({
          action: "sell",
          bench: j,
          unit: u.id,
          sellValue: value < 0 ? null : value,
          score,
          makesRoomFor: score > 0 ? blockedUnit : null,
          note: inLine ? "nằm trong line hoặc là mục tiêu" : value < 0 ? "thiếu sellValue" : blockedBuy > 0 ? "" : "không có lượt mua nào bị chặn vì bench đầy",
        })
      }
      if (score > 0 && value > sellGold) {
        sellScore = score
        sellBench = j
        sellGold = value
      }
    }
  } else if (trace) {
    trace.push({ action: "sell", score: 0, note: "không có dữ liệu bench" })
  }
  if (bestBuy <= 0 && sellScore > 0 && sellScore >= xpLive && sellScore >= rollLive) {
    out.action = SELL
    out.bench = sellBench
    out.score = sellScore
    return out
  }

  if (bestBuy > 0 && bestBuy >= xpLive && bestBuy >= rollLive) {
    out.action = BUY
    out.slot = bestSlot
    out.score = bestBuy
    out.hit = bestHit
    return out
  }
  if (xpLive > 0 && xpLive >= rollLive) {
    out.action = XP
    out.score = xpScore
    return out
  }
  if (rollLive > 0) {
    if (keepSlot >= 0) {
      out.action = BUY
      out.slot = keepSlot
      out.score = keepBuy
      out.hit = keepHit
      return out
    }
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

function wantedInShop(shop, id) {
  if (!shop) return false
  for (let i = 0; i < 5; i++) {
    const s = shop[i]
    if (s && s.priority > 0 && s.id === id) return true
  }
  return false
}

function countCopies(list, id) {
  if (!Array.isArray(list)) return 0
  let n = 0
  for (let i = 0; i < list.length; i++) {
    const u = list[i]
    if (u && u.id === id) n += u.star === 3 ? 9 : u.star === 2 ? 3 : 1
  }
  return n
}
