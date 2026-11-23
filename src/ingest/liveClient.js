import https from "node:https"

const BASE = "https://127.0.0.1:2999/liveclientdata"
const agent = new https.Agent({
  keepAlive: true,
  maxSockets: 1,
  rejectUnauthorized: false,
})

// GET a path on the Live Client and parse JSON. Rejects on non-200, timeout or bad JSON.
export function getJson(path, timeoutMs) {
  return new Promise((resolve, reject) => {
    const req = https.request(
      `${BASE}${path}`,
      { agent, method: "GET", timeout: timeoutMs, rejectUnauthorized: false },
      (res) => {
        const chunks = []
        res.on("data", (chunk) => chunks.push(chunk))
        res.on("end", () => {
          if (res.statusCode !== 200) {
            reject(new Error(`live client ${res.statusCode}`))
            return
          }
          try {
            resolve(JSON.parse(Buffer.concat(chunks).toString("utf8")))
          } catch (error) {
            reject(error)
          }
        })
      },
    )
    req.on("timeout", () => {
      req.destroy(new Error("live client timeout"))
    })
    req.on("error", reject)
    req.end()
  })
}

// Maps a raw /allgamedata payload to the state shape used by decide().
// Field paths below are NOT verified for TFT; they are the guessed locations.
// Any field the payload lacks is listed in `missing` and gets a fallback value,
// so the coach can report it instead of using the fallback silently.
export function toState(payload) {
  const player = payload?.activePlayer ?? {}
  const stats = payload?.gameData ?? payload?.gameStats ?? {}
  const goldRaw = player.currentGold ?? player.gold
  const levelRaw = player.level ?? player.xp?.level
  const hpRaw = player.championStats?.currentHealth ?? player.health
  const stageRaw = stats.round ?? stats.stage
  const shopRaw = payload?.shop ?? player.shop

  const missing = []
  if (goldRaw === undefined) missing.push("gold")
  if (levelRaw === undefined) missing.push("level")
  if (hpRaw === undefined) missing.push("hp")
  if (stageRaw === undefined) missing.push("stage")
  if (!Array.isArray(shopRaw)) missing.push("shop")

  return {
    level: levelRaw === undefined ? 1 : num(levelRaw),
    gold: num(goldRaw),
    hp: hpRaw === undefined ? 100 : num(hpRaw),
    stage: stageNumber(stageRaw),
    shop: normalizeShop(shopRaw),
    target: null,
    missing,
  }
}

function normalizeShop(shop) {
  if (!Array.isArray(shop)) return null
  const slots = [null, null, null, null, null]
  for (let i = 0; i < 5 && i < shop.length; i++) {
    const unit = shop[i]
    if (!unit || typeof unit !== "object") continue
    const cost = num(unit.cost ?? unit.rarity)
    const id = unit.id ?? unit.name ?? unit.character_id
    if (!id || !cost) continue
    slots[i] = {
      id: String(id),
      cost,
      copiesOwned: num(unit.copiesOwned),
      priority: num(unit.priority),
    }
  }
  return slots
}

function stageNumber(value) {
  if (typeof value === "number") return value | 0
  if (typeof value !== "string") return 1
  const head = Number.parseInt(value, 10)
  return Number.isFinite(head) ? head : 1
}

function num(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

export async function readLiveState(timeoutMs = 150) {
  const payload = await getJson("/allgamedata", timeoutMs)
  return toState(payload)
}
