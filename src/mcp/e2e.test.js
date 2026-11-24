import assert from "node:assert/strict"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import test from "node:test"
import { Client } from "@modelcontextprotocol/sdk/client/index.js"
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js"

const ROOT = path.join(import.meta.dirname, "..", "..")

test("MCP server on the replay fixture: initialize, list tools, call tools", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-mcp-"))
  const logPath = path.join(dir, "decisions.jsonl")
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [path.join(ROOT, "src", "mcp", "server.js")],
    cwd: ROOT,
    env: { ...process.env, TFT_SOURCE: "replay", TFT_LOG: logPath, TFT_INTERVAL_MS: "50" },
    stderr: "pipe",
  })
  const client = new Client({ name: "e2e", version: "0.0.0" })
  await client.connect(transport)
  try {
    const { tools } = await client.listTools()
    const names = tools.map((t) => t.name).sort()
    assert.deepEqual(names, [
      "tft_current_decision",
      "tft_evaluate_state",
      "tft_hit_chance",
      "tft_interest",
      "tft_recent_decisions",
      "tft_rules",
      "tft_set_line",
      "tft_set_target",
      "tft_status",
    ])

    await new Promise((r) => setTimeout(r, 400))

    const status = JSON.parse((await client.callTool({ name: "tft_status", arguments: {} })).content[0].text)
    assert.equal(status.source.kind, "replay")
    assert.equal(status.source.ok, true)
    assert.ok(status.ticks >= 1)

    const current = JSON.parse((await client.callTool({ name: "tft_current_decision", arguments: {} })).content[0].text)
    assert.equal(current.ready, true)
    assert.ok(current.reason.text.length > 0)

    const evalRes = JSON.parse(
      (
        await client.callTool({
          name: "tft_evaluate_state",
          arguments: { level: 7, gold: 42, hp: 55, stage: 4, shop: [null, { id: "B", cost: 3, copiesOwned: 2, priority: 5 }, null, null, null] },
        })
      ).content[0].text,
    )
    assert.equal(evalRes.action, "buy")

    const sellRes = JSON.parse(
      (
        await client.callTool({
          name: "tft_evaluate_state",
          arguments: {
            level: 7,
            gold: 40,
            hp: 80,
            stage: 4,
            shop: [{ id: "core", cost: 3, copiesOwned: 0, priority: 5 }, null, null, null, null],
            bench: [
              { id: "x", star: 1, sellValue: 1 },
              { id: "y", star: 1, sellValue: 3 },
            ],
          },
        })
      ).content[0].text,
    )
    assert.equal(sellRes.action, "sell")

    const hit = JSON.parse((await client.callTool({ name: "tft_hit_chance", arguments: { level: 8, cost: 4, copiesLeft: 6, champsAtCost: 12 } })).content[0].text)
    assert.ok(hit.hitChance > 0 && hit.hitChance <= 1)

    const interest = JSON.parse((await client.callTool({ name: "tft_interest", arguments: { gold: 34 } })).content[0].text)
    assert.equal(interest.interest, 3)

    await client.callTool({ name: "tft_set_target", arguments: { target: { cost: 4, copiesLeft: 6, priority: 5, champsAtCost: 12, id: "T" } } })

    const recent = JSON.parse((await client.callTool({ name: "tft_recent_decisions", arguments: { limit: 3 } })).content[0].text)
    assert.ok(recent.entries.length >= 1)
    assert.ok(fs.existsSync(logPath))
  } finally {
    await client.close()
  }
})
