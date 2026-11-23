import assert from "node:assert/strict"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import test from "node:test"
import { createDecisionLog } from "./decisionLog.js"

function tmpFile() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-log-"))
  return path.join(dir, "decisions.jsonl")
}

const rec = (hash, action = "buy", slot = 1) => ({
  stateHash: hash,
  decision: { action, slot },
  reason: { text: "x" },
})

test("writes only when the state or decision changes", () => {
  const file = tmpFile()
  const log = createDecisionLog(file)
  assert.equal(log.append(rec("a")), true)
  assert.equal(log.append(rec("a")), false)
  assert.equal(log.append(rec("b")), true)
  assert.equal(log.append(rec("b", "hold", -1)), true)
  const lines = fs.readFileSync(file, "utf8").trim().split("\n")
  assert.equal(lines.length, 3)
})

test("readRecent returns the newest entries first and skips a torn line", () => {
  const file = tmpFile()
  const log = createDecisionLog(file)
  log.append(rec("a"))
  log.append(rec("b"))
  log.append(rec("c"))
  fs.appendFileSync(file, '{"stateHash":"tor')
  const recent = log.readRecent(2)
  assert.deepEqual(recent.map((r) => r.stateHash), ["c", "b"])
})

test("on startup, the buffer loads the file tail and skips a torn line", () => {
  const file = tmpFile()
  fs.writeFileSync(file, JSON.stringify(rec("a")) + "\n" + JSON.stringify(rec("b")) + "\n" + '{"stateHash":"tor')
  const recent = createDecisionLog(file).readRecent(5)
  assert.deepEqual(recent.map((r) => r.stateHash), ["b", "a"])
})

test("readRecent on a missing file is empty", () => {
  assert.deepEqual(createDecisionLog(tmpFile()).readRecent(5), [])
})
