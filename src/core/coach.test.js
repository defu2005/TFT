import assert from "node:assert/strict"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import test from "node:test"
import { createCoach } from "./coach.js"
import { createDecisionLog } from "../log/decisionLog.js"
import { replaySource } from "../ingest/sources.js"

const FIXTURE = path.join(import.meta.dirname, "..", "data", "fixtures", "replay-synthetic.json")

test("replay source loops through the fixture and is labelled synthetic", async () => {
  const src = replaySource(FIXTURE)
  assert.equal(src.synthetic, true)
  const first = await src.read()
  for (let i = 1; i < src.frameCount; i++) await src.read()
  const again = await src.read()
  assert.deepEqual(again, first)
})

test("tick logs changes only and getState never reads the source", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-coach-"))
  const logger = createDecisionLog(path.join(dir, "d.jsonl"))
  const src = replaySource(FIXTURE)
  let reads = 0
  const counted = { kind: "replay", read: () => (reads++, src.read()) }
  const coach = createCoach({ source: counted, logger })

  for (let i = 0; i < 6; i++) await coach.tick()
  assert.equal(reads, 6)
  const logged = fs.readFileSync(path.join(dir, "d.jsonl"), "utf8").trim().split("\n").length
  assert.ok(logged >= 3 && logged <= 6, `logged ${logged}`)

  const before = reads
  for (let i = 0; i < 20; i++) coach.getState()
  assert.equal(reads, before)
})

test("every logged record carries reason, candidates and state", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-coach-"))
  const logger = createDecisionLog(path.join(dir, "d.jsonl"))
  const coach = createCoach({ source: replaySource(FIXTURE), logger })
  await coach.tick()
  const [entry] = logger.readRecent(1)
  assert.equal(entry.schema, 2)
  assert.ok(entry.reason.text.length > 0)
  assert.ok(Array.isArray(entry.reason.candidates))
  assert.equal(entry.source, "engine")
  assert.ok(entry.latencyMs >= 0)
})

test("a failing source keeps the last good decision and reports the error", async () => {
  let fail = false
  const src = replaySource(FIXTURE)
  const flaky = { kind: "live", read: () => (fail ? Promise.reject(new Error("no 2999")) : src.read()) }
  const errors = []
  const coach = createCoach({ source: flaky, onError: (e) => errors.push(e.message) })
  await coach.tick()
  const good = coach.getState().decision
  fail = true
  await coach.tick()
  const s = coach.getState()
  assert.deepEqual(s.decision, good)
  assert.equal(s.source.ok, false)
  assert.equal(s.source.error, "no 2999")
  assert.deepEqual(errors, ["no 2999"])
})

test("setTarget is used on the next tick", async () => {
  const coach = createCoach({ source: replaySource(FIXTURE) })
  coach.setTarget({ cost: 4, copiesLeft: 6, priority: 5, champsAtCost: 12, id: "T" })
  await coach.tick()
  assert.equal(coach.getState().target.id, "T")
  assert.equal(coach.setTarget(null), null)
})

test("a roll with an unread shop slot says the roll discards that slot; a buy on a readable slot does not", async () => {
  const state = {
    level: 3, gold: 4, hp: 20, stage: 4, freeRolls: 0,
    shop: [{ id: "DA_18_Ezreal", cost: 4, copiesOwned: 0, priority: 0, price: 4 }, { id: "DA_18_Xayah", cost: 1, copiesOwned: 0, priority: 0, price: 1 }, null, null, null],
    shopUnknownSlots: [4],
    target: { id: "DA_18_Zed", cost: 1, copiesLeft: 5, champsAtCost: 13, priority: 5 },
  }
  const coach = createCoach({ source: { kind: "live", read: async () => JSON.parse(JSON.stringify(state)) } })
  await coach.tick()
  const roll = coach.getState().reason
  assert.equal(coach.getState().decision.action, "roll")
  assert.match(roll.text, /roll sẽ bỏ ô 5 chưa đọc được/)
  // target already in the shop: the coach buys the readable slot 1, and the roll caveat is absent
  const buyState = { ...state, target: { id: "DA_18_Xayah", cost: 1, copiesLeft: 5, champsAtCost: 13, priority: 5 } }
  const c2 = createCoach({ source: { kind: "live", read: async () => JSON.parse(JSON.stringify(buyState)) } })
  await c2.tick()
  assert.equal(c2.getState().decision.action, "buy")
  assert.equal(c2.getState().decision.slot, 1)
  assert.doesNotMatch(c2.getState().reason.text, /roll sẽ bỏ/)
})

