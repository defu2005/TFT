import assert from "node:assert/strict"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import test from "node:test"
import { createApp, loadConfig } from "./app.js"

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
