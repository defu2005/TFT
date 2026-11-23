import { decide, actionName } from "../engine/decide.js"
import { explain } from "../engine/reason.js"

const SCHEMA_VERSION = 2

// The coach owns the tick loop and the cached state. Entry points (CLI, MCP) only
// read from it. MCP tools call getState() and never trigger a read from the source.
export function createCoach({
  source,
  logger = null,
  intervalMs = 250,
  onTick = null,
  onError = null,
  autoLine = null,
  autoLineCheck = null,
  rules = null,
  profile = null,
  now = () => Date.now(),
} = {}) {
  if (!source) throw new Error("createCoach needs a source")

  let timer = null
  let busy = false
  let target = null
  // Lines chosen by the user or an agent: unit id -> priority. Applied to the shop each tick.
  const lines = new Map()
  const sourceStatus = { kind: source.kind, ok: false, error: null, lastOkAt: null, reads: 0, failures: 0, missing: [] }
  const cache = {
    snapshot: null,
    input: null,
    decision: null,
    reason: null,
    stateHash: null,
    latencyMs: null,
    updatedAt: null,
    ticks: 0,
  }

  async function tick() {
    if (busy) return null
    busy = true
    const started = performance.now()
    try {
      let snapshot
      try {
        snapshot = await source.read()
        sourceStatus.ok = true
        sourceStatus.error = null
        sourceStatus.lastOkAt = now()
        sourceStatus.reads += 1
      } catch (error) {
        sourceStatus.ok = false
        sourceStatus.error = error.message
        sourceStatus.failures += 1
        if (onError) onError(error)
        return null
      }

      // `missing` lists fields the source did not provide; it is not part of the engine input.
      const { missing = [], ...fields } = snapshot
      sourceStatus.missing = missing
      const auto = autoLine ? autoLine(fields) : null
      const input = {
        ...fields,
        shop: applyLines(fields.shop, lines, auto),
        target: target ?? fields.target ?? null,
      }
      if (Array.isArray(fields.bench)) input.bench = applyLines(fields.bench, lines, auto)
      const trace = []
      const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
      decide(input, out, trace, rules, profile)
      const reason = explain(input, out, trace, profile ? `bảng tỉ lệ shop của set ${profile.set}, bản yêu cầu ${profile.requested ?? "mới nhất"}, bản áp dụng ${profile.applied ?? "không có"}, từ file hồ sơ, chưa xác minh` : undefined)
      if (auto && auto.size) reason.factors.autoLine = Object.fromEntries(auto)
      if (autoLineCheck) {
        const { ids, missingId, boardMissing } = autoLineCheck(fields)
        if (ids.length || missingId || boardMissing) {
          reason.factors.setMismatch = { count: ids.length, ids: ids.slice(0, 5), missingId, boardMissing }
          if (ids.length) reason.caveats.push(`${ids.length} id không có trong file set, line tự động bỏ qua chúng`)
          if (missingId) reason.caveats.push(`${missingId} tướng không có id hay championName, line tự động không xét được chúng`)
          if (boardMissing) reason.caveats.push("nguồn không gửi bàn đấu, line tự động không có gì để xét")
        }
      }
      if (rules) reason.factors.rules = rules
      if (profile) {
        reason.factors.profile = { set: profile.set, requested: profile.requested, applied: profile.applied }
        for (const note of profile.caveats) reason.caveats.push(note)
      }
      if (missing.length) {
        const note = `thiếu trường từ nguồn: ${missing.join(", ")}; đang dùng giá trị mặc định cho các trường này`
        reason.caveats.push(note)
        reason.text += ` (${note})`
      }
      const latencyMs = performance.now() - started
      const stateHash = hashState(input)

      const record = {
        schema: SCHEMA_VERSION,
        ts: new Date(now()).toISOString(),
        source: "engine",
        sourceKind: source.kind,
        latencyMs: round(latencyMs),
        stateHash,
        known: { shop: Array.isArray(input.shop), target: !!input.target },
        state: input,
        decision: { action: actionName(out.action), slot: out.slot, bench: out.bench, score: round(out.score), hit: round(out.hit) },
        reason,
      }

      cache.snapshot = snapshot
      cache.input = input
      cache.decision = record.decision
      cache.reason = reason
      cache.stateHash = stateHash
      cache.latencyMs = record.latencyMs
      cache.updatedAt = record.ts
      cache.ticks += 1

      if (logger) logger.append(record)
      if (onTick) onTick(record)
      return record
    } finally {
      busy = false
    }
  }

  return {
    tick,

    start() {
      if (timer) return
      timer = setInterval(() => {
        tick().catch((error) => onError?.(error))
      }, intervalMs)
    },

    stop() {
      if (timer) clearInterval(timer)
      timer = null
    },

    setTarget(next) {
      target = next ? sanitizeTarget(next) : null
      return target
    },

    // priority null or 0 removes the unit from the line.
    setLine(unitId, priority) {
      if (typeof unitId !== "string" || unitId === "") throw new Error("unitId phải là chuỗi không rỗng")
      if (priority == null || priority <= 0) lines.delete(unitId)
      else lines.set(unitId, priority)
      return Object.fromEntries(lines)
    },

    getLines() {
      return Object.fromEntries(lines)
    },

    // Cached values only. Never reads the source.
    getState() {
      return {
        source: { ...sourceStatus },
        target,
        lines: Object.fromEntries(lines),
        decision: cache.decision,
        reason: cache.reason,
        input: cache.input,
        stateHash: cache.stateHash,
        latencyMs: cache.latencyMs,
        updatedAt: cache.updatedAt,
        ticks: cache.ticks,
        intervalMs,
        autoLine: !!autoLine,
        rules: rules ?? null,
        profile: profile ? { set: profile.set, requested: profile.requested, applied: profile.applied } : null,
      }
    },

    recent(limit = 20) {
      return logger ? logger.readRecent(limit) : []
    },
  }
}

