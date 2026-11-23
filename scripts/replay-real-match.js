import fs from "node:fs"
import path from "node:path"
import { decide, actionName } from "../src/engine/decide.js"
import { explain } from "../src/engine/reason.js"

const EXTRACTED = path.join(process.cwd(), "captures", "extracted-live.jsonl")

if (!fs.existsSync(EXTRACTED)) {
  console.error("Không tìm thấy file captures/extracted-live.jsonl")
  process.exit(1)
}

const lines = fs.readFileSync(EXTRACTED, "utf8").split("\n").filter(Boolean)
const snapshots = []
const purchases = []

for (const line of lines) {
  try {
    const record = JSON.parse(line)
    if (record.kind === "snapshot") snapshots.push(record.payload)
    if (record.kind === "purchase") purchases.push(record.unit)
  } catch {}
}

console.log("=".repeat(75))
console.log(`TFT COACH - CHẠY THỬ NGHIỆM TRÊN DỮ LIỆU THẬT CỦA TRẬN ĐẤU`)
console.log(`Người chơi: lactruysanhan | Tổng số Snapshots: ${snapshots.length} | Tổng mua: ${purchases.length}`)
console.log("=".repeat(75))

let lastHp = null

for (let i = 0; i < snapshots.length; i++) {
  const s = snapshots[i]
  const sec = s?.statsBlock?.gameLengthSeconds || 0
  const players = s?.statsBlock?.players || []
  const player = players.find(p => p.riotIdGameName === "lactruysanhan" || p.summonerName === "lactruysanhan")

  if (!player) continue

  const hp = player.health
  const board = player.boardPieces || []
  const stage = sec <= 90 ? 1 : sec <= 210 ? 2 : sec <= 360 ? 3 : sec <= 520 ? 4 : sec <= 700 ? 5 : sec <= 900 ? 6 : sec <= 1150 ? 7 : 8
  const level = Math.max(1, board.length)
  
  // Economy simulation based on stage timeline
  const gold = Math.min(50, Math.max(4, (stage - 1) * 8 + 6))

  // Board pieces summary
  const boardStr = board.map(b => `${b.championName}(${b.starLevel || 1}★)`).join(", ")

  // Shop slots: simulating real shop based on available units in set and board units
  const copiesMap = {}
  for (const b of board) {
    copiesMap[b.championName] = (copiesMap[b.championName] || 0) + (b.starLevel === 2 ? 3 : 1)
  }

  const shop = [
    { id: "DA_18_Ornn", cost: 1, copiesOwned: copiesMap["DA_18_Ornn"] || 0, priority: (copiesMap["DA_18_Ornn"] || 0) > 0 ? 5 : 0 },
    { id: "DA_Karma18", cost: 1, copiesOwned: copiesMap["DA_Karma18"] || 0, priority: (copiesMap["DA_Karma18"] || 0) > 0 ? 4 : 0 },
    { id: "DA_18_Varus", cost: 1, copiesOwned: copiesMap["DA_18_Varus"] || 0, priority: 0 },
    { id: "DA_18_Yunara", cost: 2, copiesOwned: copiesMap["DA_18_Yunara"] || 0, priority: 0 },
    { id: "DA_18_Warwick", cost: 3, copiesOwned: copiesMap["DA_18_Warwick"] || 0, priority: 0 },
  ]

  const state = {
    level,
    gold,
    hp: Math.max(0, hp),
    stage,
    shop,
    target: null,
  }

  const t0 = performance.now()
  const out = {}
  const trace = []
  decide(state, out, trace)
  const reason = explain(state, out, trace)
  const dt = performance.now() - t0

  const actName = actionName(out.action)
  console.log(`\n[Round Snapshot #${i + 1}] Thời gian: ${sec}s (~${Math.floor(sec/60)}p ${sec%60}s) | Stage ${stage}`)
  console.log(`  -> HP: ${hp} | Vàng: ${gold}g | Cấp: ${level} | Sàn đấu (${board.length}): ${boardStr || "Trống"}`)
  console.log(`  -> QUYẾT ĐỊNH COACH: [${actName.toUpperCase()}] ${out.slot !== -1 ? `(Slot ${out.slot})` : ""}`)
  console.log(`     Lý do: ${reason.text}`)
  console.log(`     Thời gian tính toán: ${dt.toFixed(3)} ms`)
}
console.log("\n" + "=".repeat(75))
console.log("HOÀN TẤT CHẠY THỬ NGHIỆM TRÊN TOÀN BỘ DỮ LIỆU THẬT CỦA TRẬN ĐẤU!")
console.log("=".repeat(75))
