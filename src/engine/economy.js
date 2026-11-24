import { MAX_INTEREST } from "../data/rules.js"

// Gold at the start of each of the next `rounds` rounds, with income and interest added round by round.
// Interest is taken from the gold held at the start of each round, as the game does.
export function projectGold(gold, rounds, baseIncome = 5) {
  const out = []
  let g = gold
  for (let i = 0; i < rounds; i++) {
    g += baseIncome + Math.min(MAX_INTEREST, (g / 10) | 0)
    out.push(g)
  }
  return out
}