test("a shop with an unread slot is reported as unread, not as a defaulted field; a missing snapshot is a missing source", async () => {
  const state = {
    level: 7, gold: 30, hp: 80, stage: 4, freeRolls: 0,
    shop: [{ id: "DA_18_Ornn", cost: 1, copiesOwned: 0, priority: 1, price: 1 }, null, null, null, null],
    shopUnknownSlots: [4],
    missing: ["shop", "snapshot"],
    target: { id: "DA_18_Ornn", cost: 1, copiesLeft: 9, champsAtCost: 13, priority: 5 },
  }
  const coach = createCoach({ source: { kind: "standalone", read: async () => JSON.parse(JSON.stringify(state)) } })
  await coach.tick()
  const text = coach.getState().reason.text
  assert.match(text, /thiếu trường từ nguồn: shop, snapshot/)
  assert.doesNotMatch(text, /mặc định cho shop/)
  assert.match(text, /ô shop chưa đọc được: ô 5/)
})

function fakeSource(extra = {}) {
  const state = { level: 7, gold: 42, hp: 60, stage: 4, shop: [null, { id: "DA_18_Ornn", cost: 1, copiesOwned: 0, priority: 5 }, null, null, null], target: null, missing: [], ...extra }
  return { kind: "fake", read: async () => ({ ...state }) }
}

test("observed odds row differing from the default is a caveat only; the decision is unchanged", async () => {
  const with_ = await createCoach({ source: fakeSource({ oddsObserved: [16, 30, 43, 10, 1] }) }).tick()
  const without = await createCoach({ source: fakeSource() }).tick()
  assert.equal(with_.reason.factors.oddsMismatch, true)
  assert.ok(with_.reason.caveats.some((c) => c.includes("hàng odds HUD cấp 7 [16, 30, 43, 10, 1]")))
  assert.deepEqual([with_.decision.action, with_.decision.slot], [without.decision.action, without.decision.slot])
  assert.equal(without.reason.factors.oddsMismatch, null)
})

test("observed odds row matching the 18.6 candidate is not a mismatch", async () => {
  const file = JSON.parse(fs.readFileSync(new URL("../data/profiles/set18.candidate.json", import.meta.url), "utf8"))
  const { buildProfile } = await import("../data/profileFile.js")
  const record = await createCoach({ source: fakeSource({ oddsObserved: [16, 30, 43, 10, 1] }), profile: buildProfile(file, "18.6") }).tick()
  assert.equal(record.reason.factors.oddsMismatch, false)
  assert.ok(!record.reason.caveats.some((c) => c.includes("hàng odds HUD")))
})

test("odds mismatch is null when the level is unknown or no row was read", async () => {
  const noLevel = await createCoach({ source: fakeSource({ level: null, hudLevelUnknown: true, oddsObserved: [16, 30, 43, 10, 1] }) }).tick()
  assert.equal(noLevel.reason.factors.oddsMismatch, null)
  const noRow = await createCoach({ source: fakeSource({ oddsObserved: null }) }).tick()
  assert.equal(noRow.reason.factors.oddsMismatch, null)
  // a numeric level flagged unknown must still give no comparison (factors.level is the flag-aware value)
  const flaggedLevel = await createCoach({ source: fakeSource({ level: 7, hudLevelUnknown: true, oddsObserved: [16, 30, 43, 10, 1] }) }).tick()
  assert.equal(flaggedLevel.reason.factors.oddsMismatch, null)
})
