import { createApp, errorLogger, loadConfig } from "./app.js"

// CLI entry: runs the tick loop and prints a line to stderr whenever the decision changes.
// stdout is left free; the MCP server (src/mcp/server.js) is a separate entry point.
const config = loadConfig()
let lastKey = null

const { coach, source } = createApp(config, {
  onTick(record) {
    const key = `${record.stateHash}|${record.decision.action}|${record.decision.slot}`
    if (key === lastKey) return
    lastKey = key
    const d = record.decision
    const line = [
      record.ts,
      `level=${record.state.level ?? "?"}`,
      `gold=${record.state.gold ?? "?"}`,
      `hp=${record.state.hp}`,
      `stage=${record.state.stage}`,
      `action=${d.action}`,
      d.slot >= 0 ? `slot=${d.slot}` : null,
      `score=${d.score}`,
      `ms=${record.latencyMs}`,
      record.reason.text,
    ]
      .filter(Boolean)
      .join(" ")
    process.stderr.write(line + "\n")
  },
  onError: errorLogger((text) => process.stderr.write(text)),
})

process.stderr.write(`TFT coach (${source.kind}) ghi log vào ${config.logPath}\n`)
coach.start()

process.on("SIGINT", () => {
  coach.stop()
  process.exit(0)
})
