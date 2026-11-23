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
