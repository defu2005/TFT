import fs from "node:fs"
import path from "node:path"

const DEFAULT_EOG = path.join(process.env.LOCALAPPDATA || "", "TFT", "Saved", "Logs", "TFTEoGStats.json")
const DEFAULT_LOG = path.join(process.env.LOCALAPPDATA || "", "TFT", "Saved", "Logs", "TFT.log")
const DEFAULT_EXTRACTED = path.join(process.cwd(), "captures", "extracted-live.jsonl")
const DEFAULT_HUD = path.join(process.cwd(), "captures", "hud-live.json")
const HUD_MAX_AGE_MS = 2_000

// Known Set 18 champion costs for accurate shop & economy calculations
export const CHAMPION_COSTS = {
  DA_18_Ornn: 1,
  DA_Karma18: 1,
  DA_18_Sentry: 1,
  DA_18_Rakan: 1,
  DA_18_Varus: 1,
  DA_18_Yorick: 1,
  DA_18_KhaZix: 1,
  DA_18_Kayle: 1,
  DA_18_Yunara: 2,
  DA_Scuttlecrab18: 2,
  DA_18_Sejuani: 2,
  DA_18_Elise: 2,
  DA_18_Alistar: 2,
  DA_18_Warwick: 3,
  DA_18_Xayah: 3,
  DA_18_Diana: 4,
}

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
      const missing = []
      const partialHud = hud?.hudSchema === 2

      // Compute Level (board capacity gives minimum level)
      const levelKnown = Number.isInteger(hud?.level) && hud.level > 0
      let level = Math.max(1, boardPieces.length)
      if (levelKnown) {
        level = hud.level
      } else {
        missing.push("level")
        if (partialHud) level = null
        else if (stage > 1 && level < 3) level = stage >= 4 ? 6 : stage >= 3 ? 5 : 4
      }

      // Compute HP
      const hp = typeof activePlayer?.health === "number" ? activePlayer.health : 100

      // Compute Gold
      const goldKnown = Number.isInteger(hud?.gold) && hud.gold >= 0
      let gold
      if (goldKnown) {
        gold = hud.gold
      } else {
        missing.push("gold")
        gold = partialHud ? null : Math.min(50, Math.max(5, (stage - 1) * 12 + 10))
      }

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
            cost: slot.cost || CHAMPION_COSTS[slot.id] || 1,
            ...(Object.hasOwn(slot, "price")
              ? { price: Number.isInteger(slot.price) && slot.price >= 0 && slot.price <= 999 ? slot.price : null }
              : {}),
            copiesOwned: copiesMap[slot.id] || 0,
            priority: slot.priority || 0,
          }
        })
      }
      if (shopUnknownSlots.length === 5) shop = null
      if (!shop || shopUnknownSlots.length) missing.push("shop")

      if (!snapshot) {
        missing.push("snapshot")
      }

      return {
        level,
        gold,
        hp,
        stage,
        shop,
        ...(partialHud && !goldKnown ? { hudGoldUnknown: true } : {}),
        ...(partialHud && !levelKnown ? { hudLevelUnknown: true } : {}),
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

function validShopUnit(slot) {
  return typeof slot?.id === "string" && slot.id.length > 0 &&
    Number.isInteger(slot.cost) && slot.cost >= 1 && slot.cost <= 5
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
