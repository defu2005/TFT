import assert from "node:assert/strict"
import test from "node:test"
import { hitChance, hitChanceOverRolls } from "./odds.js"

test("one roll equals the single-shop hit chance, and zero rolls gives 0", () => {
  assert.ok(Math.abs(hitChanceOverRolls(8, 2, 10, 13, 1) - hitChance(8, 2, 10, 13)) < 1e-12)
  assert.equal(hitChanceOverRolls(8, 2, 10, 13, 0), 0)
  assert.equal(hitChanceOverRolls(8, 2, 10, 13, -3), 0)
})

test("more rolls never lower the chance", () => {
  const one = hitChanceOverRolls(7, 3, 9, 13, 1)
  const five = hitChanceOverRolls(7, 3, 9, 13, 5)
  assert.ok(five > one)
  assert.ok(five <= 1)
})
