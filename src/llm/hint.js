// The model never sits on the decision tick. A hint is computed beside it
// and can be read later. The engine ignores this module.

let latest = null
let inflight = false
let lastHash = ""

export function latestHint() {
  return latest
}

export function observe(state) {
  const hash = hashState(state)
  if (hash === lastHash || inflight) return
  lastHash = hash
  inflight = true
  setTimeout(() => {
    latest = {
      hash,
      at: Date.now(),
      text: null,
    }
    inflight = false
  }, 0)
}

function hashState(state) {
  const shop = state.shop
  let ids = ""
  if (shop) {
    for (let i = 0; i < shop.length; i++) ids += shop[i]?.id ?? "-"
  }
  return `${state.level}|${state.gold}|${state.hp}|${ids}`
}
