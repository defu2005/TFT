import assert from "node:assert/strict"
import test from "node:test"
import { decide, BUY, HOLD, XP } from "./decide.js"
import { hitChance } from "./odds.js"

test("a five-cost unit is impossible in a level 3 shop", () => {
  assert.equal(hitChance(3, 5, 9), 0)
})

test("more copies left raises the hit chance", () => {
  assert.ok(hitChance(8, 4, 10) > hitChance(8, 4, 1))
})

test("buys the highest priority unit the player can afford", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0 }
  decide(
    {
      level: 7,
      gold: 40,
      hp: 80,
      stage: 4,
      shop: [
        { id: "cheap", cost: 1, copiesOwned: 0, priority: 1 },
        { id: "core", cost: 3, copiesOwned: 2, priority: 5, poolCopies: 18 },
        null,
        null,
        null,
      ],
      target: null,
    },
    out,
  )
  assert.equal(out.action, BUY)
  assert.equal(out.slot, 1)
})

test("holds when the shop has nothing in the line", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0 }
  decide(
    {
      level: 6,
      gold: 30,
      hp: 90,
      stage: 3,
      shop: [{ id: "x", cost: 2, copiesOwned: 0, priority: 0 }, null, null, null, null],
      target: null,
    },
    out,
  )
  assert.equal(out.action, HOLD)
})

test("levels when ahead on gold and behind the stage line", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0 }
  decide(
    {
      level: 6,
      gold: 58,
      hp: 80,
      stage: 4,
      shop: [null, null, null, null, null],
      target: null,
    },
    out,
  )
  assert.equal(out.action, XP)
})

test("trace lists every shop slot, xp and roll with the numbers behind them", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0 }
  const trace = []
  decide(
    {
      level: 7,
      gold: 42,
      hp: 55,
      stage: 4,
      shop: [
        { id: "a", cost: 1, copiesOwned: 0, priority: 1 },
        { id: "b", cost: 3, copiesOwned: 2, priority: 5 },
        null,
        null,
        null,
      ],
      target: null,
    },
    out,
    trace,
  )
  const buys = trace.filter((c) => c.action === "buy")
  assert.equal(buys.length, 5)
  assert.equal(buys[1].unit, "b")
  assert.ok(buys[1].hit >= 0 && buys[1].hit <= 1)
  assert.equal(buys[1].copiesSource, "pool - copiesOwned (ước lượng)")
  assert.ok(trace.some((c) => c.action === "xp"))
  assert.ok(trace.some((c) => c.action === "roll" && /không có mục tiêu/.test(c.note)))
})

test("without a trace the decision is the same", () => {
  const state = {
    level: 8,
    gold: 30,
    hp: 25,
    stage: 5,
    shop: [{ id: "d", cost: 2, copiesOwned: 0, priority: 3 }, null, null, null, null],
    target: null,
  }
  const a = decide(state, { action: 0, slot: -1, score: 0, hit: 0 })
  const b = decide(state, { action: 0, slot: -1, score: 0, hit: 0 }, [])
  assert.deepEqual(a, b)
})
