#!/usr/bin/env node
// Probes the Live Client endpoints on 127.0.0.1:2999 once per interval and logs the
// HTTP status and size of each one. Read-only: it only sends GET requests to localhost.
// Raw bodies are saved to captures/probe/ (gitignored, may contain Riot ID).
//
// Usage: node scripts/probe-live.js [intervalMs]
import fs from "node:fs"
import path from "node:path"
import https from "node:https"
import { fileURLToPath } from "node:url"

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
const OUT = path.join(ROOT, "captures", "probe")
const INTERVAL = Number(process.argv[2]) || 2000
const ENDPOINTS = ["allgamedata", "activeplayer", "playerlist", "eventdata", "gamestats", "activeplayername"]
const agent = new https.Agent({ rejectUnauthorized: false, keepAlive: false })

fs.mkdirSync(OUT, { recursive: true })
const logFile = path.join(OUT, `probe-${new Date().toISOString().replace(/[:.]/g, "-")}.log`)
const log = (line) => {
  fs.appendFileSync(logFile, line + "\n", "utf8")
  process.stderr.write(line + "\n")
}

function get(endpoint) {
  return new Promise((resolve) => {
    const req = https.request(
      `https://127.0.0.1:2999/liveclientdata/${endpoint}`,
      { agent, method: "GET", timeout: 1000, rejectUnauthorized: false },
      (res) => {
        const chunks = []
        res.on("data", (c) => chunks.push(c))
        res.on("end", () => resolve({ endpoint, status: res.statusCode, body: Buffer.concat(chunks) }))
      },
    )
    req.on("timeout", () => req.destroy(new Error("timeout")))
    req.on("error", (e) => resolve({ endpoint, status: e.code || e.message, body: null }))
    req.end()
  })
}

const seen = new Map()
const rawFile = logFile.replace(/\.log$/, ".raw.jsonl")
log(`[probe] log: ${logFile}`)
log(`[probe] raw: ${rawFile}, chu kỳ ${INTERVAL} ms. Ctrl+C để dừng.`)

// Every response is kept raw: one JSONL line per change of (status, body), including non-200
// bodies, so nothing is lost if the endpoint answers with an error text.
const timer = setInterval(async () => {
  for (const endpoint of ENDPOINTS) {
    const r = await get(endpoint)
    const text = r.body ? r.body.toString("utf8") : ""
    const key = `${r.status}|${text}`
    if (seen.get(endpoint) === key) continue
    seen.set(endpoint, key)
    const ts = new Date().toISOString()
    log(`${ts} ${endpoint} -> ${r.status} (${r.body ? r.body.length : 0} bytes)`)
    fs.appendFileSync(rawFile, JSON.stringify({ ts, endpoint, status: r.status, body: text }) + "\n", "utf8")
  }
}, INTERVAL)

process.on("SIGINT", () => {
  clearInterval(timer)
  log("[probe] dừng")
  process.exit(0)
})
