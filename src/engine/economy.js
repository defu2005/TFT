import { interestGold } from "./odds.js"

// Gold at the end of each of the next `rounds` rounds, with income and interest added round by round.
// Interest uses the gold held at the start of the round (research §14.1 example). The timing is not yet
// checked against the game, so this is a planning projection and not used in any decision.
export function projectGold(gold, rounds, baseIncome = 5) {
  const out = []
  let g = gold
  for (let i = 0; i < rounds; i++) {
    g += baseIncome + interestGold(g)
    out.push(g)
  }
  return out
}
