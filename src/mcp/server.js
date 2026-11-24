#!/usr/bin/env node
// MCP server over stdio. stdout belongs to the protocol: all human-readable output goes to stderr.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"
import { createApp, errorLogger, loadConfig } from "../app.js"
import { registerTools } from "./tools.js"

const { coach, source, config, profile } = createApp(loadConfig(), {
  onError: errorLogger((text) => process.stderr.write(text)),
})

coach.start()
process.stderr.write(`tft-coach MCP (${source.kind}), log: ${config.logPath}\n`)

const server = new McpServer({ name: "tft-coach", version: "0.1.0" })
registerTools(server, { coach, rules: config.rules ?? null, profile })

const shutdown = () => {
  coach.stop()
  process.exit(0)
}
process.on("SIGINT", shutdown)
process.stdin.on("end", shutdown)

await server.connect(new StdioServerTransport())