// Returns a new shop array with priorities taken from the line map. The source's array is not changed.
function applyLines(shop, lines, auto = null) {
  if (!Array.isArray(shop)) return shop ?? null
  return shop.map((unit) => {
    if (!unit) return null
    const priority = lines.has(unit.id) ? lines.get(unit.id) : Math.max(auto?.get(unit.id) ?? 0, unit.priority ?? 0)
    return { ...unit, priority }
  })
}

// Includes everything decide() reads, so a change in target or line is logged.
export function hashState(state) {
  let ids = ""
  if (Array.isArray(state.shop)) {
    for (const unit of state.shop) ids += unit ? `${unit.id ?? "-"}:${unit.priority ?? 0}:${unit.copiesOwned ?? 0}:${unit.takenByOthers ?? ""},` : "-,"
  }
  const t = state.target
  const targetKey = t ? `${t.id ?? "-"}:${t.cost}:${t.copiesLeft}:${t.priority}:${t.champsAtCost ?? ""}` : "none"
  return `${state.level}|${state.gold}|${state.hp}|${state.stage}|${ids}|${targetKey}|${unitsKey(state.board)}|${unitsKey(state.bench)}|${state.freeRolls ?? ""}`
}

function unitsKey(list) {
  if (!Array.isArray(list)) return ""
  let key = ""
  for (const u of list) key += u ? `${u.id ?? "-"}:${u.star ?? ""}:${u.priority ?? 0}:${u.sellValue ?? ""},` : "-,"
  return key
}

function sanitizeTarget(t) {
  return {
    id: t.id ?? null,
    cost: t.cost,
    copiesLeft: t.copiesLeft ?? 0,
    priority: t.priority ?? 1,
    champsAtCost: t.champsAtCost,
  }
}

function round(value) {
  return typeof value === "number" && Number.isFinite(value) ? Math.round(value * 1000) / 1000 : value
}
