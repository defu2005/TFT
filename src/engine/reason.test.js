import assert from "node:assert/strict"
import test from "node:test"
import { decide } from "./decide.js"
import { explain, CAVEAT_ODDS } from "./reason.js"

function run(state) {
  const out = { action: 0, slot: -1, score: 0, hit: 0 }
  const trace = []
  decide(state, out, trace)
  return explain(state, out, trace)
}

test("explains a buy with slot, odds and interest, and carries the odds caveat", () => {
  const r = run({
    level: 7,
    gold: 42,
    hp: 55,
    stage: 4,
    shop: [null, { id: "B", cost: 3, copiesOwned: 2, priority: 5 }, null, null, null],
    target: null,
  })
  assert.equal(r.action, "buy")
  assert.match(r.text, /Mua ô 1 \(B, cost 3\)/)
  assert.match(r.text, /xác suất gặp/)
  assert.ok(r.caveats.includes(CAVEAT_ODDS))
  assert.match(r.text, /ước lượng/)
})

test("explains a roll toward the target when HP is low", () => {
  const r = run({
    level: 7,
    gold: 4,
    hp: 20,
    stage: 3,
    shop: [null, null, null, null, null],
    target: { id: "T", cost: 2, copiesLeft: 20, priority: 5, champsAtCost: 13 },
  })
  assert.equal(r.action, "roll")
  assert.match(r.text, /Roll để tìm T/)
  assert.match(r.text, /xác suất gặp/)
})

test("a hold reports the XP and roll scores against their thresholds", () => {
  const r = run({ level: 7, gold: 12, hp: 60, stage: 3, shop: [null, null, null, null, null], target: null })
  assert.equal(r.action, "hold")
  assert.match(r.text, /XP 0 \(ngưỡng 0\.5\)/)
  assert.match(r.text, /Roll 0 \(ngưỡng 0\.45\) — không có mục tiêu/)
})

test("explains an xp purchase against the stage line", () => {
  const r = run({ level: 6, gold: 58, hp: 80, stage: 4, shop: [null, null, null, null, null], target: null })
  assert.equal(r.action, "xp")
  assert.match(r.text, /level 6 dưới mục tiêu 8/)
})

test("a hold names why the shop was skipped", () => {
  const r = run({
    level: 7,
    gold: 12,
    hp: 40,
    stage: 3,
    shop: [{ id: "C", cost: 2, copiesOwned: 0, priority: 0 }, null, null, null, null],
    target: null,
  })
  assert.equal(r.action, "hold")
  assert.match(r.text, /không nằm trong line/)
})

test("candidates carry numeric scores rounded to three places", () => {
  const r = run({ level: 6, gold: 58, hp: 80, stage: 4, shop: [null, null, null, null, null], target: null })
  for (const c of r.candidates) {
    if (typeof c.score === "number") assert.equal(Math.round(c.score * 1000) / 1000, c.score)
  }
})

test("explains a sell that makes room on a full bench", () => {
  const r = run({
    level: 7,
    gold: 40,
    hp: 80,
    stage: 4,
    shop: [{ id: "core", cost: 3, copiesOwned: 0, priority: 5 }, null, null, null, null],
    target: null,
    bench: [
      { id: "x", star: 1, sellValue: 1 },
      { id: "y", star: 1, sellValue: 3 },
    ],
  })
  assert.equal(r.action, "sell")
  assert.match(r.text, /Bán ô bench 1 \(y\) lấy 3 vàng/)
  assert.match(r.text, /mua core/)
})

test("a roll that spans several shops reports the budget chance in the reason", () => {
  const trace = []
  const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
  const state = { level: 8, gold: 30, hp: 80, stage: 5, shop: [null, null, null, null, null], target: { id: "Z", cost: 1, copiesLeft: 30, priority: 5, champsAtCost: 1 } }
  decide(state, out, trace)
  const reason = explain(state, out, trace)
  assert.equal(out.action, 3)
  assert.match(reason.text, /Roll hết 10 lượt/)
})
