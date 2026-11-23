// Shop odds by player level. Index 0 is unused so level N maps to row N.
// Values are probabilities for cost 1..5. Replace this table when a set changes it.
export const SHOP_ODDS = [
  null,
  [1, 0, 0, 0, 0],
  [1, 0, 0, 0, 0],
  [0.75, 0.25, 0, 0, 0],
  [0.55, 0.30, 0.15, 0, 0],
  [0.45, 0.33, 0.20, 0.02, 0],
  [0.30, 0.40, 0.25, 0.05, 0],
  [0.19, 0.30, 0.40, 0.10, 0.01],
  [0.17, 0.24, 0.32, 0.24, 0.03],
  [0.15, 0.18, 0.25, 0.30, 0.12],
  [0.05, 0.10, 0.20, 0.40, 0.25],
  [0.01, 0.02, 0.12, 0.50, 0.35],
]

// Copies of each champion in the shared bag, by cost.
export const POOL_COPIES = [0, 30, 25, 18, 10, 9]

// Typical champion counts per cost. Used only when the set file does not say.
export const CHAMPS_PER_COST = [0, 13, 13, 13, 12, 8]

// Level the econ line aims for at the start of each stage.
export const LEVEL_BY_STAGE = [0, 2, 4, 6, 8, 8, 9, 9]

export const BUY_XP_COST = 4
export const REROLL_COST = 2
export const MAX_INTEREST = 5
