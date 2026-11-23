import assert from "node:assert/strict"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import test from "node:test"
import { toState } from "./liveClient.js"
import { captureSource } from "./sources.js"
import { startCapture } from "./capture.js"
import { createCoach } from "../core/coach.js"

const fullPayload = () => ({
  activePlayer: { currentGold: 42, level: 7, championStats: { currentHealth: 55 } },
  gameData: { round: 4 },
  shop: [{ id: "B", cost: 3, copiesOwned: 2, priority: 0 }, null, null, null, null],
})

test("a full payload maps to a state with no missing fields", () => {
  const s = toState(fullPayload())
  assert.deepEqual(s.missing, [])
  assert.equal(s.gold, 42)
  assert.equal(s.level, 7)
  assert.equal(s.hp, 55)
  assert.equal(s.stage, 4)
  assert.equal(s.shop[0].id, "B")
})

test("a payload without a shop reports shop as missing and leaves the shop null", () => {
  const p = fullPayload()
  delete p.shop
  const s = toState(p)
  assert.deepEqual(s.missing, ["shop"])
  assert.equal(s.shop, null)
})

test("an empty payload lists every field it lacks and does not hide them as zeros", () => {
  const s = toState({})
  assert.deepEqual(s.missing, ["gold", "level", "hp", "stage", "shop"])
})

test("a payload with no gold or level gives null for both, not 0 or 1", () => {
  const s = toState({ activePlayer: { championStats: { currentHealth: 40 } }, gameData: { round: 3 }, shop: [null, null, null, null, null] })
  assert.equal(s.gold, null)
  assert.equal(s.level, null)
  assert.ok(s.missing.includes("gold") && s.missing.includes("level"))
})

test("the coach flags a missing level and makes no xp or roll on it", async () => {
  const p = { activePlayer: { currentGold: 50, championStats: { currentHealth: 40 } }, gameData: { round: 3 }, shop: [{ id: "DA_18_Varus", cost: 3, copiesOwned: 0, priority: 5 }, null, null, null, null] }
  const src = { kind: "fake", read: async () => toState(p) }
  const record = await createCoach({ source: src }).tick()
  assert.equal(record.state.hudLevelUnknown, true)
  assert.notEqual(record.decision.action, 2)
  assert.notEqual(record.decision.action, 3)
  assert.equal(record.reason.factors.level, null)
})

test("hp of 0 is kept, not replaced by the fallback", () => {
  const p = fullPayload()
  p.activePlayer.championStats.currentHealth = 0
  assert.equal(toState(p).hp, 0)
})

test("the coach reports missing fields in status and in the reason text", async () => {
  const src = { kind: "fake", read: async () => ({ ...toState({ activePlayer: { currentGold: 10, level: 5, championStats: { currentHealth: 40 } }, gameData: { round: 3 } }) }) }
  const coach = createCoach({ source: src })
  const record = await coach.tick()
  assert.deepEqual(coach.getState().source.missing, ["shop"])
  assert.match(record.reason.text, /thiếu trường từ nguồn: shop/)
  assert.ok(record.reason.caveats.some((c) => c.includes("thiếu trường từ nguồn")))
  assert.equal("missing" in record.state, false)
})

test("capture source replays raw payloads through toState and loops", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-cap-"))
  const file = path.join(dir, "c.jsonl")
  const a = fullPayload()
  const b = fullPayload()
  b.activePlayer.currentGold = 9
  fs.writeFileSync(file, JSON.stringify({ ts: "x", payload: a }) + "\n" + JSON.stringify({ ts: "y", payload: b }) + "\n" + '{"torn')
  const src = captureSource(file)
  assert.equal(src.kind, "capture")
  assert.equal(src.frameCount, 2)
  assert.equal((await src.read()).gold, 42)
  assert.equal((await src.read()).gold, 9)
  assert.equal((await src.read()).gold, 42)
})

test("capture writer appends only when the payload changes", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-capw-"))
  const file = path.join(dir, "out", "c.jsonl")
  const payloads = [fullPayload(), fullPayload(), { activePlayer: { currentGold: 1 } }]
  let i = 0
  const cap = startCapture({ outFile: file, pollMs: 5, fetchPayload: async () => payloads[Math.min(i++, payloads.length - 1)], write: () => {} })
  await new Promise((r) => setTimeout(r, 80))
  cap.stop()
  const lines = fs.readFileSync(file, "utf8").trim().split("\n")
  assert.equal(lines.length, 2)
  assert.ok(JSON.parse(lines[0]).payload.shop)
})
