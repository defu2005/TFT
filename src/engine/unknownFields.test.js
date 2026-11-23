// HUD fields the engine must not read as zero: unknown gold or level, a null price, unknown shop slots.
// Default-off: a state without these fields decides exactly as before (see invariants.test.js).
import assert from "node:assert/strict"
import test from "node:test"
import { decide } from "./decide.js"

const TARGET = { id: "t", cost: 2, copiesLeft: 10, priority: 1, champsAtCost: 13 }
const unit = (extra = {}) => ({ id: "a", cost: 1, copiesOwned: 0, priority: 1, ...extra })
const run = (state) => {
  const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
  const trace = []
  decide(state, out, trace)
  return { out, trace }
}

test("a null price is never bought, even with enough gold", () => {
  const { out, trace } = run({ level: 7, gold: 30, hp: 80, stage: 3, shop: [unit({ price: null }), null, null, null, null], target: null })
  assert.notEqual(out.action, 1)
  assert.ok(trace.some((t) => t.note === "chưa đọc được giá mua"))
})

test("price equal to the tier decides exactly like no price", () => {
  const plain = { level: 7, gold: 30, hp: 80, stage: 3, shop: [unit(), null, null, null, null], target: TARGET }
  const priced = { ...plain, shop: [unit({ price: 1 }), null, null, null, null] }
  const a = run(plain)
  const b = run(priced)
  assert.equal(b.out.action, a.out.action)
  assert.equal(b.out.slot, a.out.slot)
  assert.equal(b.out.score, a.out.score)
})

test("affordability uses the price, not the tier", () => {
  const { out } = run({ level: 7, gold: 3, hp: 80, stage: 3, shop: [unit({ cost: 1, price: 5 }), null, null, null, null], target: null })
  assert.notEqual(out.action, 1)
  const cheaper = run({ level: 7, gold: 3, hp: 80, stage: 3, shop: [unit({ cost: 1, price: 1 }), null, null, null, null], target: null })
  assert.equal(cheaper.out.action, 1)
})

test("unknown gold: no buy, no roll, no xp", () => {
  const state = {
    level: 7,
    gold: 0,
    hp: 80,
    stage: 3,
    hudGoldUnknown: true,
    freeRolls: 2,
    shop: [unit(), null, null, null, null],
    target: TARGET,
  }
  const { out, trace } = run(state)
  assert.equal(out.action, 0)
  assert.ok(trace.some((t) => t.action === "roll" && t.note === "chưa đọc được vàng"))
  assert.equal(trace.find((t) => t.action === "xp").score, 0)
})

test("unknown level: no xp or roll; a buy is still allowed and its hit is null in the trace", () => {
  const state = { level: 0, gold: 30, hp: 80, stage: 3, hudLevelUnknown: true, shop: [unit({ price: 1 }), null, null, null, null], target: TARGET }
  const { out, trace } = run(state)
  assert.equal(out.action, 1)
  assert.equal(trace.find((t) => t.action === "buy" && t.slot === 0).hit, null)
  assert.ok(trace.some((t) => t.action === "roll" && t.note === "chưa đọc được cấp"))
  assert.ok(trace.some((t) => t.action === "xp" && t.note === "chưa đọc được cấp"))
})

test("an unreadable shop slot is named as unknown and never bought", () => {
  const state = { level: 7, gold: 30, hp: 80, stage: 3, shop: [null, null, null, null, null], shopUnknownSlots: [2], target: null }
  const { out, trace } = run(state)
  assert.notEqual(out.action, 1)
  assert.ok(trace.some((t) => t.slot === 2 && t.unknown === true && t.note === "chưa đọc được ô này"))
})

// Price flips, mirroring decide.test.js: same gold, tier 1, only the price differs.
const ROLL_TARGET = { id: "Z", cost: 1, copiesLeft: 30, priority: 5, champsAtCost: 1 }
const ROLL_STATE = (gold, shop, extra = {}) => ({ level: 8, gold, hp: 80, stage: 5, shop, target: ROLL_TARGET, ...extra })

test("a cheap price leaves the roll affordable and the roll is chosen (no flip claimed here)", () => {
  const cheap = run(ROLL_STATE(12, [unit({ id: "a", price: 1 }), null, null, null, null]))
  const dear = run(ROLL_STATE(12, [unit({ id: "a", price: 2 }), null, null, null, null]))
  assert.equal(cheap.out.action, 3)
  assert.equal(dear.out.action, 3)
})

test("a price that lets gold fall below the roll need is not kept", () => {
  const plain = run(ROLL_STATE(31, [unit({ id: "a" }), null, null, null, null]))
  const priced = run(ROLL_STATE(31, [unit({ id: "a", price: 25 }), null, null, null, null]))
  assert.equal(plain.out.action, 1)
  assert.notEqual(priced.out.action, 1)
})
