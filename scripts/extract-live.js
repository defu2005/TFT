#!/usr/bin/env node
// Extracts every gameplay fact the TFT client actually writes, as it is written.
// Sources: TFT.log (events) and TFTEoGStats.json (board, health, placement).
// Read-only. Output: captures/extracted-live.jsonl
//
// Usage: node scripts/extract-live.js
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const LOG = path.join(process.env.LOCALAPPDATA || "", "TFT", "Saved", "Logs", "TFT.log")
const EOG = path.join(process.env.LOCALAPPDATA || "", "TFT", "Saved", "Logs", "TFTEoGStats.json")
const OUT = path.join(ROOT, "captures", "extracted-live.jsonl")
const POLL_MS = Number(process.env.TFT_EXTRACT_POLL_MS) || 400

fs.mkdirSync(path.dirname(OUT), { recursive: true })
fs.writeFileSync(OUT, "", "utf8")

let offset = 0
let carry = ""
let lines = 0
let lastEog = ""

function write(record) {
  fs.appendFileSync(OUT, JSON.stringify(record) + "\n", "utf8")
  lines += 1
}

function note(text) {
  process.stderr.write(`[extract] ${text}\n`)
}

function logTime(line) {
  const m = line.match(/\[(\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})\.(\d{2}):(\d{3})\]/)
  if (!m) return null
  return `${m[1]}-${m[2]}-${m[3]}T${m[4]}:${m[5]}:${m[6]}.${m[7]}Z`
}

function unitOf(line) {
  const m = line.match(/\{(DA_[A-Za-z0-9_]+)\}/)
  return m ? m[1] : null
}

export function parseLogLine(line) {
  const ts = logTime(line)
  if (!ts) {
    if (line.startsWith("Log file open")) return { ts: null, kind: "log-open", text: line.trim() }
    return null
  }

  const phase = line.match(/ETFTPhaseType::(\w+)/)
  if (phase) return { ts, kind: "phase", phase: phase[1] }

  const afk = line.match(/PlayerName\[([^\]]+)\] bNewIsAFK\[(\d)\]/)
  if (afk) return { ts, kind: "afk", player: afk[1], afk: afk[2] === "1" }

  if (line.includes("Trigger[Audio.Event.VO.Unit.Purchase")) return { ts, kind: "purchase", unit: unitOf(line) }

  const star = line.match(/Unit\.StarUp\.(\d)Star/)
  if (star && line.includes("Trigger[")) return { ts, kind: "star", stars: Number(star[1]), unit: unitOf(line) }

  if (line.includes("Trigger[Audio.Event.VO.Unit.Spell")) return { ts, kind: "spell", unit: unitOf(line) }

  if (line.includes("Trigger[Audio.Event.VO.Army.Round.UnitCombatVictory")) return { ts, kind: "victory", unit: unitOf(line) }

  if (line.includes("TFTRoundSubsystem:")) {
    return { ts, kind: "round", message: line.split("TFTRoundSubsystem:")[1].trim() }
  }

  if (line.includes("Augment choice lifecycle")) {
    const event = line.match(/Event\[([^\]]+)\]/)
    const count = line.match(/ChoiceCount\[(\d+)\]/)
    return { ts, kind: "augment", event: event ? event[1] : null, choiceCount: count ? Number(count[1]) : null }
  }

  if (line.includes("Browse Started Browse:")) {
    let where = "other"
    if (line.includes("Frontend_")) where = "frontend"
    else if (line.includes("Name=Player")) where = "bootstrap"
    else if (line.includes("/Mode_Bootstrap/")) where = "match"
    return { ts, kind: "travel", where }
  }

  const music = line.match(/SwitchToMusic - Switched to music \[([^\]]+)\]/)
  if (music) return { ts, kind: "music", music: music[1] }

  return null
}

function consume(text) {
  const parts = (carry + text).split("\n")
  carry = parts.pop() ?? ""
  for (const line of parts) {
    const record = parseLogLine(line)
    if (record) write(record)
  }
}

function readLog() {
  if (!fs.existsSync(LOG)) return
  const size = fs.statSync(LOG).size
  if (size < offset) {
    offset = 0
    carry = ""
    write({ ts: new Date().toISOString(), kind: "log-reset" })
  }
  if (size === offset) return
  const fd = fs.openSync(LOG, "r")
  const buf = Buffer.alloc(size - offset)
  fs.readSync(fd, buf, 0, buf.length, offset)
  fs.closeSync(fd)
  offset = size
  consume(buf.toString("utf8"))
}

function readEog() {
  if (!fs.existsSync(EOG)) return
  const text = fs.readFileSync(EOG, "utf8")
  if (text === lastEog) return
  lastEog = text
  const payload = JSON.parse(text)
  write({ ts: new Date().toISOString(), kind: "snapshot", payload })
  note(`snapshot ${payload.statsBlock?.gameLengthSeconds ?? "?"}s, ${payload.statsBlock?.players?.length ?? 0} người`)
}

function start() {
  write({ ts: new Date().toISOString(), kind: "meta", log: LOG, eog: EOG })
  readLog()
  try { readEog() } catch (error) { note(error.message) }
  note(`đã ghi ${lines} dòng vào ${OUT}`)

  const timer = setInterval(() => {
    try { readLog() } catch (error) { note(error.message) }
    try { readEog() } catch (error) { note(error.message) }
  }, POLL_MS)

  process.on("SIGINT", () => {
    clearInterval(timer)
    note(`dừng, ${lines} dòng`)
    process.exit(0)
  })
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) start()
