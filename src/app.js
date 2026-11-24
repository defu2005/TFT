import path from "node:path"
import { fileURLToPath } from "node:url"
import fs from "node:fs"
import { createCoach } from "./core/coach.js"
import { buildProfile } from "./data/profileFile.js"
import { autoLine, createSetIndex, unknownIds } from "./engine/autoline.js"
import { applyTraitOverlay } from "./engine/traitOverlay.js"
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
//   TFT_RULES        comma list of opt-in U9 rules: keepInterest, earlyLevel, guideLevels (default: none)
//   TFT_PROFILE_FILE set file with base tables and patch overlays (default: rules.js)
//   TFT_TRAIT_OVERLAY trait overlay file (add-only, off by default); needs TFT_AUTO_LINE=1
//   TFT_PATCH        patch version to apply from that file (default: the latest)
const KNOWN_RULES = ["keepInterest", "earlyLevel", "guideLevels"]

// Returns null when unset; otherwise flags for the named rules. Unknown names throw.
export function parseRules(value) {
  const names = String(value ?? "").split(",").map((s) => s.trim()).filter(Boolean)
  if (names.length === 0) return null
  const rules = { keepInterest: false, earlyLevel: false, guideLevels: false }
  for (const name of names) {
    if (!KNOWN_RULES.includes(name)) throw new Error(`TFT_RULES có tên không rõ: ${name} (chọn trong ${KNOWN_RULES.join(", ")})`)
    rules[name] = true
  }
  return rules
}

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
    traitOverlayFile: env.TFT_TRAIT_OVERLAY || null,
    rules: parseRules(env.TFT_RULES),
    profileFile: env.TFT_PROFILE_FILE || null,
    patch: env.TFT_PATCH || null,
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
  let autoCheck = null
  let traitOverlay = null
  if (config.traitOverlayFile && !config.autoLine) throw new Error("TFT_TRAIT_OVERLAY cần TFT_AUTO_LINE=1")
  if (config.autoLine) {
    if (!config.setFile) throw new Error("TFT_AUTO_LINE=1 cần TFT_SET_FILE")
    let index = createSetIndex(JSON.parse(fs.readFileSync(config.setFile, "utf8")))
    if (config.traitOverlayFile) {
      index = applyTraitOverlay(index, JSON.parse(fs.readFileSync(config.traitOverlayFile, "utf8")))
      traitOverlay = { set: index.set, verified: index.verified, applied: index.applied, file: config.traitOverlayFile }
    }
    auto = (state) => autoLine(index, state)
    autoCheck = (state) => unknownIds(index, state)
  }
  if (config.patch && !config.profileFile) throw new Error("TFT_PATCH cần TFT_PROFILE_FILE")
  let profile = null
  if (config.profileFile) {
    profile = buildProfile(JSON.parse(fs.readFileSync(config.profileFile, "utf8")), config.patch)
  }
  const source = makeSource(config)
  const logger = createDecisionLog(config.logPath)
  const coach = createCoach({ source, logger, intervalMs: config.intervalMs, onTick, onError, autoLine: auto, autoLineCheck: autoCheck, rules: config.rules ?? null, profile, traitOverlay })
  return { coach, source, logger, config, profile, traitOverlay }
}
