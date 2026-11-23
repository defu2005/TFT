import assert from "node:assert/strict"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import test from "node:test"
import { hitChance } from "../engine/odds.js"
import { DEFAULT_PROFILE } from "./profile.js"
import { buildProfile, compareVersions } from "./profileFile.js"
import { createApp, loadConfig } from "../app.js"

const SHOP_17 = [0, [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [0.75, 0.25, 0, 0, 0], [0.55, 0.3, 0.15, 0, 0], [0.45, 0.33, 0.2, 0.02, 0], [0.3, 0.4, 0.25, 0.05, 0], [0.19, 0.3, 0.4, 0.1, 0.01], [0.15, 0.2, 0.32, 0.3, 0.03], [0.1, 0.17, 0.25, 0.33, 0.15]]

function fileWith(patches, extra = {}) {
  return { set: "TEST", base: { shopOdds: SHOP_17, poolCopies: [0, 30, 25, 18, 10, 9], champsPerCost: [0, 13, 13, 13, 12, 8] }, patches, ...extra }
}

test("a level 8 overlay changes the hit chance at level 8 and not at level 7", () => {
  const profile = buildProfile(fileWith([{ version: "16.20", shopOdds: { 8: [0.5, 0.2, 0.1, 0.1, 0.1] } }]))
  assert.notEqual(hitChance(8, 1, 10, 13, profile), hitChance(8, 1, 10, 13))
  assert.equal(hitChance(7, 1, 10, 13, profile), hitChance(7, 1, 10, 13))
})

test("a seven-column table gives cost 7 a non-zero hit chance", () => {
  const row = [0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.3]
  const profile = buildProfile({
    set: "SEVEN",
    base: { maxCost: 7, shopOdds: [0, row, row, row, row, row, row, row, row, row], poolCopies: [0, 30, 25, 18, 10, 9, 6, 4], champsPerCost: [0, 13, 13, 13, 12, 8, 6, 4] },
  })
  assert.equal(profile.maxCost, 7)
  assert.ok(hitChance(8, 7, 2, 4, profile) > 0)
  assert.equal(hitChance(8, 7, 2, 4), 0)
})

test("a row that does not sum to 1 throws", () => {
  assert.throws(() => buildProfile(fileWith([{ version: "16.20", shopOdds: { 8: [0.5, 0.5, 0.5, 0, 0] } }])), /tổng/)
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

test("an unmodelled feature becomes a caveat", () => {
  const profile = buildProfile(fileWith([{ version: "16.20", unmodelled: ["augment rounds"] }]))
  assert.ok(profile.caveats.some((c) => /augment rounds/.test(c)))
})

test("the default profile adds no caveats", () => {
  assert.equal(DEFAULT_PROFILE.caveats, undefined)
})

test("a set file reaches the decision through createApp, and TFT_PATCH selects the overlay", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-profile-"))
  const profilePath = path.join(dir, "set.json")
  fs.writeFileSync(profilePath, JSON.stringify(fileWith([{ version: "16.9" }, { version: "16.20", shopOdds: { 8: [0.5, 0.2, 0.1, 0.1, 0.1] } }])))
  const frame = path.join(dir, "frame.json")
  fs.writeFileSync(frame, JSON.stringify({ frames: [{ level: 8, gold: 30, hp: 80, stage: 5, target: null, shop: [{ id: "X", cost: 1, copiesOwned: 0, priority: 1 }, null, null, null, null] }] }))
  const base = { TFT_SOURCE: "replay", TFT_REPLAY: frame, TFT_LOG: path.join(dir, "d.jsonl"), TFT_PROFILE_FILE: profilePath }

  const older = createApp(loadConfig({ ...base, TFT_PATCH: "16.9" }))
  const newer = createApp(loadConfig({ ...base, TFT_PATCH: "16.20" }))
  const a = await older.coach.tick()
  const b = await newer.coach.tick()
  assert.equal(newer.coach.getState().profile.patch, "16.20")
  assert.equal(b.reason.factors.profile.set, "TEST")
  assert.notEqual(a.decision.hit, b.decision.hit)

  assert.throws(() => createApp(loadConfig({ TFT_SOURCE: "replay", TFT_PATCH: "16.20", TFT_LOG: path.join(dir, "e.jsonl") })), /TFT_PROFILE_FILE/)
})
