import fs from "node:fs"
import path from "node:path"

const DEFAULT_EOG = path.join(process.env.LOCALAPPDATA || "", "TFT", "Saved", "Logs", "TFTEoGStats.json")
const DEFAULT_LOG = path.join(process.env.LOCALAPPDATA || "", "TFT", "Saved", "Logs", "TFT.log")
const DEFAULT_EXTRACTED = path.join(process.cwd(), "captures", "extracted-live.jsonl")
const DEFAULT_HUD = path.join(process.cwd(), "captures", "hud-live.json")

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

  let lastKnownGold = 10
  let lastKnownLevel = 1
  let lastPhase = null

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
          hud = JSON.parse(fs.readFileSync(hudPath, "utf8"))
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

      // Missing fields are reported, so the coach can say what it used as a default.
      const missing = []

      // Compute Level (board capacity gives minimum level)
      let level = Math.max(1, boardPieces.length)
      if (hud && typeof hud.level === "number" && hud.level > 0) {
        level = hud.level
      } else {
        missing.push("level")
        if (stage > 1 && level < 3) level = stage >= 4 ? 6 : stage >= 3 ? 5 : 4
      }
      lastKnownLevel = level

      // Compute HP
      const hp = typeof activePlayer?.health === "number" ? activePlayer.health : 100

      // Compute Gold
      let gold = lastKnownGold
      if (hud && typeof hud.gold === "number" && hud.gold >= 0) {
        gold = hud.gold
      } else {
        missing.push("gold")
        // Base gold estimation based on stage and interest
        const baseGoldForStage = Math.min(50, Math.max(5, (stage - 1) * 12 + 10))
        gold = baseGoldForStage
      }
      lastKnownGold = gold

      // Compute Shop
      let shop = null

      if (hud && Array.isArray(hud.shop) && hud.shop.length === 5) {
        shop = hud.shop.map((slot) => {
          if (!slot || !slot.id) return null
          const cost = slot.cost || CHAMPION_COSTS[slot.id] || 1
          return {
            id: slot.id,
            cost,
            copiesOwned: copiesMap[slot.id] || 0,
            priority: slot.priority || 0,
          }
        })
      } else {
        // Shop is unknown without HUD reader
        missing.push("shop")
      }

      if (!snapshot) {
        missing.push("snapshot")
      }

      return {
        level,
        gold,
        hp,
        stage,
        shop,
        target: null,
        missing,
        board: boardPieces,
        augments: activePlayer?.augments || [],
        gameLengthSeconds,
      }
    },
  }
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
