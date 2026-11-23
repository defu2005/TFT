import test from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import path from "node:path"
import os from "node:os"
import { createStandaloneSource } from "./standaloneSource.js"

test("standaloneSource handles missing files gracefully", async () => {
  const fakeEog = path.join(os.tmpdir(), `nonexistent-eog-${Date.now()}.json`)
  const fakeHud = path.join(os.tmpdir(), `nonexistent-hud-${Date.now()}.json`)
  const src = createStandaloneSource({ eogPath: fakeEog, hudPath: fakeHud })
  const state = await src.read()

  assert.equal(src.kind, "standalone")
  assert.equal(state.hp, 100)
  assert.ok(state.missing.includes("snapshot"))
  assert.ok(state.missing.includes("shop"))
  // Without a HUD, gold and level are estimates: they must be reported as missing, not passed as read values.
  assert.ok(state.missing.includes("gold"))
  assert.ok(state.missing.includes("level"))
})

test("standaloneSource parses snapshot to extract player HP and board pieces", async () => {
  const tmpDir = os.tmpdir()
  const eogPath = path.join(tmpDir, `test-eog-${Date.now()}.json`)
  const snapshotData = {
    statsBlock: {
      gameLengthSeconds: 430,
      players: [
        {
          riotIdGameName: "lactruysanhan",
          health: 84,
          isInteractable: true,
          boardPieces: [
            { championName: "DA_18_Ornn", starLevel: 1, price: 1 },
            { championName: "DA_Karma18", starLevel: 1, price: 1 },
            { championName: "DA_18_Sentry", starLevel: 1, price: 1 },
            { championName: "DA_18_Rakan", starLevel: 2, price: 1 },
            { championName: "DA_18_Varus", starLevel: 1, price: 1 }
          ]
        }
      ]
    }
  }
  fs.writeFileSync(eogPath, JSON.stringify(snapshotData), "utf8")

  const src = createStandaloneSource({ eogPath, hudPath: "/nonexistent", playerName: "lactruysanhan" })
  const state = await src.read()

  assert.equal(state.hp, 84)
  assert.equal(state.level, 5) // 5 pieces on board -> level 5
  assert.equal(state.stage, 4) // 430s is stage 4
  assert.equal(state.board.length, 5)
  assert.ok(!state.missing.includes("snapshot"))
  assert.ok(state.missing.includes("shop"))

  fs.unlinkSync(eogPath)
})

test("standaloneSource merges HUD reader output for exact gold, level, and shop", async () => {
  const tmpDir = os.tmpdir()
  const eogPath = path.join(tmpDir, `test-eog2-${Date.now()}.json`)
  const hudPath = path.join(tmpDir, `test-hud2-${Date.now()}.json`)

  const snapshotData = {
    statsBlock: {
      gameLengthSeconds: 600,
      players: [
        {
          riotIdGameName: "lactruysanhan",
          health: 72,
          isInteractable: true,
          boardPieces: [
            { championName: "DA_18_Ornn", starLevel: 2, price: 1 } // 3 copies owned
          ]
        }
      ]
    }
  }

  const hudData = {
    gold: 52,
    level: 7,
    shop: [
      { id: "DA_18_Ornn", cost: 1, priority: 5 },
      { id: "DA_18_Varus", cost: 1, priority: 0 },
      null,
      null,
      null
    ]
  }

  fs.writeFileSync(eogPath, JSON.stringify(snapshotData), "utf8")
  fs.writeFileSync(hudPath, JSON.stringify(hudData), "utf8")

  const src = createStandaloneSource({ eogPath, hudPath, playerName: "lactruysanhan" })
  const state = await src.read()

  assert.equal(state.gold, 52)
  assert.equal(state.level, 7)
  assert.equal(state.hp, 72)
  assert.equal(state.shop[0].id, "DA_18_Ornn")
  assert.equal(state.shop[0].copiesOwned, 3) // 2-star Ornn has 3 copies
  assert.equal(state.missing.length, 0)

  fs.unlinkSync(eogPath)
  fs.unlinkSync(hudPath)
})
