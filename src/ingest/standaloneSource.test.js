import test from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import path from "node:path"
import os from "node:os"
import { createStandaloneSource } from "./standaloneSource.js"
import { createCoach } from "../core/coach.js"

test("standaloneSource handles missing files gracefully", async () => {
  const fakeEog = path.join(os.tmpdir(), `nonexistent-eog-${Date.now()}.json`)
  const fakeHud = path.join(os.tmpdir(), `nonexistent-hud-${Date.now()}.json`)
  const src = createStandaloneSource({ eogPath: fakeEog, hudPath: fakeHud })
  const state = await src.read()

  assert.equal(src.kind, "standalone")
  assert.equal(state.hp, 100)
  assert.ok(state.missing.includes("snapshot"))
  assert.ok(state.missing.includes("shop"))
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

test("standaloneSource rejects unverified, stale, and offline HUD records", async (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-hud-"))
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }))
  const hudPath = path.join(dir, "hud.json")
  const source = createStandaloneSource({ hudPath, eogPath: path.join(dir, "snapshot.json") })
  const live = {
    hudSchema: 1,
    source: "window",
    set: 18,
    capturedAtMs: Date.now(),
    hudDetected: true,
    gold: 0,
    level: 6,
    shop: null,
  }
  fs.writeFileSync(hudPath, JSON.stringify(live))
  const state = await source.read()
  assert.equal(state.gold, 0)
  assert.equal(state.level, 6)
  assert.ok(state.missing.includes("shop"))
  assert.ok(!state.missing.includes("gold"))

  const rejected = [
    { ...live, source: "video" },
    { ...live, hudDetected: false },
    { ...live, capturedAtMs: Date.now() - 10_000 },
    { ...live, capturedAtMs: Date.now() + 10_000 },
    { hudDetected: true, gold: 24, level: 6, shop: Array(5).fill({ id: "DA_18_Ornn" }) },
  ]
  for (const hud of rejected) {
    fs.writeFileSync(hudPath, JSON.stringify(hud))
    const state = await source.read()
    assert.equal(state.gold, 10)
    assert.equal(state.level, 1)
    assert.equal(state.shop, null)
    assert.ok(["gold", "level", "shop"].every((field) => state.missing.includes(field)))
  }
})

test("coach uses verified slots with observed gold while level and other slots are unknown", async (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-hud-partial-"))
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }))
  const hudPath = path.join(dir, "hud.json")
  const source = createStandaloneSource({ hudPath, eogPath: path.join(dir, "snapshot.json") })
  const coach = createCoach({ source })
  const hud = {
    hudSchema: 2,
    source: "window",
    set: 18,
    capturedAtMs: Date.now(),
    hudDetected: true,
    gold: 55,
    level: null,
    shop: null,
    shopSlots: [null, { id: "DA_18_Ornn", cost: 1 }, null, { id: "DA_18_Varus", cost: 1 }, null],
  }
  fs.writeFileSync(hudPath, JSON.stringify(hud))
  coach.setTarget({ cost: 1, copiesLeft: 30, priority: 10 })
  coach.setLine("DA_18_Ornn", 4)
  const record = await coach.tick()
  assert.equal(record.state.gold, 55)
  assert.equal(record.state.level, null)
  assert.equal(record.reason.factors.level, null)
  assert.deepEqual(record.state.shopUnknownSlots, [0, 2, 4])
  assert.equal(record.known.shop, false)
  assert.equal(record.decision.action, "buy")
  assert.equal(record.decision.slot, 1)
  assert.equal(record.decision.hit, null)
  assert.ok(record.reason.candidates.find((candidate) => candidate.action === "buy" && candidate.slot === 0).unknown)
  assert.ok(record.reason.candidates.filter((candidate) => ["xp", "roll"].includes(candidate.action)).every((candidate) => candidate.score === 0))
  assert.ok(coach.getState().source.missing.includes("level"))
  assert.ok(coach.getState().source.missing.includes("shop"))

  fs.writeFileSync(hudPath, JSON.stringify({ ...hud, gold: null, level: 7 }))
  const missingGold = await coach.tick()
  assert.equal(missingGold.state.gold, null)
  assert.equal(missingGold.state.shop, null)
  assert.equal(missingGold.decision.action, "hold")
  assert.ok(coach.getState().source.missing.includes("gold"))
})

test("observed shop prices gate buying independently of unit tier", async (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-hud-price-"))
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }))
  const hudPath = path.join(dir, "hud.json")
  const coach = createCoach({ source: createStandaloneSource({
    hudPath, eogPath: path.join(dir, "snapshot.json"),
  }) })
  const id = "tft18_rammus"
  coach.setLine(id, 5)
  function publish(price) {
    fs.writeFileSync(hudPath, JSON.stringify({
      hudSchema: 2, source: "window", set: 18, capturedAtMs: Date.now(), hudDetected: true,
      gold: 7, level: 7, shopSlots: [{ id, cost: 3, price }, null, null, null, null],
    }))
  }
  publish(9)
  const expensive = await coach.tick()
  assert.equal(expensive.decision.action, "hold")
  assert.equal(expensive.state.shop[0].price, 9)
  assert.match(expensive.reason.candidates[0].note, /cần 9/)

  publish(null)
  const unreadable = await coach.tick()
  assert.equal(unreadable.decision.action, "hold")
  assert.match(unreadable.reason.candidates[0].note, /chưa đọc được giá/)
  assert.notEqual(unreadable.stateHash, expensive.stateHash)

  publish(0)
  const free = await coach.tick()
  assert.equal(free.decision.action, "buy")
  assert.equal(free.reason.candidates[0].cost, 3)
  assert.equal(free.reason.candidates[0].price, 0)
  assert.ok(free.reason.candidates[0].hit > 0)
})
