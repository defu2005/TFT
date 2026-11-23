import fs from "node:fs"

const data = JSON.parse(fs.readFileSync(new URL("../.cache/tft-en_us.json", import.meta.url)))
for (const id of Object.keys(data.sets).sort((a, b) => Number(a) - Number(b))) {
  const set = data.sets[id]
  const champs = set.champions ?? []
  const prefixes = new Map()
  for (const champ of champs) {
    const idName = champ.apiName ?? ""
    const prefix = idName.split("_")[0]
    prefixes.set(prefix, (prefixes.get(prefix) ?? 0) + 1)
  }
  const top = [...prefixes.entries()].sort((a, b) => b[1] - a[1]).slice(0, 4)
  console.log(
    `id=${id} name=${set.name} champs=${champs.length} traits=${(set.traits ?? []).length} prefixes=${top.map(([k, v]) => `${k}:${v}`).join(",")}`,
  )
}
