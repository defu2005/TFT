import assert from "node:assert/strict"
import test from "node:test"
import { decide, BUY, HOLD, XP, ROLL, NO_RULES } from "./decide.js"
import { parseRules } from "../app.js"

// Opt-in U9 rules (docs/needs.md). Off by default; each test names the rule it checks.
const empty = [null, null, null, null, null]
const T = { id: "Z", cost: 1, copiesLeft: 30, priority: 5, champsAtCost: 1 }
const ROLL_STATE = (gold, extra = {}) => ({ level: 8, gold, hp: 80, stage: 5, shop: empty, target: T, ...extra })
const run = (state, rules, trace = null) => {
  const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
  decide(state, out, trace, rules)
  return out
}
const KEEP = { ...NO_RULES, keepInterest: true }

test("U9 rule keepInterest: a roll below 52 gold is held when the rule is on", () => {
  const trace = []
  const out = run(ROLL_STATE(51), KEEP, trace)
  assert.equal(out.action, HOLD)
  assert.match(trace.find((c) => c.action === "roll").note, /cần 52/)
})

test("U9 rule keepInterest: 52 gold rolls when the rule is on", () => {
  assert.equal(run(ROLL_STATE(52), KEEP).action, ROLL)
})

test("U9 rule keepInterest: low HP still rolls with 2 gold", () => {
  assert.equal(run(ROLL_STATE(2, { hp: 20 }), KEEP).action, ROLL)
})

test("U9 rule keepInterest: a free roll costs no gold", () => {
  assert.equal(run(ROLL_STATE(0, { freeRolls: 2 }), KEEP).action, ROLL)
})

test("U9 rule earlyLevel: level 3 at stage 2 with 20 gold levels up when the rule is on", () => {
  const state = { level: 3, stage: 2, gold: 20, hp: 80, shop: empty, target: null }
  assert.equal(run(state, { ...NO_RULES, earlyLevel: true }).action, XP)
})

test("U9 rule earlyLevel: level 5 at stage 3 with 20 gold still holds", () => {
  const state = { level: 5, stage: 3, gold: 20, hp: 80, shop: empty, target: null }
  assert.equal(run(state, { ...NO_RULES, earlyLevel: true }).action, HOLD)
})

test("U9 rule guideLevels: level 7 at stage 4 holds when the guide target is 7 (stage 4 opens at 7)", () => {
  const state = { level: 7, stage: 4, gold: 50, hp: 80, shop: empty, target: null }
  assert.equal(run(state, { ...NO_RULES, guideLevels: true }).action, HOLD)
})

test("U9 rule guideLevels: the same state at stage 5 levels up (guide opens at 8)", () => {
  const state = { level: 7, stage: 5, gold: 50, hp: 80, shop: empty, target: null }
  assert.equal(run(state, { ...NO_RULES, guideLevels: true }).action, XP)
})

test("TFT_RULES parses names into flags, rejects unknown names, and is null when unset", () => {
  assert.equal(parseRules(undefined), null)
  assert.equal(parseRules(""), null)
  assert.deepEqual(parseRules("keepInterest, guideLevels"), { keepInterest: true, earlyLevel: false, guideLevels: true })
  assert.throws(() => parseRules("keepInterest,nope"), /nope/)
})
