import fs from "node:fs"

const raw = fs.readFileSync(new URL("../.cache/tft-en_us.json", import.meta.url))
const data = JSON.parse(raw)
const top = Object.keys(data)
console.log("keys", top.join(", "))
const sets = data.sets ?? data.setData
if (sets && !Array.isArray(sets)) {
  const names = Object.keys(sets)
  console.log("setIds", names.join(", "))
  const latest = names.sort((a, b) => Number(a) - Number(b)).at(-1)
  const set = sets[latest]
  console.log("latest", latest, "setKeys", Object.keys(set).join(", "))
  const champs = set.champions ?? []
  const traits = set.traits ?? []
  console.log("champions", champs.length, "traits", traits.length)
  console.log("sample", champs.slice(0, 3).map((c) => `${c.name}|${c.cost}|${c.apiName ?? c.characterName}`).join(" ; "))
} else if (Array.isArray(data.setData)) {
  console.log("setData", data.setData.length)
  const current = data.setData.filter((s) => s.mutator && !s.mutator.startsWith("TFTTutorial"))
  console.log("named", current.map((s) => `${s.number ?? s.mutator}:${s.name}`).join(" | "))
}
