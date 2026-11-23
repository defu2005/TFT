// Exports the Set 18 roster from a CommunityDragon en_us dump.
// Set 18 units use the DA_ apiName prefix, so export-set.js (TFT<key>_) cannot read them.
// Usage: node scripts/export-set18.js [path-to-en_us.json]
// If meta.json sits beside the dump, its version is recorded as contentVersion.
// Default path is ../.cache/tft-en_us.json next to this repo.
// Writes src/data/set18.json. Riftbeast-trait units are included as-is; they are NOT
// filtered here, because whether they are shop units is still unverified (see docs/needs.md).
import fs from "node:fs"
import path from "node:path"

const input = process.argv[2] ? path.resolve(process.argv[2]) : new URL("../.cache/tft-en_us.json", import.meta.url).pathname
const data = JSON.parse(fs.readFileSync(input, "utf8"))
const set = data.sets["18"]
// The dump has no version field; meta.json beside it holds the content version.
const metaPath = path.join(path.dirname(input), "meta.json")
const contentVersion = fs.existsSync(metaPath) ? JSON.parse(fs.readFileSync(metaPath, "utf8")).version ?? null : null

const champs = (set.champions ?? []).filter((c) => (c.apiName ?? "").startsWith("DA_") && Array.isArray(c.traits) && c.traits.length > 0 && c.cost >= 1 && c.cost <= 5)
const traits = (set.traits ?? []).filter((t) => (t.apiName ?? "").startsWith("DA_"))
const byCost = [0, 0, 0, 0, 0]
for (const c of champs) byCost[c.cost - 1] += 1

const snapshot = {
  source: "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json",
  contentVersion,
  set: 18,
  name: "Set 18",
  nameInDump: set.name,
  note: "DA_ prefix; units with empty traits and TFT_ minions excluded; Riftbeast units included, unverified as shop units",
  championCount: champs.length,
  traitCount: traits.length,
  championsByCost: byCost,
  champions: champs.map((c) => ({ id: c.apiName, name: c.name, cost: c.cost, traits: c.traits })),
  traits: traits.map((t) => ({
    id: t.apiName,
    name: t.name,
    breakpoints: (t.effects ?? []).map((e) => e.minUnits).filter((n) => Number(n) > 0),
  })),
}

fs.writeFileSync(new URL("../src/data/set18.json", import.meta.url), JSON.stringify(snapshot))
console.log("set 18", snapshot.championCount, snapshot.traitCount, snapshot.championsByCost.join("/"), "contentVersion", contentVersion)
