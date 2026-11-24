// The data a decision reads: shop odds, pool sizes, champions per cost, and the largest cost in the table.
// Today every value comes from rules.js (Set 17 numbers, unverified for Set 18). A profile can replace
// these tables for a set or patch without touching the engine.
import * as rules from "./rules.js"

export * from "./rules.js"

export const DEFAULT_PROFILE = Object.freeze({
  shopOdds: rules.SHOP_ODDS,
  poolCopies: rules.POOL_COPIES,
  champsPerCost: rules.CHAMPS_PER_COST,
  maxCost: 5,
})
