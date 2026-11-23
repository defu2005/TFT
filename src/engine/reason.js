import { BUY, XP, ROLL, SELL, actionName } from "./decide.js"

export const CAVEAT_ODDS = "bảng tỉ lệ shop trong rules.js chưa xác minh cho Set 18"

// Builds a one-line Vietnamese reason and the factors behind it.
// `trace` is the candidate list filled by decide(state, out, trace).
export function explain(state, out, trace) {
  const chosen = out.action
  const caveats = [CAVEAT_ODDS]

  let text
  if (chosen === BUY) {
    const c = trace.find((t) => t.action === "buy" && t.slot === out.slot)
    const roll = trace.find((t) => t.action === "roll")
    text =
      `Mua ô ${out.slot} (${c?.unit ?? "?"}, cost ${c?.cost ?? "?"}): điểm ${out.score.toFixed(2)}, ` +
      `xác suất gặp ${(out.hit * 100).toFixed(1)}%, còn ${c?.copiesLeft ?? "?"} bản ` +
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
    text = `Roll để tìm ${state.target?.id ?? "mục tiêu"}: xác suất gặp ${((c?.hit ?? 0) * 100).toFixed(1)}%, điểm ${out.score.toFixed(2)}.` + (c?.free > 0 ? ` Dùng lượt roll miễn phí (còn ${c.free}).` : "") + budgetNote(c)
  } else if (chosen === SELL) {
    const c = trace.find((t) => t.action === "sell" && t.bench === out.bench)
    text = `Bán ô bench ${out.bench} (${c?.unit ?? "?"}) lấy ${c?.sellValue ?? "?"} vàng: bench đầy, cần chỗ để mua ${c?.makesRoomFor ?? "?"} (điểm ${out.score.toFixed(2)}).`
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
      gold: state.gold | 0,
      level: state.level | 0,
      stage: state.stage | 0,
      shopKnown: Array.isArray(state.shop),
      targetSet: !!state.target,
    },
    caveats,
    candidates,
  }
}

// Odds over the whole roll budget, shown only when it says more than one shop.
function budgetNote(c) {
  if (!c || !(c.rolls > 1) || !(c.hitWithin > 0)) return ""
  return ` Roll hết ${c.rolls} lượt trong ngân sách: ${(c.hitWithin * 100).toFixed(1)}%.`
}

function round(value) {
  return typeof value === "number" && Number.isFinite(value) ? Math.round(value * 1000) / 1000 : value
}
