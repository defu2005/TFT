import test from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import path from "node:path"
import os from "node:os"
import { ramSource } from "./ramSource.js"

test("ramSource returns missing file error when state file does not exist", async () => {
  const fakePath = path.join(os.tmpdir(), `nonexistent-tft-${Date.now()}.json`)
  const src = ramSource(fakePath)
  const state = await src.read()

  assert.equal(src.kind, "ram")
  assert.equal(state.gold, null)
  assert.equal(state.level, null)
  assert.equal(state.hp, 100)
  assert.ok(state.missing.includes("ram-state-file-not-found"))
})

test("ramSource correctly parses live RAM state file", async () => {
  const tmpPath = path.join(os.tmpdir(), `ram-test-${Date.now()}.json`)
  const sampleState = {
    ts: Date.now(),
    gold: 48,
    hp: 82,
    level: 7,
    stage: 3,
    shop: [
      { id: "TFT17_Ahri", cost: 4, copiesOwned: 1, priority: 0 },
      null,
      null,
      null,
      null
    ]
  }
  fs.writeFileSync(tmpPath, JSON.stringify(sampleState), "utf8")

  const src = ramSource(tmpPath)
  const state = await src.read()

  assert.equal(state.gold, 48)
  assert.equal(state.hp, 82)
  assert.equal(state.level, 7)
  assert.equal(state.stage, 3)
  assert.equal(state.shop[0].id, "TFT17_Ahri")
  assert.equal(state.missing.length, 0)

  fs.unlinkSync(tmpPath)
})
