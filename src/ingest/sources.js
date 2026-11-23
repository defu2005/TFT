import fs from "node:fs"
import { readLiveState, toState } from "./liveClient.js"
import { ramSource } from "./ramSource.js"
import { createStandaloneSource } from "./standaloneSource.js"

export { ramSource, createStandaloneSource }

// A state source is { kind, read(): Promise<state> }. read() must resolve to the state
// shape used by decide(): { level, gold, hp, stage, shop, target }.

export function standaloneSource(options = {}) {
  return createStandaloneSource(options)
}

export function liveSource({ timeoutMs = 150 } = {}) {
  return {
    kind: "live",
    read: () => readLiveState(timeoutMs),
  }
}

// Replays raw payloads from a capture file (JSONL written by src/ingest/capture.js).
// Each line is { ts, payload }; every payload goes through the same toState() as live.
export function captureSource(capturePath) {
  const payloads = []
  for (const line of fs.readFileSync(capturePath, "utf8").split("\n")) {
    if (!line.trim()) continue
    try {
      payloads.push(JSON.parse(line).payload)
    } catch {
      // A torn last line from an interrupted capture is skipped.
    }
  }
  if (payloads.length === 0) throw new Error(`capture has no payloads: ${capturePath}`)
  let index = 0
  return {
    kind: "capture",
    frameCount: payloads.length,
    read: async () => {
      const payload = payloads[index]
      index = (index + 1) % payloads.length
      return toState(structuredClone(payload))
    },
  }
}

// Replays frames from a JSON fixture: { synthetic?, note?, frames: [state, ...] }.
// Loops when it reaches the end.
export function replaySource(fixturePath) {
  const data = JSON.parse(fs.readFileSync(fixturePath, "utf8"))
  const frames = Array.isArray(data) ? data : data.frames
  if (!Array.isArray(frames) || frames.length === 0) {
    throw new Error(`replay fixture has no frames: ${fixturePath}`)
  }
  let index = 0
  return {
    kind: "replay",
    synthetic: data.synthetic === true,
    frameCount: frames.length,
    read: async () => {
      const frame = frames[index]
      index = (index + 1) % frames.length
      return structuredClone(frame)
    },
  }
}
