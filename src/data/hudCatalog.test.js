import assert from "node:assert/strict"
import fs from "node:fs"
import path from "node:path"
import test from "node:test"

const read = (f) => JSON.parse(fs.readFileSync(path.join(import.meta.dirname, f), "utf8"))

test("every HUD catalog id exists in set18.json with the same cost", () => {
  const catalog = read("set18-hud.json").champions
  const set = new Map(read("set18.json").champions.map((c) => [c.id, c.cost]))
  const bad = catalog.filter((c) => set.get(c.id) !== c.cost).map((c) => `${c.name}:${c.id}:${c.cost}`)
  assert.deepEqual(bad, [])
  assert.equal(catalog.length, 65)
})

test("every HUD catalog name has a row in the name map", () => {
  const names = new Set(read("set18-hud-names.json").rows.map((r) => r.name))
  const missing = read("set18-hud.json").champions.filter((c) => !names.has(c.name)).map((c) => c.name)
  assert.deepEqual(missing, [])
})
