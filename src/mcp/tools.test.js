import assert from "node:assert/strict"
import test from "node:test"
import fs from "node:fs"
import { registerTools } from "./tools.js"
import { buildProfile } from "../data/profileFile.js"
import { hitChance } from "../engine/odds.js"

// Captures the handlers registerTool() receives, so the tools can be called without a transport.
function fakeServer() {
  const handlers = new Map()
  return {
    handlers,
    registerTool(name, _config, handler) {
      handlers.set(name, handler)
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
