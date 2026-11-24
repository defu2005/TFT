import assert from "node:assert/strict"
import test from "node:test"
import { atLeastKOfSlots, hitChance, hitChanceOverRolls, hitAtLeastKOverRolls, slotChance } from "./odds.js"

// Research document §17.1 inputs: p = 0.024 per slot, 75 slots (15 rolls x 5).
test("k = 1 over slots equals one minus (1-p)^n", () => {
  assert.ok(Math.abs(atLeastKOfSlots(0.024, 75, 1) - (1 - Math.pow(1 - 0.024, 75))) < 1e-12)
})

test("research §17.1 figures, computed (the document prints 53.9% and 26.8%; computed values are 54.0% and 26.9%)", () => {
  const pct = (k) => Math.round(atLeastKOfSlots(0.024, 75, k) * 1000) / 10
  assert.equal(pct(1), 83.8)
  assert.equal(pct(2), 54)
  assert.equal(pct(3), 26.9)
})

test("research §17.1 unseen-target case: p = 0.012, 75 slots, at least one = 59.6% (document prints 59.5%)", () => {
  assert.equal(Math.round(atLeastKOfSlots(0.012, 75, 1) * 1000) / 10, 59.6)
})

test("k = 1 matches hitChanceOverRolls for a real profile row", () => {
  const args = [7, 1, 9, 13]
  for (const rolls of [1, 3, 10]) {
    const a = hitAtLeastKOverRolls(...args, 1, rolls)
    const b = hitChanceOverRolls(...args, rolls)
    assert.ok(Math.abs(a - b) < 1e-12, `rolls ${rolls}: ${a} vs ${b}`)
  }
  assert.ok(Math.abs(slotChance(...args) - (1 - Math.pow(1 - hitChance(...args), 1 / 5))) < 1e-12)
})

test("at least k is monotone in k and zero when k exceeds slots", () => {
  assert.ok(hitAtLeastKOverRolls(7, 1, 9, 13, 2, 5) <= hitAtLeastKOverRolls(7, 1, 9, 13, 1, 5))
  assert.equal(atLeastKOfSlots(0.5, 3, 4), 0)
  assert.equal(hitAtLeastKOverRolls(7, 1, 9, 13, 1, 0), 0)
})
