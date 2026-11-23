import assert from "node:assert/strict"
import test from "node:test"
import { decide, BUY, HOLD, XP, SELL } from "./decide.js"
import { hitChance } from "./odds.js"
import { POOL_COPIES } from "../data/rules.js"
import { explain } from "./reason.js"

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

test("a unit with 9 copies (3 sao) is not bought again", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0 }
  const trace = []
  decide(
    {
      level: 7,
      gold: 40,
      hp: 80,
      stage: 4,
      shop: [{ id: "core", cost: 3, copiesOwned: 9, priority: 5 }, null, null, null, null],
      target: null,
    },
    out,
    trace,
  )
  assert.equal(out.action, HOLD)
  const entry = trace.find((c) => c.action === "buy" && c.slot === 0)
  assert.match(entry.note, /3 sao/)
})

test("a unit with 3 copies scores with priority times owned times odds, minus interest", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0 }
  const trace = []
  decide(
    {
      level: 7,
      gold: 40,
      hp: 80,
      stage: 4,
      shop: [null, { id: "core", cost: 3, copiesOwned: 3, priority: 5 }, null, null, null],
      target: null,
    },
    out,
    trace,
  )
  const entry = trace.find((c) => c.action === "buy" && c.slot === 1)
  const expected = 5 * 4 * (0.4 + entry.hit) - entry.interestLoss * 0.35
  assert.ok(Math.abs(entry.score - expected) < 1e-9)
})

const CORE = (shop) => ({ level: 7, gold: 40, hp: 80, stage: 4, shop: [shop, null, null, null, null], target: null })

test("owned copies include the board and bench, not only copiesOwned", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0 }
  const trace = []
  decide(
    {
      ...CORE({ id: "core", cost: 3, copiesOwned: 0, priority: 5 }),
      board: [{ id: "core", star: 2 }],
      bench: [{ id: "core", star: 1 }, null],
    },
    out,
    trace,
  )
  const entry = trace.find((c) => c.action === "buy" && c.slot === 0)
  assert.equal(entry.copiesOwned, 4)
  assert.equal(entry.copiesLeft, POOL_COPIES[3] - 4)
})

test("copies held by other players are subtracted from the pool", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0 }
  const trace = []
  const state = CORE({ id: "core", cost: 3, copiesOwned: 1, priority: 5, takenByOthers: 6 })
  decide(state, out, trace)
  assert.equal(out.action, BUY)
  const entry = trace.find((c) => c.action === "buy" && c.slot === 0)
  assert.equal(entry.copiesLeft, POOL_COPIES[3] - 7)
  assert.equal(entry.copiesSource, "pool - copiesOwned - takenByOthers")
  assert.equal(explain(state, out, trace).caveats.length, 1)
})

test("a raw board entry without an id does not change copiesOwned", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0 }
  const trace = []
  decide(
    { ...CORE({ id: "core", cost: 3, copiesOwned: 3, priority: 5 }), board: [{ championName: "core", starLevel: 2 }] },
    out,
    trace,
  )
  const entry = trace.find((c) => c.action === "buy" && c.slot === 0)
  assert.equal(entry.copiesOwned, 3)
})

const SELL_BENCH = [
  { id: "x", star: 1, sellValue: 1 },
  { id: "y", star: 1, sellValue: 3 },
]

test("a full bench blocks the buy and sells the most valuable bench unit that is not in the line", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
  const trace = []
  const state = { ...CORE({ id: "core", cost: 3, copiesOwned: 0, priority: 5 }), bench: SELL_BENCH }
  decide(state, out, trace)
  assert.equal(out.action, SELL)
  assert.equal(out.bench, 1)
  assert.equal(out.slot, -1)
  const buy = trace.find((c) => c.action === "buy" && c.slot === 0)
  assert.match(buy.note, /bench đầy/)
  assert.equal(out.score, buy.score)
  const sell = trace.find((c) => c.action === "sell" && c.bench === 1)
  assert.equal(sell.makesRoomFor, "core")
})

test("a buy that completes a 3-star is not blocked by a full bench", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
  decide({ ...CORE({ id: "core", cost: 3, copiesOwned: 2, priority: 5 }), bench: SELL_BENCH }, out)
  assert.equal(out.action, BUY)
  assert.equal(out.slot, 0)
  assert.equal(out.bench, -1)
})

test("a full bench with nothing sellable holds and names the reasons", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
  const trace = []
  const state = {
    ...CORE({ id: "core", cost: 3, copiesOwned: 0, priority: 5 }),
    bench: [
      { id: "a", star: 1, priority: 4, sellValue: 2 },
      { id: "b", star: 1 },
    ],
  }
  decide(state, out, trace)
  assert.equal(out.action, HOLD)
  const sells = trace.filter((c) => c.action === "sell")
  assert.match(sells[0].note, /line/)
  assert.match(sells[1].note, /sellValue/)
  assert.match(explain(state, out, trace).text, /bench đầy/)
})

test("a free bench slot lets the buy go ahead", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
  decide({ ...CORE({ id: "core", cost: 3, copiesOwned: 0, priority: 5 }), bench: [null, { id: "x", star: 1, sellValue: 1 }] }, out)
  assert.equal(out.action, BUY)
})

test("without bench data the engine buys and records that the bench is unknown", () => {
  const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
  const trace = []
  decide(CORE({ id: "core", cost: 3, copiesOwned: 0, priority: 5 }), out, trace)
  assert.equal(out.action, BUY)
  assert.match(trace.find((c) => c.action === "sell").note, /không có dữ liệu bench/)
})
