import assert from "node:assert/strict"
import test from "node:test"
import { projectGold } from "./economy.js"
import { targetBudgetRolls, copiesToNextStar } from "./decide.js"
import { atLeastKOfSlots } from "./odds.js"

test("gold projection matches the research examples (§14.1)", () => {
  assert.deepEqual(projectGold(50, 3), [60, 70, 80])
  assert.deepEqual(projectGold(30, 3), [38, 46, 55])
})

test("interest in the projection is capped at 5", () => {
  assert.deepEqual(projectGold(200, 1), [210])
})

test("copies to the next star: 3 for none owned, 2 for one, 1 for two, 3 again after a 2-star", () => {
  assert.equal(copiesToNextStar(0), 3)
  assert.equal(copiesToNextStar(1), 2)
  assert.equal(copiesToNextStar(2), 1)
  assert.equal(copiesToNextStar(3), 3)
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
