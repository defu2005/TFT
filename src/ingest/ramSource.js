import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..")
const DEFAULT_STATE_FILE = path.join(ROOT, "captures", "ram-state.json")

/**
 * Tạo nguồn dữ liệu đọc từ RAM.
 * Dữ liệu được probe-ram.py cập nhật liên tục vào captures/ram-state.json.
 */
export function ramSource(statePath = DEFAULT_STATE_FILE) {
  return {
    kind: "ram",
    read: async () => {
      if (!fs.existsSync(statePath)) {
        return {
          level: null,
          gold: null,
          hp: 100,
          stage: 1,
          shop: null,
          target: null,
          missing: ["ram-state-file-not-found"],
        }
      }

      try {
        const text = fs.readFileSync(statePath, "utf8")
        const data = JSON.parse(text)
        const missing = []

        if (data.gold == null) missing.push("gold")
        if (data.level == null) missing.push("level")
        if (data.hp === undefined) missing.push("hp")
        if (data.stage === undefined) missing.push("stage")
        if (!Array.isArray(data.shop) || data.shop.every(s => s === null)) missing.push("shop")

        return {
          // Missing gold or level is null, not 0 or 1: the coach flags it and the engine makes no buy, roll or xp on it.
          level: data.level == null ? null : Number(data.level) || 1,
          gold: data.gold == null ? null : Number(data.gold) || 0,
          hp: Number(data.hp) || 100,
          stage: Number(data.stage) || 1,
          shop: Array.isArray(data.shop) ? data.shop : null,
          target: data.target ?? null,
          missing,
          ts: data.ts,
        }
      } catch (err) {
        return {
          level: null,
          gold: null,
          hp: 100,
          stage: 1,
          shop: null,
          target: null,
          missing: [`ram-read-error: ${err.message}`],
        }
      }
    },
  }
}
