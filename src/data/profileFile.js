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
  for (const field of INHERITABLE) {
    if (base[field] !== undefined) {
      tables[field] = structuredClone(base[field])
    } else {
      if (maxCost !== DEFAULT_PROFILE.maxCost) throw new Error(`maxCost ${maxCost} cần ${field} trong base`)
      tables[field] = structuredClone(DEFAULT_PROFILE[field])
      caveats.push(`${field} lấy từ mặc định (rules.js), không có trong file set`)
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
  let applied = patches
  let selected = patches.length ? patches[patches.length - 1].version : null
  if (patchVersion != null) {
    if (!patches.some((p) => compareVersions(p.version, patchVersion) === 0)) throw new Error(`không có bản vá ${patchVersion} trong file set`)
    applied = patches.filter((p) => compareVersions(p.version, patchVersion) <= 0)
    selected = patchVersion
  }

  let maxCostNow = maxCost
  for (const patch of applied) {
    if (patch.maxCost !== undefined) maxCostNow = patch.maxCost
    const where = `bản vá ${patch.version}`
    for (const [level, row] of Object.entries(patch.shopOdds ?? {})) {
      checkIndexKeys({ [level]: row }, 99, `${where} shopOdds`)
      tables.shopOdds[Number(level)] = row
    }
    checkIndexKeys(patch.poolCopies ?? {}, maxCostNow, `${where} poolCopies`)
    checkIndexKeys(patch.champsPerCost ?? {}, maxCostNow, `${where} champsPerCost`)
    for (const [cost, value] of Object.entries(patch.poolCopies ?? {})) tables.poolCopies[Number(cost)] = value
    for (const [cost, value] of Object.entries(patch.champsPerCost ?? {})) tables.champsPerCost[Number(cost)] = value
    for (const note of patch.unmodelled ?? []) caveats.push(`chưa mô hình (bản ${patch.version}): ${note}`)
  }

  validate(tables, maxCostNow, caveats)
  return Object.freeze({
    set: file.set,
    patch: selected,
    maxCost: maxCostNow,
    shopOdds: Object.freeze(tables.shopOdds),
    poolCopies: Object.freeze(tables.poolCopies),
    champsPerCost: Object.freeze(tables.champsPerCost),
    caveats: Object.freeze(caveats),
  })
}

function validate(tables, maxCost, caveats) {
  if (tables.poolCopies.length !== maxCost + 1) throw new Error(`poolCopies cần ${maxCost + 1} phần tử`)
  if (tables.champsPerCost.length !== maxCost + 1) throw new Error(`champsPerCost cần ${maxCost + 1} phần tử`)
  const odds = tables.shopOdds
  for (let level = 1; level < odds.length; level++) {
    const row = odds[level]
    if (!Array.isArray(row) || row.length !== maxCost) throw new Error(`shopOdds level ${level} cần một hàng ${maxCost} phần tử`)
    if (row.some((p) => typeof p !== "number" || p < 0 || p > 1)) throw new Error(`shopOdds level ${level} có giá trị ngoài [0, 1]`)
    const sum = row.reduce((a, b) => a + b, 0)
    if (Math.abs(sum - 1) > 1e-6) throw new Error(`shopOdds level ${level} có tổng ${sum}, cần 1`)
  }
  const top = odds.length - 1
  if (top < DEFAULT_PROFILE.shopOdds.length - 1) {
    caveats.push(`bảng odds chỉ đến level ${top}; level cao hơn trả xác suất 0`)
  }
}
