// Builds a profile from a set file with ordered patch overlays. Each patch lists only the rows it changes.
// Missing base tables fall back to DEFAULT_PROFILE (rules.js) and are named in the caveats.
// `version` is the patch label the set file uses (for example metabot's 16.20); it is not Riot's client patch number.
import { DEFAULT_PROFILE } from "./profile.js"

const INHERITABLE = ["shopOdds", "poolCopies", "champsPerCost"]
const BASE_KEYS = ["maxCost", ...INHERITABLE]
const PATCH_KEYS = ["version", "notes", "maxCost", "shopOdds", "poolCopies", "champsPerCost", "unmodelled"]
const FILE_KEYS = ["set", "base", "patches", "unmodelled"]

export function parseVersion(version) {
  const parts = String(version).split(".")
  if (parts.some((p) => !/^\d+$/.test(p))) throw new Error(`phiên bản không hợp lệ: ${version}`)
  return parts.map(Number)
}

// Numeric compare: 16.9 comes before 16.20.
export function compareVersions(a, b) {
  const x = parseVersion(a)
  const y = parseVersion(b)
  for (let i = 0; i < Math.max(x.length, y.length); i++) {
    const d = (x[i] ?? 0) - (y[i] ?? 0)
    if (d !== 0) return d
  }
  return 0
}

function checkKeys(obj, allowed, where) {
  for (const key of Object.keys(obj)) {
    if (!allowed.includes(key)) throw new Error(`${where}: trường không rõ "${key}"`)
  }
}

function checkIndexKeys(obj, max, where) {
  for (const key of Object.keys(obj)) {
    const n = Number(key)
    if (!/^\d+$/.test(key) || n < 1 || n > max) throw new Error(`${where}: khóa "${key}" không hợp lệ (cần số từ 1 đến ${max})`)
  }
}

export function buildProfile(file, patchVersion = null) {
  if (!file || typeof file !== "object" || typeof file.set !== "string") throw new Error("file profile cần trường set")
  checkKeys(file, FILE_KEYS, "file")
  const base = file.base ?? {}
  checkKeys(base, BASE_KEYS, "base")
  const caveats = []
  for (const note of file.unmodelled ?? []) caveats.push(`chưa mô hình (set ${file.set}): ${note}`)

  const maxCost = base.maxCost ?? DEFAULT_PROFILE.maxCost
  if (!Number.isInteger(maxCost) || maxCost < 1) throw new Error("maxCost phải là số nguyên dương")

  const tables = {}
  const fromDefault = new Set()
  for (const field of INHERITABLE) {
    if (base[field] !== undefined) {
      tables[field] = structuredClone(base[field])
    } else {
      if (maxCost !== DEFAULT_PROFILE.maxCost) throw new Error(`maxCost ${maxCost} cần ${field} trong base`)
      tables[field] = structuredClone(DEFAULT_PROFILE[field])
      fromDefault.add(field)
    }
  }

  const patches = [...(file.patches ?? [])]
  for (const patch of patches) {
    if (!patch || typeof patch.version !== "string") throw new Error("mỗi bản vá cần trường version")
    checkKeys(patch, PATCH_KEYS, `bản vá ${patch.version}`)
    parseVersion(patch.version)
  }
  patches.sort((a, b) => compareVersions(a.version, b.version))
  for (let i = 1; i < patches.length; i++) {
    if (compareVersions(patches[i - 1].version, patches[i].version) === 0) throw new Error(`trùng phiên bản: ${patches[i].version}`)
  }
  const requested = patchVersion ?? null
  if (requested != null) parseVersion(requested)
  const applied = requested == null ? patches : patches.filter((p) => compareVersions(p.version, requested) <= 0)
  const newestApplied = applied.length ? applied[applied.length - 1].version : null

  let maxCostNow = maxCost
  const overridden = new Set()
  for (const patch of applied) {
    if (patch.maxCost !== undefined) maxCostNow = patch.maxCost
    const where = `bản vá ${patch.version}`
    for (const [level, row] of Object.entries(patch.shopOdds ?? {})) {
      checkIndexKeys({ [level]: row }, 99, `${where} shopOdds`)
      tables.shopOdds[Number(level)] = row
      overridden.add(Number(level))
    }
    checkIndexKeys(patch.poolCopies ?? {}, maxCostNow, `${where} poolCopies`)
    checkIndexKeys(patch.champsPerCost ?? {}, maxCostNow, `${where} champsPerCost`)
    for (const [cost, value] of Object.entries(patch.poolCopies ?? {})) tables.poolCopies[Number(cost)] = value
    for (const [cost, value] of Object.entries(patch.champsPerCost ?? {})) tables.champsPerCost[Number(cost)] = value
    for (const note of patch.unmodelled ?? []) caveats.push(`chưa mô hình (bản ${patch.version}): ${note}`)
  }

  validate(tables, maxCostNow)
  if (fromDefault.has("shopOdds")) {
    const levels = []
    for (let level = 1; level < tables.shopOdds.length; level++) if (!overridden.has(level)) levels.push(level)
    if (levels.length) caveats.push(`shopOdds ở level ${levels.join(", ")} lấy từ mặc định (rules.js)`)
  }
  if (tables.shopOdds.length < DEFAULT_PROFILE.shopOdds.length) {
    caveats.push(`bảng odds chỉ đến level ${tables.shopOdds.length - 1}; level cao hơn trả xác suất 0`)
  }
  for (const field of ["poolCopies", "champsPerCost"]) {
    if (fromDefault.has(field)) caveats.push(`${field} lấy từ mặc định (rules.js)`)
  }
  return Object.freeze({
    set: file.set,
    requested,
    applied: newestApplied,
    patch: requested ?? newestApplied,
    maxCost: maxCostNow,
    shopOdds: Object.freeze(tables.shopOdds),
    poolCopies: Object.freeze(tables.poolCopies),
    champsPerCost: Object.freeze(tables.champsPerCost),
    caveats: Object.freeze(caveats),
  })
}

function validate(tables, maxCost) {
  for (const field of ["poolCopies", "champsPerCost"]) {
    const table = tables[field]
    if (table.length !== maxCost + 1) throw new Error(`${field} cần ${maxCost + 1} phần tử`)
    table.forEach((value, i) => {
      if (typeof value !== "number" || !Number.isFinite(value) || value < 0) throw new Error(`${field}[${i}] phải là số không âm`)
    })
  }
  const odds = tables.shopOdds
  for (let level = 1; level < odds.length; level++) {
    const row = odds[level]
    if (!Array.isArray(row) || row.length !== maxCost) throw new Error(`shopOdds level ${level} cần một hàng ${maxCost} phần tử`)
    if (row.some((p) => typeof p !== "number" || p < 0 || p > 1)) throw new Error(`shopOdds level ${level} có giá trị ngoài [0, 1]`)
    const sum = row.reduce((a, b) => a + b, 0)
    if (Math.abs(sum - 1) > 1e-6) throw new Error(`shopOdds level ${level} có tổng ${sum}, cần 1`)
  }
}
