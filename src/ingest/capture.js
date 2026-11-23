#!/usr/bin/env node
// Records raw /allgamedata payloads from the Live Client to a JSONL file, one line per
// change: { ts, payload }. It makes no decisions. Use the file with TFT_SOURCE=capture.
//
// The payload contains the player's Riot ID, so captures go to captures/ (gitignored).
//
// Usage: npm run capture            -> captures/live-<timestamp>.jsonl
//        npm run capture -- my.jsonl
// Env:   TFT_CAPTURE_POLL_MS        poll interval (default 1000)
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { getJson } from "./liveClient.js"

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..")
const POLL_MS = Number(process.env.TFT_CAPTURE_POLL_MS) || 1000

function defaultOutFile() {
  const stamp = new Date().toISOString().replace(/[:.]/g, "-")
  return path.join(ROOT, "captures", `live-${stamp}.jsonl`)
}

export function startCapture({ outFile, pollMs = POLL_MS, fetchPayload = () => getJson("/allgamedata", 500), write = (t) => process.stderr.write(t) }) {
  fs.mkdirSync(path.dirname(outFile), { recursive: true })
  let last = null
  let lines = 0
  let busy = false
  let lastError = null

  const timer = setInterval(async () => {
    if (busy) return
    busy = true
    try {
      const payload = await fetchPayload()
      lastError = null
      const text = JSON.stringify(payload)
      if (text !== last) {
        fs.appendFileSync(outFile, JSON.stringify({ ts: new Date().toISOString(), payload }) + "\n", "utf8")
        last = text
        lines += 1
      }
    } catch (error) {
      if (error.message !== lastError) {
        lastError = error.message
        write(`[capture] ${error.message}\n`)
      }
    } finally {
      busy = false
    }
  }, pollMs)

  return {
    outFile,
    lines: () => lines,
    stop: () => clearInterval(timer),
  }
}

// Only runs as the CLI entry point, not when imported by tests.
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const outFile = path.resolve(process.argv[2] || defaultOutFile())
  const capture = startCapture({ outFile })
  process.stderr.write(`[capture] ghi vào ${outFile}, poll ${POLL_MS} ms. Ctrl+C để dừng.\n`)
  process.on("SIGINT", () => {
    capture.stop()
    process.stderr.write(`[capture] đã ghi ${capture.lines()} dòng vào ${outFile}\n`)
    process.exit(0)
  })
}
