import { BUY, XP, ROLL, SELL, actionName } from "./decide.js"

export const CAVEAT_ODDS = "bảng tỉ lệ shop trong rules.js chưa xác minh cho Set 18"

// Builds a one-line Vietnamese reason and the factors behind it.
// `trace` is the candidate list filled by decide(state, out, trace).
export function explain(state, out, trace, oddsCaveat = CAVEAT_ODDS) {
  const chosen = out.action
  const caveats = [oddsCaveat]

  let text
  if (chosen === BUY) {
    const c = trace.find((t) => t.action === "buy" && t.slot === out.slot)
    const roll = trace.find((t) => t.action === "roll")
    text =
      `Mua ô ${out.slot + 1} (${c?.unit ?? "?"}, cost ${c?.cost ?? "?"}${c?.price !== undefined && c.price !== c.cost ? `, giá ${c.price ?? "chưa đọc"}` : ""}): điểm ${out.score.toFixed(2)}, ` +
      `${c?.hit === null ? "xác suất chưa tính (chưa đọc được cấp)" : `xác suất gặp ${(out.hit * 100).toFixed(1)}%`}, còn ${c?.copiesLeft ?? "?"} bản ` +
      `(nguồn số bản: ${c?.copiesSource ?? "?"}), mất ${c?.interestLoss ?? 0} lãi.` +
      (roll && roll.score > 0.45 && roll.score > out.score ? " Mua trước rồi mới roll, vì roll sẽ thay shop." : "")
    if (c?.copiesSource === "pool - copiesOwned (ước lượng)") {
      caveats.push("số bản còn lại là ước lượng vì state không có số bản của người chơi khác")
    }
  } else if (chosen === XP) {
    const c = trace.find((t) => t.action === "xp")
    text = `Lên level: level ${c?.level} dưới mục tiêu ${c?.wanted} của stage ${c?.stage}, vàng ${state.gold} đủ điều kiện.`
  } else if (chosen === ROLL) {
    const c = trace.find((t) => t.action === "roll")
    text = `Roll để tìm ${state.target?.id ?? "mục tiêu"}: ${c?.hit === null ? "xác suất chưa tính (chưa đọc được cấp)" : `xác suất gặp ${((c?.hit ?? 0) * 100).toFixed(1)}%`}, điểm ${out.score.toFixed(2)}.` + (c?.free > 0 ? ` Dùng lượt roll miễn phí (còn ${c.free}).` : "") + (c?.budgeted ? budgetSentence(c) : budgetNote(c))
  } else if (chosen === SELL) {
    const c = trace.find((t) => t.action === "sell" && t.bench === out.bench)
    text = `Bán ô bench ${out.bench + 1} (${c?.unit ?? "?"}) lấy ${c?.sellValue ?? "?"} vàng: bench đầy, cần chỗ để mua ${c?.makesRoomFor ?? "?"} (điểm ${out.score.toFixed(2)}).`
  } else {
    const blocked = trace.filter((c) => c.action === "buy" && c.note && c.note !== "ô trống").map((c) => c.note)
    const reasons = [...new Set(blocked)].slice(0, 3)
    const xp = trace.find((c) => c.action === "xp")
    const roll = trace.find((c) => c.action === "roll")
    text = "Giữ vàng: không có hành động nào vượt ngưỡng."
    if (reasons.length) text += " Mua: " + reasons.join("; ") + "."
    text += ` XP ${round(xp?.score ?? 0)} (ngưỡng 0.5)` + (xp?.note ? ` — ${xp.note}` : "") + "."
    text += ` Roll ${round(roll?.score ?? 0)} (ngưỡng 0.45)` + (roll?.note ? ` — ${roll.note}` : "") + "."
    text += budgetNote(roll)
  }

  const candidates = trace.map((c) => ({ ...c, score: round(c.score) }))
  return {
    action: actionName(chosen),
    text: `${text} (${caveats.join("; ")})`,
    factors: {
      hpUrgent: (state.hp | 0) <= 30,
      // Unknown values are null, never the number the engine used.
      gold: state.hudGoldUnknown ? null : state.gold | 0,
      level: state.hudLevelUnknown ? null : state.level | 0,
      stage: state.stage | 0,
      shopKnown: Array.isArray(state.shop) && !(state.shopUnknownSlots?.length),
      targetSet: !!state.target,
    },
    caveats,
    candidates,
  }
}

// Odds over the whole roll budget, shown only when it says more than one shop.
// Opt-in rule: the budget left after buying the copies needed, and the chance of finishing them in it.
function budgetSentence(c) {
  if (!c.ownedKnown) return " Thiếu board hoặc bench nên không biết số bản đang có: tính cần 1 bản."
  if (!(c.budgetHit > 0)) return ` Ngân sách ${c.budgetRolls} lượt không đủ để gặp ${c.copiesNeeded} bản: không roll.`
  return ` Ngân sách ${c.budgetRolls} lượt: xác suất gặp ít nhất ${c.copiesNeeded} bản ${(c.budgetHit * 100).toFixed(1)}%.`
}

function budgetNote(c) {
  if (!c || c.budgeted || !(c.rolls > 1) || !(c.hitWithin > 0)) return ""
  return ` Roll hết ${c.rolls} lượt trong ngân sách: ${(c.hitWithin * 100).toFixed(1)}%.`
}

function round(value) {
  return typeof value === "number" && Number.isFinite(value) ? Math.round(value * 1000) / 1000 : value
}
