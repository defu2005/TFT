import fs from "node:fs"
import path from "node:path"

const DEFAULT_EOG = path.join(process.env.LOCALAPPDATA || "", "TFT", "Saved", "Logs", "TFTEoGStats.json")
const DEFAULT_LOG = path.join(process.env.LOCALAPPDATA || "", "TFT", "Saved", "Logs", "TFT.log")
const DEFAULT_EXTRACTED = path.join(process.cwd(), "captures", "extracted-live.jsonl")
const DEFAULT_HUD = path.join(process.cwd(), "captures", "hud-live.json")
const HUD_MAX_AGE_MS = 2_000

// Champion costs come from the set file, not a hand-typed table. An id missing from the set file has no cost, so its slot is unread.
const SET18_FILE = path.join(import.meta.dirname, "..", "data", "set18.json")
export const SET18_COSTS = Object.fromEntries(
  (JSON.parse(fs.readFileSync(SET18_FILE, "utf8")).champions ?? []).map((c) => [c.id, c.cost]),
)

export function createStandaloneSource(options = {}) {
  const eogPath = options.eogPath || DEFAULT_EOG
  const logPath = options.logPath || DEFAULT_LOG
  const extractedPath = options.extractedPath || DEFAULT_EXTRACTED
  const hudPath = options.hudPath || DEFAULT_HUD
  const playerName = options.playerName || process.env.TFT_PLAYER || null

  return {
    kind: "standalone",
    read: async () => {
      // 1. Read Snapshot (TFTEoGStats.json)
      let snapshot = null
      if (fs.existsSync(eogPath)) {
        try {
          const raw = fs.readFileSync(eogPath, "utf8")
          snapshot = JSON.parse(raw)
        } catch {
          // File may be partially written by game client, retry next tick
        }
      }

      // 2. Read HUD state (if HUD reader is running)
      let hud = null
      if (fs.existsSync(hudPath)) {
        try {
          const candidate = JSON.parse(fs.readFileSync(hudPath, "utf8"))
          if (usableHud(candidate)) hud = candidate
        } catch {}
      }

      const missing = []
      const players = snapshot?.statsBlock?.players || []
      const activePlayer = findPlayer(players, playerName)
      const gameLengthSeconds = Number(snapshot?.statsBlock?.gameLengthSeconds) || 0

      // Compute board pieces & copies owned
      const boardPieces = activePlayer?.boardPieces || []
      const copiesMap = {}
      for (const piece of boardPieces) {
        const name = piece.championName
        const stars = piece.starLevel || 1
        const count = stars === 3 ? 9 : stars === 2 ? 3 : 1
        copiesMap[name] = (copiesMap[name] || 0) + count
      }

      // Compute Stage from game duration
      const stage = computeStage(gameLengthSeconds)
      if (!gameLengthSeconds) missing.push("stage")
      const partialHud = hud?.hudSchema === 2

      // Compute Level (board capacity gives minimum level)
      const levelKnown = Number.isInteger(hud?.level) && hud.level > 0
      // Unknown level is null with a flag, never a guess from the stage or the board (decision 2026-11-23).
      const level = levelKnown ? hud.level : null
      if (!levelKnown) missing.push("level")

      // Compute HP
      const hpKnown = typeof activePlayer?.health === "number"
  const hp = hpKnown ? activePlayer.health : 100
  if (!hpKnown) missing.push("hp")

      // Compute Gold
      const goldKnown = Number.isInteger(hud?.gold) && hud.gold >= 0
      // Unknown gold is null with a flag, never an estimate from the stage (decision 2026-11-23).
      const gold = goldKnown ? hud.gold : null
      if (!goldKnown) missing.push("gold")

      // Compute Shop
      let shop = null
      const shopUnknownSlots = []
      const observedSlots = partialHud ? (goldKnown ? hud.shopSlots : null) : hud?.shop
      if (Array.isArray(observedSlots) && observedSlots.length === 5) {
        shop = observedSlots.map((slot, index) => {
          if (partialHud && !validShopUnit(slot)) {
            shopUnknownSlots.push(index)
            return null
          }
          if (!slot?.id) return null
          return {
            id: slot.id,
            cost: unitCost(slot),
            ...(Object.hasOwn(slot, "price")
              ? { price: Number.isInteger(slot.price) && slot.price >= 0 && slot.price <= 999 ? slot.price : null }
              : {}),
            copiesOwned: copiesMap[slot.id] || 0,
            priority: slot.priority || 0,
          }
        })
      }
      if (shopUnknownSlots.length === 5) shop = null
      if (!shop) missing.push("shop")

      if (!snapshot) {
        missing.push("snapshot")
      }

      return {
        level,
        gold,
        hp,
        stage,
        shop,
        ...(!goldKnown ? { hudGoldUnknown: true } : {}),
        ...(!levelKnown ? { hudLevelUnknown: true } : {}),
        oddsObserved: validOddsRow(hud),
        ...(shop && shopUnknownSlots.length ? { shopUnknownSlots } : {}),
        target: null,
        missing,
        board: boardPieces,
        augments: activePlayer?.augments || [],
        gameLengthSeconds,
      }
    },
  }
}

// Observed shop odds row from the HUD (I11): five numbers in percent that sum to 100 within 1. Anything else is unread (null).
function validOddsRow(hud) {
  const row = hud?.oddsRow
  if (!Array.isArray(row) || row.length !== 5) return null
  if (!row.every((x) => Number.isFinite(x) && x >= 0 && x <= 100)) return null
  if (Math.abs(row.reduce((a, b) => a + b, 0) - 100) > 1) return null
  return row
}

function usableHud(hud) {
  if (!hud || typeof hud !== "object") return false
  if (hud.hudSchema === undefined) {
    // Preserve imported snapshots. The original Python reader always wrote
    // hudDetected alongside its hard-coded sample data.
    return !Object.hasOwn(hud, "hudDetected")
  }
  if (![1, 2].includes(hud.hudSchema) || hud.set !== 18 || hud.source !== "window" || hud.hudDetected !== true) return false
  if (!Number.isSafeInteger(hud.capturedAtMs)) return false
  const age = Date.now() - hud.capturedAtMs
  return age >= 0 && age <= HUD_MAX_AGE_MS
}

function unitCost(slot) {
  return slot?.cost ?? SET18_COSTS[slot?.id]
}

function validShopUnit(slot) {
  const cost = unitCost(slot)
  return typeof slot?.id === "string" && slot.id.length > 0 &&
    Number.isInteger(cost) && cost >= 1 && cost <= 5
}

function findPlayer(players, name) {
  if (!players || players.length === 0) return null
  if (name) {
    const found = players.find(
      (p) =>
        (p.riotIdGameName && p.riotIdGameName.toLowerCase() === name.toLowerCase()) ||
        (p.summonerName && p.summonerName.toLowerCase() === name.toLowerCase()),
    )
    if (found) return found
  }
  // Default to player with isInteractable: true or first player
  return players.find((p) => p.isInteractable) || players[0]
}

function computeStage(gameSeconds) {
  if (!gameSeconds || gameSeconds <= 90) return 1
  if (gameSeconds <= 210) return 2
  if (gameSeconds <= 360) return 3
  if (gameSeconds <= 520) return 4
  if (gameSeconds <= 700) return 5
  if (gameSeconds <= 900) return 6
  if (gameSeconds <= 1150) return 7
  return 8
}
