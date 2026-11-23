import assert from "node:assert/strict"
import test from "node:test"
import { decide, BUY, SELL, ROLL } from "./decide.js"

// Seeded generator so every run checks the same 2,000 states.
function mulberry32(seed) {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

const IDS = ["A", "B", "C", "T", "D"]

function makeState(rnd) {
  const pick = (arr) => arr[Math.floor(rnd() * arr.length)]
  const int = (lo, hi) => lo + Math.floor(rnd() * (hi - lo + 1))
  const maybe = (p, v) => (rnd() < p ? v : undefined)

  const shop = Array.from({ length: 5 }, () => {
    if (rnd() < 0.3) return null
    return {
      id: pick(IDS),
      cost: maybe(0.9, int(1, 5)),
      copiesOwned: maybe(0.8, int(0, 9)),
      priority: maybe(0.8, int(0, 5)),
    }
  })
  const target =
    rnd() < 0.6
      ? null
      : {
          id: rnd() < 0.5 ? pick(IDS) : "Z",
          cost: int(1, 5),
          copiesLeft: int(0, 20),
          priority: int(0, 5),
          champsAtCost: int(1, 13),
        }
  const state = { level: int(1, 11), gold: int(0, 60), hp: int(0, 100), stage: int(1, 8), shop, target }

  const benchRoll = rnd()
  if (benchRoll < 0.3) {
    // bench absent
  } else if (benchRoll < 0.4) {
    state.bench = []
  } else {
    const len = int(1, 9)
    state.bench = Array.from({ length: len }, () => (rnd() < 0.3 ? null : { id: pick(IDS), star: int(1, 3), priority: maybe(0.5, int(0, 5)), sellValue: maybe(0.7, int(0, 5)) }))
  }
  if (rnd() < 0.5) state.board = Array.from({ length: int(0, 6) }, () => ({ id: pick(IDS), star: int(1, 2) }))
  return state
}

test("engine invariants hold on 2,000 seeded states", () => {
  const rnd = mulberry32(20261123)
  for (let n = 0; n < 2000; n++) {
    const state = makeState(rnd)
    const where = () => JSON.stringify(state)
    const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
    const trace = []
    decide(state, out, trace)
    const plain = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
    decide(state, plain)

    assert.ok(Number.isFinite(out.score), `score not finite: ${where()}`)
    for (const c of trace) {
      if (typeof c.score === "number") assert.ok(Number.isFinite(c.score), `trace score not finite: ${where()}`)
    }
    assert.deepEqual(plain, out, `trace changed the decision: ${where()}`)

    if (out.action === BUY) {
      const unit = state.shop?.[out.slot]
      assert.ok(unit, `BUY on empty slot: ${where()}`)
      assert.ok(unit.cost >= 1 && unit.cost <= state.gold, `BUY not affordable: ${where()}`)
    }
    if (out.action === SELL) {
      const unit = state.bench?.[out.bench]
      assert.ok(unit, `SELL on empty bench slot: ${where()}`)
      assert.equal(typeof unit.sellValue, "number", `SELL without sellValue: ${where()}`)
      assert.ok(!(unit.priority > 0), `SELL of a line unit: ${where()}`)
    }
    if (out.action === ROLL && state.target) {
      const inShop = state.shop?.some((u) => u && u.id === state.target.id)
      assert.ok(!inShop, `ROLL while target is in the shop: ${where()}`)
    }
  }
})
