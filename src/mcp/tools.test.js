import assert from "node:assert/strict"
import test from "node:test"
import fs from "node:fs"
import { registerTools } from "./tools.js"
import { buildProfile } from "../data/profileFile.js"
import { hitChance } from "../engine/odds.js"

// Captures the handlers registerTool() receives, so the tools can be called without a transport.
function fakeServer() {
  const handlers = new Map()
  const configs = new Map()
  return {
    handlers,
    configs,
    registerTool(name, config, handler) {
      handlers.set(name, handler)
      configs.set(name, config)
    },
  }
}

const coach = { getState: () => ({}), recent: () => [] }
const candidate = JSON.parse(fs.readFileSync(new URL("../data/profiles/set18.candidate.json", import.meta.url), "utf8"))

test("tft_hit_chance uses the profile when one is given and the default table when not", async () => {
  const profile = buildProfile(candidate, "16.20")
  const withProfile = fakeServer()
  registerTools(withProfile, { coach, profile })
  const plain = fakeServer()
  registerTools(plain, { coach })
  const args = { level: 8, cost: 4, copiesLeft: 10, champsAtCost: 14 }
  const viaProfile = JSON.parse((await withProfile.handlers.get("tft_hit_chance")(args)).content[0].text)
  const viaDefault = JSON.parse((await plain.handlers.get("tft_hit_chance")(args)).content[0].text)
  assert.equal(viaProfile.hitChance, Math.round(hitChance(8, 4, 10, 14, profile) * 1000) / 1000)
  assert.notEqual(viaProfile.hitChance, viaDefault.hitChance)
  assert.match(viaProfile.caveat, /hồ sơ/)
})

test("tft_rules reports the profile tables and the profile when one is given", async () => {
  const profile = buildProfile(candidate, "16.20")
  const server = fakeServer()
  registerTools(server, { coach, profile })
  const body = JSON.parse((await server.handlers.get("tft_rules")({})).content[0].text)
  assert.deepEqual(body.shopOdds[8], candidate.patches[0].shopOdds["8"])
  assert.equal(body.profile.applied, "16.20")
})

const { z } = await import("zod")
const S18_PROFILE = () => buildProfile(candidate, "16.20")

// A state where the U9 keepInterest rule flips the action: 51 gold, no free rolls, a wanted target.
const ROLL_STATE = { level: 8, gold: 51, hp: 80, stage: 5, shop: [null, null, null, null, null], target: { id: "Z", cost: 1, copiesLeft: 30, priority: 5, champsAtCost: 1 } }

test("tft_evaluate_state changes its action when the keepInterest rule is passed", async () => {
  const plain = fakeServer()
  registerTools(plain, { coach, rules: null, profile: null })
  const ruled = fakeServer()
  registerTools(ruled, { coach, rules: { keepInterest: true, earlyLevel: false, guideLevels: false }, profile: null })
  const without = JSON.parse((await plain.handlers.get("tft_evaluate_state")(ROLL_STATE)).content[0].text)
  const withRule = JSON.parse((await ruled.handlers.get("tft_evaluate_state")(ROLL_STATE)).content[0].text)
  assert.equal(without.action, "roll")
  assert.equal(withRule.action, "hold")
  assert.deepEqual(withRule.factors.rules, { keepInterest: true, earlyLevel: false, guideLevels: false })
})

test("tft_evaluate_state carries the profile caveats and factor when a profile is given", async () => {
  const profile = S18_PROFILE()
  const server = fakeServer()
  registerTools(server, { coach, rules: null, profile })
  const body = JSON.parse((await server.handlers.get("tft_evaluate_state")(ROLL_STATE)).content[0].text)
  assert.equal(body.factors.profile.applied, "16.20")
  for (const c of profile.caveats) assert.ok(body.caveats.includes(c), c)
})

test("tft_rules returns the guide level table when guideLevels is on", async () => {
  const server = fakeServer()
  registerTools(server, { coach, rules: { keepInterest: false, earlyLevel: false, guideLevels: true }, profile: null })
  const body = JSON.parse((await server.handlers.get("tft_rules")({})).content[0].text)
  assert.deepEqual(body.levelByStage, [0, 2, 4, 6, 7, 8, 9, 9])
  assert.equal(body.maxCost, 5)
})

test("tool input schemas take the cost bound from the profile, not a fixed 5", () => {
  const plain = fakeServer()
  registerTools(plain, { coach })
  const wide = fakeServer()
  registerTools(wide, { coach, profile: { ...S18_PROFILE(), maxCost: 7 } })
  const cfgPlain = plain.configs.get("tft_hit_chance").inputSchema
  const cfgWide = wide.configs.get("tft_hit_chance").inputSchema
  assert.equal(z.object(cfgPlain).safeParse({ level: 8, cost: 6, copiesLeft: 5 }).success, false)
  assert.equal(z.object(cfgWide).safeParse({ level: 8, cost: 6, copiesLeft: 5 }).success, true)
})

test("tft_evaluate_state still accepts level 11 when the profile's odds table is shorter", () => {
  const short = { ...S18_PROFILE(), shopOdds: S18_PROFILE().shopOdds.slice(0, 9) }
  const server = fakeServer()
  registerTools(server, { coach, profile: short })
  const schema = z.object(server.configs.get("tft_evaluate_state").inputSchema)
  assert.equal(schema.safeParse({ ...ROLL_STATE, level: 11 }).success, true)
})

test("tft_evaluate_state takes a null price and the HUD flags, and never buys the null-price slot", async () => {
  const server = fakeServer()
  registerTools(server, { coach, rules: null, profile: null })
  const state = {
    level: 7,
    gold: 0,
    hp: 80,
    stage: 3,
    hudGoldUnknown: true,
    shopUnknownSlots: [1],
    shop: [{ id: "DA_18_Ornn", cost: 1, price: null, copiesOwned: 0, priority: 1 }, null, null, null, null],
  }
  const out = JSON.parse((await server.handlers.get("tft_evaluate_state")(state)).content[0].text)
  assert.notEqual(out.action, "buy")
  assert.equal(out.action, "hold")
})
