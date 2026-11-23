import assert from "node:assert/strict"
import test from "node:test"
import { applyTraitOverlay } from "./traitOverlay.js"
import { createSetIndex } from "./autoline.js"

const base = () =>
  createSetIndex({
    champions: [
      { id: "DA_18_Ivern", traits: ["Greenfather"] },
      { id: "DA_18_Kennen", traits: ["Inferno", "Executioner"] },
      { id: "DA_18_Ornn", traits: ["Elderwood", "Defender"] },
    ],
    traits: [
      { name: "Elderwood", breakpoints: [3, 5, 7] },
      { name: "Sprykin", breakpoints: [3, 5, 7] },
      { name: "Greenfather", breakpoints: [1] },
      { name: "Inferno", breakpoints: [2] },
      { name: "Executioner", breakpoints: [2] },
      { name: "Defender", breakpoints: [2] },
    ],
  })

const overlay = (extra = {}) => ({
  set: "18",
  verified: false,
  note: "test",
  champions: { DA_18_Ivern: { add: ["Elderwood"] }, DA_18_Kennen: { add: ["Sprykin"] } },
  ...extra,
})

test("the overlay adds the stated trait and keeps the old ones (add-only)", () => {
  const out = applyTraitOverlay(base(), overlay())
  assert.deepEqual(out.traitsOf.get("DA_18_Ivern"), ["Greenfather", "Elderwood"])
  assert.deepEqual(out.traitsOf.get("DA_18_Kennen"), ["Inferno", "Executioner", "Sprykin"])
  assert.equal(out.applied, 2)
  assert.equal(out.verified, false)
})

test("the overlay does not change the input index", () => {
  const index = base()
  applyTraitOverlay(index, overlay())
  assert.deepEqual(index.traitsOf.get("DA_18_Ivern"), ["Greenfather"])
})

test("a trait the champion already has is not counted twice", () => {
  const out = applyTraitOverlay(base(), overlay({ champions: { DA_18_Ornn: { add: ["Elderwood"] } } }))
  assert.deepEqual(out.traitsOf.get("DA_18_Ornn"), ["Elderwood", "Defender"])
  assert.equal(out.applied, 0)
})

test("unknown keys, missing fields and unknown ids or traits are refused", () => {
  assert.throws(() => applyTraitOverlay(base(), overlay({ extra: 1 })), /trường không rõ "extra"/)
  assert.throws(() => applyTraitOverlay(base(), { ...overlay(), verified: "yes" }), /verified/)
  assert.throws(() => applyTraitOverlay(base(), { ...overlay(), set: undefined }), /set/)
  assert.throws(() => applyTraitOverlay(base(), overlay({ champions: { DA_18_Nobody: { add: ["Elderwood"] } } })), /không có trong file set/)
  assert.throws(() => applyTraitOverlay(base(), overlay({ champions: { DA_18_Ivern: { add: ["Nope"] } } })), /Nope/)
  assert.throws(() => applyTraitOverlay(base(), overlay({ champions: { DA_18_Ivern: { remove: ["Greenfather"] } } })), /remove/)
  assert.throws(() => applyTraitOverlay(base(), overlay({ champions: { DA_18_Ivern: "Elderwood" } })), /object/)
  assert.throws(() => applyTraitOverlay(base(), overlay({ champions: { DA_18_Ivern: { add: "Elderwood" } } })), /phải là mảng/)
  assert.throws(() => applyTraitOverlay(base(), null), /object/)
})
