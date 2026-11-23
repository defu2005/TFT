import assert from "node:assert/strict"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import test from "node:test"
import { createApp, loadConfig, parseRules } from "./app.js"

const SET17 = path.join(import.meta.dirname, "data", "set17.json")

function replayConfig(extra) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-app-"))
  return loadConfig({ TFT_SOURCE: "replay", TFT_LOG: path.join(dir, "d.jsonl"), ...extra })
}

test("the auto line needs a set file", () => {
  assert.throws(() => createApp(replayConfig({ TFT_AUTO_LINE: "1" })), /TFT_SET_FILE/)
})

test("the auto line is off by default and on with a set file", () => {
  assert.equal(createApp(replayConfig({})).coach.getState().autoLine, false)
  assert.equal(createApp(replayConfig({ TFT_AUTO_LINE: "1", TFT_SET_FILE: SET17 })).coach.getState().autoLine, true)
})

test("the auto line on the real set file buys a shop unit that shares a trait with the board", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-real-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [
        {
          level: 7,
          gold: 20,
          hp: 80,
          stage: 3,
          target: null,
          shop: [{ id: "TFT17_Briar", cost: 1, copiesOwned: 0, priority: 0 }, null, null, null, null],
          board: [{ id: "TFT17_Belveth", star: 1 }],
        },
      ],
    }),
  )
  const config = replayConfig({ TFT_REPLAY: fixture, TFT_AUTO_LINE: "1", TFT_SET_FILE: SET17 })
  const { coach } = createApp(config)
  const record = await coach.tick()
  assert.equal(record.decision.action, "buy")
  assert.equal(record.decision.slot, 0)
  assert.ok(record.reason.factors.autoLine.TFT17_Briar >= 1)
})

test("TFT_RULES parses names into flags, rejects unknown names, and is null when unset", () => {
  assert.equal(parseRules(undefined), null)
  assert.equal(parseRules(""), null)
  assert.deepEqual(parseRules("keepInterest, guideLevels"), { keepInterest: true, earlyLevel: false, guideLevels: true })
  assert.throws(() => parseRules("keepInterest,nope"), /nope/)
})

// One frame, no target: rule 3 pin state (level 7, stage 4, 50 gold, empty shop).
function guideFrame() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-rules-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({ frames: [{ level: 7, gold: 50, hp: 80, stage: 4, target: null, shop: [null, null, null, null, null] }] }),
  )
  return fixture
}

test("with TFT_RULES unset the tick levels up and no rules are reported", async () => {
  const { coach } = createApp(replayConfig({ TFT_REPLAY: guideFrame() }))
  const record = await coach.tick()
  assert.equal(record.decision.action, "xp")
  assert.equal(record.reason.factors.rules, undefined)
  assert.equal(coach.getState().rules, null)
})

test("with TFT_RULES=guideLevels the tick holds and reports the rule", async () => {
  const { coach } = createApp(replayConfig({ TFT_REPLAY: guideFrame(), TFT_RULES: "guideLevels" }))
  const record = await coach.tick()
  assert.equal(record.decision.action, "hold")
  assert.equal(record.reason.factors.rules.guideLevels, true)
  assert.equal(coach.getState().rules.guideLevels, true)
})
