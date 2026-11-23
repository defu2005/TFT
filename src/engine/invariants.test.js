import assert from "node:assert/strict"
import test from "node:test"
import fs from "node:fs"
import { decide, actionName, BUY, SELL, ROLL, HOLD } from "./decide.js"
import { buildProfile } from "../data/profileFile.js"

const ALL_RULES = { keepInterest: true, earlyLevel: true, guideLevels: true }

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
    rnd() < 0.4
      ? null
      : {
          id: rnd() < 0.7 ? "Z" : pick(IDS),
          cost: int(1, 5),
          copiesLeft: int(0, 20),
          priority: int(2, 5),
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
  if (rnd() < 0.3) state.freeRolls = int(0, 3)
  if (rnd() < 0.5) state.board = Array.from({ length: int(0, 6) }, () => ({ id: pick(IDS), star: int(1, 2) }))
  return state
}

function checkInvariants(rules, profile = null, record = null) {
  const rnd = mulberry32(20261123)
  const counts = { hold: 0, buy: 0, xp: 0, roll: 0, sell: 0 }
  for (let n = 0; n < 2000; n++) {
    const state = makeState(rnd)
    const where = () => JSON.stringify(state)
    const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
    const trace = []
    decide(state, out, trace, rules, profile)
    const plain = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
    decide(state, plain, null, rules, profile)
    if (record) record.push([out.action, out.slot, out.bench])

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
    counts[actionName(out.action)]++
    if (out.action === HOLD) {
      for (const c of trace) {
        if (c.action === "buy" && c.score > 0 && c.note === "") assert.fail(`HOLD while a buy is available: ${where()}`)
        if (c.action === "sell") assert.ok(!(c.score > 0), `HOLD while a sell is available: ${where()}`)
        if (c.action === "xp") assert.ok(c.score <= 0.5, `HOLD while xp is above threshold: ${where()}`)
        if (c.action === "roll") assert.ok(c.score <= 0.45, `HOLD while roll is above threshold: ${where()}`)
      }
    }
    if (out.action === ROLL) {
      const roll = trace.find((c) => c.action === "roll")
      for (const c of trace) {
        if (c.action !== "buy" || !(c.score > 0) || c.note !== "") continue
        assert.ok(!(state.gold - c.cost >= roll.needs), `ROLL while a wanted affordable buy remains: ${where()}`)
      }
    }
    if (out.action === ROLL && state.target) {
      const inShop = state.shop?.some((u) => u && u.id === state.target.id)
      assert.ok(!inShop, `ROLL while target is in the shop: ${where()}`)
    }
  }
  return counts
}

test("engine invariants hold on 2,000 seeded states", () => {
  const counts = checkInvariants(null)
  for (const [name, count] of Object.entries(counts)) {
    assert.ok(count >= 20, `${name} occurred ${count} times, need at least 20`)
  }
  console.log("action counts", JSON.stringify(counts))
})

test("engine invariants hold on the same 2,000 states with all U9 rules on", () => {
  const counts = checkInvariants(ALL_RULES)
  console.log("action counts (all U9 rules on)", JSON.stringify(counts))
})

test("engine invariants hold on the same 2,000 states under the Set 18 candidate profile; differences from default are printed", () => {
  const file = JSON.parse(fs.readFileSync(new URL("../data/profiles/set18.candidate.json", import.meta.url), "utf8"))
  const profile = buildProfile(file, "16.20")
  const defaultRecord = []
  const candRecord = []
  checkInvariants(null, null, defaultRecord)
  const counts = checkInvariants(null, profile, candRecord)
  const differ = defaultRecord.filter((d, i) => d[0] !== candRecord[i][0] || d[1] !== candRecord[i][1] || d[2] !== candRecord[i][2]).length
  console.log("action counts (candidate profile)", JSON.stringify(counts), "differ from default", differ, "of 2000")
})


// HUD unknown-field properties over the same seeded states (rules off and all U9 rules on).
function withUnit(state, f) {
  return { ...state, shop: state.shop?.map((u) => (u ? f(u) : u)) ?? state.shop }
}

function decideOf(state, rules) {
  const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
  decide(state, out, null, rules, null)
  return out
}

for (const [label, rules] of [["rules off", null], ["all U9 rules on", ALL_RULES]]) {
  test(`HUD fields: price equal to the tier decides as before, and a null price is never bought (${label})`, () => {
    const rnd = mulberry32(20261124)
    for (let n = 0; n < 2000; n++) {
      const state = makeState(rnd)
      const same = withUnit(state, (u) => ({ ...u, price: u.cost }))
      const a = decideOf(state, rules)
      const b = decideOf(same, rules)
      assert.deepEqual([b.action, b.slot, b.score], [a.action, a.slot, a.score], `state ${n}`)
      const nulled = withUnit(state, (u) => ({ ...u, price: null }))
      assert.notEqual(decideOf(nulled, rules).action, BUY, `null price bought in state ${n}`)
    }
  })

  test(`HUD fields: unknown gold never buys, rolls or levels; unknown level never levels or rolls (${label})`, () => {
    const rnd = mulberry32(20261125)
    for (let n = 0; n < 2000; n++) {
      const state = makeState(rnd)
      const noGold = decideOf({ ...state, hudGoldUnknown: true }, rules)
      assert.ok(![BUY, ROLL, 2].includes(noGold.action), `unknown gold acted in state ${n}: ${noGold.action}`)
      const noLevel = decideOf({ ...state, hudLevelUnknown: true }, rules)
      assert.ok(![2, ROLL].includes(noLevel.action), `unknown level acted in state ${n}: ${noLevel.action}`)
      // With the level unknown, whatever number is sent must not change the output.
      const a = decideOf({ ...state, level: 1, hudLevelUnknown: true }, rules)
      const b = decideOf({ ...state, level: 11, hudLevelUnknown: true }, rules)
      assert.deepEqual([b.action, b.slot, b.score], [a.action, a.slot, a.score], `level leaked in state ${n}`)
    }
  })
}
