import assert from "node:assert/strict"
import test from "node:test"
import { projectGold } from "./economy.js"
import { targetBudgetRolls, copiesToNextStar, decide } from "./decide.js"
import { atLeastKOfSlots, hitAtLeastKOverRolls } from "./odds.js"
import { explain } from "./reason.js"

test("gold projection matches the research examples (§14.1)", () => {
  assert.deepEqual(projectGold(50, 3), [60, 70, 80])
  assert.deepEqual(projectGold(30, 3), [38, 46, 55])
})

test("interest in the projection is capped at 5", () => {
  assert.deepEqual(projectGold(200, 1), [210])
})

test("copies to the next star in copy units: 2-star under 3 copies, 3-star from 3 to 8, none at 9", () => {
  assert.equal(copiesToNextStar(0), 3)
  assert.equal(copiesToNextStar(1), 2)
  assert.equal(copiesToNextStar(2), 1)
  assert.equal(copiesToNextStar(3), 6)
  assert.equal(copiesToNextStar(8), 1)
  assert.equal(copiesToNextStar(9), 0)
})

test("targetBudget trace pins the budget, copies needed and the odds for one copy on the bench", () => {
  const bench = [{ id: "T", star: 1, priority: 5, sellValue: 1 }, null, null, null, null, null, null, null, null]
  const state = { level: 7, gold: 30, hp: 80, stage: 5, shop: [null, null, null, null, null], board: [null, null, null, null, null, null, null, null, null], bench, target: { id: "T", cost: 4, copiesLeft: 9, priority: 5, champsAtCost: 13 } }
  const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
  const trace = []
  decide(state, out, trace, { keepInterest: false, earlyLevel: false, guideLevels: false, targetBudget: true })
  const roll = trace.find((t) => t.action === "roll")
  assert.equal(roll.budgeted, true)
  assert.equal(roll.ownedKnown, true)
  assert.equal(roll.copiesNeeded, 2)
  assert.equal(roll.budgetRolls, 6)
  assert.ok(Math.abs(roll.hit - hitAtLeastKOverRolls(7, 4, 9, 13, 2, 6)) < 1e-12)
})

test("the roll reason states the k-copies budget and not the old one-copy figure", () => {
  const state = { level: 7, gold: 30, hp: 80, stage: 5, shop: [null, null, null, null, null], board: [null, null, null, null, null, null, null, null, null], bench: [{ id: "T", star: 1, priority: 5, sellValue: 1 }, null, null, null, null, null, null, null, null], target: { id: "T", cost: 4, copiesLeft: 9, priority: 5, champsAtCost: 13 } }
  const out = { action: 3, slot: -1, score: 0.5, hit: 0, bench: -1 }
  const trace = []
  decide(state, out, trace, { keepInterest: false, earlyLevel: false, guideLevels: false, targetBudget: true })
  out.action = 3 // decide() may hold; this test checks the wording of a roll reason only
  const text = explain(state, out, trace).text
  assert.match(text, /ít nhất 2 bản trong 6 lượt/)
  assert.doesNotMatch(text, /Roll hết/)
})

test("without board or bench the copies needed fall back to 1 and say so", () => {
  const state = { level: 7, gold: 30, hp: 80, stage: 5, shop: [null, null, null, null, null], target: { id: "T", cost: 4, copiesLeft: 9, priority: 5, champsAtCost: 13 } }
  const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
  const trace = []
  decide(state, out, trace, { keepInterest: false, earlyLevel: false, guideLevels: false, targetBudget: true })
  const roll = trace.find((t) => t.action === "roll")
  assert.equal(roll.ownedKnown, false)
  assert.equal(roll.copiesNeeded, 1)
  assert.match(explain(state, { ...out, action: 3, score: 0.5 }, trace).text, /tính cần 1 bản/)
})

test("budget rolls keep the interest reserve and pay for copies needed", () => {
  // Research §26.2 quotes 11 rolls with no reserve; with the default 10-gold reserve it is 6.
  assert.equal(targetBudgetRolls(30, 0, 4, 2, 0), 11)
  assert.equal(targetBudgetRolls(30, 10, 4, 2, 0), 6)
  assert.equal(targetBudgetRolls(5, 10, 4, 2, 0), 0)
  assert.equal(targetBudgetRolls(5, 10, 4, 2, 3), 3)
})

test("P(at least 2 of 55 slots at p=0.02) matches the research value (§26.2, 30.1%)", () => {
  assert.ok(Math.abs(atLeastKOfSlots(0.02, 55, 2) - 0.3012) < 0.0005)
})
