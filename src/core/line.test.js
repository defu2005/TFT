import assert from "node:assert/strict"
import test from "node:test"
import { createCoach, hashState } from "./coach.js"

const snapshot = () => ({
  level: 7,
  gold: 20,
  hp: 50,
  stage: 3,
  shop: [{ id: "A", cost: 1, copiesOwned: 0, priority: 0 }, null, null, null, null],
  target: null,
})

function fakeSource() {
  return { kind: "fake", read: async () => snapshot() }
}

test("a unit in the line is bought after setLine; the source array is not changed", async () => {
  const coach = createCoach({ source: fakeSource() })
  await coach.tick()
  assert.notEqual(coach.getState().decision.action, "buy")

  coach.setLine("A", 5)
  const record = await coach.tick()
  assert.equal(record.decision.action, "buy")
  assert.equal(record.decision.slot, 0)
  assert.equal(coach.getState().lines.A, 5)
})

test("a target's copies do not apply to other units in the shop", async () => {
  const src = {
    kind: "fake",
    read: async () => ({
      level: 7,
      gold: 20,
      hp: 50,
      stage: 3,
      shop: [
        { id: "A", cost: 1, copiesOwned: 0, priority: 5 },
        { id: "B", cost: 1, copiesOwned: 0, priority: 5 },
        null,
        null,
        null,
      ],
      target: null,
    }),
  }
  const coach = createCoach({ source: src })
  coach.setTarget({ id: "A", cost: 1, copiesLeft: 40, priority: 1, champsAtCost: 13 })
  const record = await coach.tick()
  const candidates = record.reason.candidates.filter((c) => c.action === "buy")
  const a = candidates.find((c) => c.unit === "A")
  const b = candidates.find((c) => c.unit === "B")
  assert.equal(a.copiesSource, "target")
  assert.notEqual(b.copiesSource, "target")
  assert.notEqual(b.copiesLeft, 40)
})

test("a target change alone changes the state hash", () => {
  const base = snapshot()
  const withTarget = { ...base, target: { id: "T", cost: 2, copiesLeft: 10, priority: 3, champsAtCost: 13 } }
  assert.notEqual(hashState(base), hashState(withTarget))
})
