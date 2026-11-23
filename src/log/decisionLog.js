import fs from "node:fs"
import path from "node:path"

const BUFFER_SIZE = 200

// JSONL log of decisions. A line is written only when the state or the decision changes.
// The last BUFFER_SIZE records are kept in memory, so readRecent never touches the file
// during a tick. The file is read once, at creation, to fill the buffer.
export function createDecisionLog(filePath) {
  let lastKey = null
  const buffer = []

  fs.mkdirSync(path.dirname(filePath), { recursive: true })
  loadTail()

  function loadTail() {
    if (!fs.existsSync(filePath)) return
    const lines = fs.readFileSync(filePath, "utf8").split("\n").filter(Boolean)
    for (let i = Math.max(0, lines.length - BUFFER_SIZE); i < lines.length; i++) {
      try {
        buffer.push(JSON.parse(lines[i]))
      } catch {
        // A torn last line from a crash is skipped.
      }
    }
  }

  return {
    path: filePath,

    // Returns true when a line was written.
    append(record) {
      const key = `${record.stateHash}|${record.decision.action}|${record.decision.slot}`
      if (key === lastKey) return false
      fs.appendFileSync(filePath, JSON.stringify(record) + "\n", "utf8")
      lastKey = key
      buffer.push(record)
      if (buffer.length > BUFFER_SIZE) buffer.splice(0, buffer.length - BUFFER_SIZE)
      return true
    },

    // Newest first, from memory.
    readRecent(limit = 20) {
      const n = Math.min(Math.max(1, limit | 0), buffer.length)
      return buffer.slice(-n).reverse()
    },
  }
}
