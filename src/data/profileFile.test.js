import assert from "node:assert/strict"
import fs from "node:fs"
import test from "node:test"
import { decide, ROLL } from "../engine/decide.js"
import { hitChance } from "../engine/odds.js"
import { DEFAULT_PROFILE } from "./profile.js"
import { buildProfile, compareVersions } from "./profileFile.js"

const SHOP_17 = [0, [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [0.75, 0.25, 0, 0, 0], [0.55, 0.3, 0.15, 0, 0], [0.45, 0.33, 0.2, 0.02, 0], [0.3, 0.4, 0.25, 0.05, 0], [0.19, 0.3, 0.4, 0.1, 0.01], [0.15, 0.2, 0.32, 0.3, 0.03], [0.1, 0.17, 0.25, 0.33, 0.15]]
const BASE = { shopOdds: SHOP_17, poolCopies: [0, 30, 25, 18, 10, 9], champsPerCost: [0, 13, 13, 13, 12, 8] }
const fileWith = (patches, extra = {}) => ({ set: "TEST", base: BASE, patches, ...extra })

test("a level 8 overlay changes the hit chance at level 8 and not at level 7", () => {
  const profile = buildProfile(fileWith([{ version: "16.20", shopOdds: { 8: [0.5, 0.2, 0.1, 0.1, 0.1] } }]))
  assert.notEqual(hitChance(8, 1, 10, 13, profile), hitChance(8, 1, 10, 13))
  assert.equal(hitChance(7, 1, 10, 13, profile), hitChance(7, 1, 10, 13))
})

test("a seven-column table gives cost 7 a non-zero hit chance, in the roll decision too", () => {
  const row = [0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.3]
  const profile = buildProfile({
    set: "SEVEN",
    base: { maxCost: 7, shopOdds: [0, row, row, row, row, row, row, row, row, row], poolCopies: [0, 30, 25, 18, 10, 9, 6, 4], champsPerCost: [0, 13, 13, 13, 12, 8, 6, 4] },
  })
  assert.equal(profile.maxCost, 7)
  assert.ok(hitChance(8, 7, 2, 4, profile) > 0)
  assert.equal(hitChance(8, 7, 2, 4), 0)

  const trace = []
  const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
  const state = { level: 8, gold: 30, hp: 20, stage: 5, shop: [null, null, null, null, null], target: { id: "S7", cost: 7, copiesLeft: 2, priority: 5, champsAtCost: 4 } }
  decide(state, out, trace, null, profile)
  assert.equal(out.action, ROLL)
  assert.ok(trace.find((c) => c.action === "roll").hit > 0)
})

test("a row that does not sum to 1 throws", () => {
  assert.throws(() => buildProfile(fileWith([{ version: "16.20", shopOdds: { 8: [0.5, 0.5, 0.5, 0, 0] } }])), /tổng/)
})

test("a null row at a level from 1 up throws, not only at level 0", () => {
  assert.throws(() => buildProfile({ set: "HOLE", base: { ...BASE, shopOdds: [null, [1, 0, 0, 0, 0], null] } }), /level 2/)
})

test("a patch past the end of the table leaves a hole and throws", () => {
  const short = { ...BASE, shopOdds: SHOP_17.slice(0, 10) }
  assert.throws(() => buildProfile({ set: "LONG", base: short, patches: [{ version: "16.20", shopOdds: { 12: [0.2, 0.2, 0.2, 0.2, 0.2] } }] }), /level 10/)
})

test("a table shorter than the default says which top level it reaches", () => {
  const profile = buildProfile({ set: "SHORT", base: { ...BASE, shopOdds: SHOP_17.slice(0, 10) } })
  assert.ok(profile.caveats.some((c) => /level 9/.test(c)))
  assert.equal(hitChance(10, 1, 10, 13, profile), 0)
})

test("misspelt level, cost, or field names throw instead of being dropped", () => {
  assert.throws(() => buildProfile(fileWith([{ version: "16.20", shopOdds: { lvl8: [0.2, 0.2, 0.2, 0.2, 0.2] } }])), /lvl8/)
  assert.throws(() => buildProfile(fileWith([{ version: "16.20", poolCopies: { x2: 20 } }])), /x2/)
  assert.throws(() => buildProfile({ set: "T", base: { ...BASE, shopOdd: SHOP_17 } }), /shopOdd/)
  assert.throws(() => buildProfile(fileWith([{ version: "16.20", shopOddz: {} }])), /shopOddz/)
})

test("a set-level unmodelled list becomes a caveat", () => {
  const profile = buildProfile(fileWith([], { unmodelled: ["augment rounds"] }))
  assert.ok(profile.caveats.some((c) => /augment rounds/.test(c)))
})

test("patch versions compare numerically, so 16.9 comes before 16.20", () => {
  assert.ok(compareVersions("16.9", "16.20") < 0)
  const profile = buildProfile(fileWith([{ version: "16.20", shopOdds: { 8: [0.5, 0.2, 0.1, 0.1, 0.1] } }, { version: "16.9", shopOdds: { 8: [0.2, 0.2, 0.2, 0.2, 0.2] } }]), "16.9")
  assert.deepEqual([...profile.shopOdds[8]], [0.2, 0.2, 0.2, 0.2, 0.2])
})

test("a missing base table falls back to rules.js and says so in the caveats", () => {
  const profile = buildProfile({ set: "PARTIAL", base: { shopOdds: SHOP_17, poolCopies: DEFAULT_PROFILE.poolCopies } })
  assert.ok(profile.caveats.some((c) => /champsPerCost/.test(c)))
})

test("the Set 18 candidate loads: rows 8 and 9 change, every other row equals the default", () => {
  const file = JSON.parse(fs.readFileSync(new URL("./profiles/set18.candidate.json", import.meta.url), "utf8"))
  const profile = buildProfile(file, "16.20")
  for (let level = 1; level < DEFAULT_PROFILE.shopOdds.length; level++) {
    if (level === 8 || level === 9) {
      assert.notDeepEqual([...profile.shopOdds[level]], [...DEFAULT_PROFILE.shopOdds[level]])
    } else {
      assert.deepEqual([...profile.shopOdds[level]], [...DEFAULT_PROFILE.shopOdds[level]], `level ${level}`)
    }
  }
  assert.deepEqual([...profile.poolCopies], [...DEFAULT_PROFILE.poolCopies])
  assert.deepEqual([...profile.champsPerCost], [...DEFAULT_PROFILE.champsPerCost])
  assert.ok(profile.caveats.some((c) => /Reroll Subscription/.test(c)))
})
