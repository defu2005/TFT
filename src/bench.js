import { decide, BUY } from "./engine/decide.js"

const shop = [
  { id: "a", cost: 1, copiesOwned: 0, priority: 0 },
  { id: "b", cost: 2, copiesOwned: 1, priority: 3 },
  { id: "c", cost: 3, copiesOwned: 0, priority: 0 },
  { id: "d", cost: 4, copiesOwned: 2, priority: 5 },
  { id: "e", cost: 1, copiesOwned: 0, priority: 1 },
]
const state = {
  level: 7,
  gold: 42,
  hp: 55,
  stage: 4,
  shop,
  target: { cost: 4, copiesLeft: 6, priority: 5, champsAtCost: 12 },
}
const out = { action: 0, slot: -1, score: 0, hit: 0 }

const warmup = 20_000
const rounds = 200_000
for (let i = 0; i < warmup; i++) decide(state, out)

const started = performance.now()
for (let i = 0; i < rounds; i++) decide(state, out)
const elapsed = performance.now() - started
const per = (elapsed * 1_000_000) / rounds

if (out.action !== BUY) {
  console.error("bench expected a buy")
  process.exit(1)
}

console.log(`decisions=${rounds}`)
console.log(`total_ms=${elapsed.toFixed(2)}`)
console.log(`ns_per_decision=${per.toFixed(0)}`)
console.log(`decisions_per_sec=${Math.round(rounds / (elapsed / 1000))}`)
