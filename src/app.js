import path from "node:path"
import { fileURLToPath } from "node:url"
import fs from "node:fs"
import { createCoach } from "./core/coach.js"
import { autoLine, createSetIndex } from "./engine/autoline.js"
import { createDecisionLog } from "./log/decisionLog.js"
import { captureSource, liveSource, replaySource, ramSource, standaloneSource } from "./ingest/sources.js"

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const SOURCES = ["live", "replay", "capture", "ram", "standalone", "hybrid"]

// Environment:
//   TFT_SOURCE       live (default), replay (synthetic states) or capture (raw payloads from a capture file)
//   TFT_REPLAY       fixture path for replay (default: synthetic fixture in src/data/fixtures)
//   TFT_CAPTURE      capture file for capture mode (JSONL from `npm run capture`); required in that mode
//   TFT_LOG          decision log path (default: logs/decisions.jsonl)
//   TFT_INTERVAL_MS  tick interval (default: 250)
export function loadConfig(env = process.env) {
  const source = SOURCES.includes(env.TFT_SOURCE) ? env.TFT_SOURCE : "live"
  if (source === "capture" && !env.TFT_CAPTURE) {
    throw new Error("TFT_SOURCE=capture cần TFT_CAPTURE trỏ tới file capture")
  }
  return {
    source,
    replayPath: env.TFT_REPLAY || path.join(ROOT, "src", "data", "fixtures", "replay-synthetic.json"),
    capturePath: env.TFT_CAPTURE || null,
    ramStatePath: env.TFT_RAM_STATE || path.join(ROOT, "captures", "ram-state.json"),
    logPath: env.TFT_LOG || path.join(ROOT, "logs", "decisions.jsonl"),
    intervalMs: Number(env.TFT_INTERVAL_MS) || 250,
    autoLine: env.TFT_AUTO_LINE === "1",
    setFile: env.TFT_SET_FILE || null,
  }
}

function makeSource(config) {
  if (config.source === "replay") return replaySource(config.replayPath)
  if (config.source === "capture") return captureSource(config.capturePath)
  if (config.source === "ram") return ramSource(config.ramStatePath)
  if (config.source === "standalone" || config.source === "hybrid") return standaloneSource(config.standaloneOptions || {})
  return liveSource({ timeoutMs: 150 })
}

// Writes a source error to `write` only when the message changes, so a dead source
// does not flood the output at tick rate.
export function errorLogger(write) {
  let last = null
  return (error) => {
    const message = error?.message ?? String(error)
    if (message === last) return
    last = message
    write(`[coach] ${message}\n`)
  }
}

export function createApp(config = loadConfig(), { onTick = null, onError = null } = {}) {
  let auto = null
  if (config.autoLine) {
    if (!config.setFile) throw new Error("TFT_AUTO_LINE=1 cần TFT_SET_FILE")
    const index = createSetIndex(JSON.parse(fs.readFileSync(config.setFile, "utf8")))
    auto = (state) => autoLine(index, state)
  }
  const source = makeSource(config)
  const logger = createDecisionLog(config.logPath)
  const coach = createCoach({ source, logger, intervalMs: config.intervalMs, onTick, onError, autoLine: auto })
  return { coach, source, logger, config }
}
