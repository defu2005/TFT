#!/usr/bin/env node
// Tails the TFT client's own log for gameplay lines and polls Live Client Data.
// Read-only: it does not attach to the game process. Output stays in captures/.
//
// Usage: node scripts/tail-live.js
import fs from "node:fs"
import path from "node:path"
import https from "node:https"
import { fileURLToPath } from "node:url"

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const LOG = path.join(process.env.LOCALAPPDATA || "", "TFT", "Saved", "Logs", "TFT.log")
const EOG = path.join(process.env.LOCALAPPDATA || "", "TFT", "Saved", "Logs", "TFTEoGStats.json")
const POLL_MS = Number(process.env.TFT_TAIL_POLL_MS) || 400
const KEEP = /ETFTPhaseType|TFTRoundSubsystem|TFTShopPlayerSubsystem|TFTAugmentPlayerSubsystem|TFTCarouselSubsystem|TFTScoreboardSubsystem|TFTCharacter_|TFTPlayerState|TFTPlayerAFKSubsystem/

const stamp = new Date().toISOString().replace(/[:.]/g, "-")
const outFile = path.join(ROOT, "captures", `tail-${stamp}.jsonl`)
fs.mkdirSync(path.dirname(outFile), { recursive: true })

let offset = fs.existsSync(LOG) ? fs.statSync(LOG).size : 0
let carry = ""
let lines = 0
let eogStamp = fs.existsSync(EOG) ? fs.statSync(EOG).mtimeMs : 0
let liveStatus = "unknown"

function write(record) {
  fs.appendFileSync(outFile, JSON.stringify(record) + "\n", "utf8")
  lines += 1
}

function note(text) {
  process.stderr.write(`[tail] ${text}\n`)
}

function pollLive() {
  const req = https.request(
    "https://127.0.0.1:2999/liveclientdata/allgamedata",
    { method: "GET", timeout: 800, rejectUnauthorized: false },
    (res) => {
      const chunks = []
      res.on("data", (c) => chunks.push(c))
      res.on("end", () => {
        const body = Buffer.concat(chunks).toString("utf8")
        const status = `http ${res.statusCode} ${body.length}b`
        if (status !== liveStatus) {
          liveStatus = status
          note(`live client ${status}`)
          let payload = body
          try { payload = JSON.parse(body) } catch { /* keep text */ }
          write({ ts: new Date().toISOString(), source: "liveclient", status: res.statusCode, payload })
        }
      })
    },
  )
  req.on("timeout", () => req.destroy(new Error("timeout")))
  req.on("error", (error) => {
    const status = error.code || error.message
    if (status !== liveStatus) {
      liveStatus = status
      note(`live client ${status}`)
      write({ ts: new Date().toISOString(), source: "liveclient", error: status })
    }
  })
  req.end()
}

function readLog() {
  if (!fs.existsSync(LOG)) return
  const size = fs.statSync(LOG).size
  if (size < offset) {
    offset = 0
    carry = ""
    note("log đã quay vòng")
  }
  if (size === offset) return
  const fd = fs.openSync(LOG, "r")
  const buf = Buffer.alloc(size - offset)
  fs.readSync(fd, buf, 0, buf.length, offset)
  fs.closeSync(fd)
  offset = size
  const text = carry + buf.toString("utf8")
  const parts = text.split("\n")
  carry = parts.pop() ?? ""
  for (const line of parts) {
    if (!KEEP.test(line)) continue
    write({ ts: new Date().toISOString(), source: "tft.log", line })
    note(line.slice(line.indexOf("]") + 1, line.indexOf("]") + 180).trim())
  }
}

function readEog() {
  if (!fs.existsSync(EOG)) return
  const mtime = fs.statSync(EOG).mtimeMs
  if (mtime === eogStamp) return
  eogStamp = mtime
  write({ ts: new Date().toISOString(), source: "eog", payload: JSON.parse(fs.readFileSync(EOG, "utf8")) })
  note("TFTEoGStats.json đổi")
}

write({ ts: new Date().toISOString(), source: "meta", log: LOG, offset })
note(`ghi ${outFile}`)
note(`TFT.log từ offset ${offset}. Ctrl+C để dừng.`)

const timer = setInterval(() => {
  try { readLog() } catch (error) { note(error.message) }
  try { readEog() } catch (error) { note(error.message) }
  pollLive()
}, POLL_MS)

process.on("SIGINT", () => {
  clearInterval(timer)
  note(`dừng, ${lines} dòng`)
  process.exit(0)
})
