import fs from "node:fs"

const data = JSON.parse(fs.readFileSync(new URL("../.cache/tft-en_us.json", import.meta.url)))
console.log("setData", (data.setData ?? []).map((s) => `${s.number ?? "?"} ${s.name} mutator=${s.mutator}`).join("\n"))

function exportSet(key) {
  const set = data.sets[key]
  const prefix = `TFT${key}_`
  const champs = (set.champions ?? []).filter((c) => (c.apiName ?? "").startsWith(prefix))
  const traits = (set.traits ?? []).filter((t) => (t.apiName ?? "").startsWith(prefix))
  const byCost = [0, 0, 0, 0, 0]
  for (const champ of champs) {
    if (champ.cost >= 1 && champ.cost <= 5) byCost[champ.cost - 1] += 1
  }
  return {
    source: "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json",
    set: Number(key),
    name: set.name,
    championCount: champs.length,
    traitCount: traits.length,
    championsByCost: byCost,
    champions: champs.map((c) => ({
      id: c.apiName,
      name: c.name,
      cost: c.cost,
      traits: c.traits,
    })),
    traits: traits.map((t) => ({
      id: t.apiName,
      name: t.name,
      breakpoints: (t.effects ?? []).map((e) => e.minUnits).filter((n) => Number(n) > 0),
    })),
  }
}

const snapshot = exportSet("17")
fs.writeFileSync(new URL("../src/data/set17.json", import.meta.url), JSON.stringify(snapshot))
console.log("--- set 17 ---")
console.log(snapshot.name, snapshot.championCount, snapshot.traitCount, snapshot.championsByCost.join("/"))
console.log(snapshot.champions.slice(0, 12).map((c) => `${c.cost} ${c.name} [${c.traits.join(", ")}]`).join("\n"))
console.log(snapshot.traits.slice(0, 8).map((t) => `${t.name} ${t.breakpoints.join("/")}`).join("\n"))
