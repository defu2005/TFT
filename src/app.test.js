import assert from "node:assert/strict"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import test from "node:test"
import { createApp, loadConfig, parseRules } from "./app.js"

const SET17 = path.join(import.meta.dirname, "data", "set17.json")

function replayConfig(extra) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-app-"))
  return loadConfig({ TFT_SOURCE: "replay", TFT_LOG: path.join(dir, "d.jsonl"), ...extra })
}

test("the auto line needs a set file", () => {
  assert.throws(() => createApp(replayConfig({ TFT_AUTO_LINE: "1" })), /TFT_SET_FILE/)
})

test("the auto line is off by default and on with a set file", () => {
  assert.equal(createApp(replayConfig({})).coach.getState().autoLine, false)
  assert.equal(createApp(replayConfig({ TFT_AUTO_LINE: "1", TFT_SET_FILE: SET17 })).coach.getState().autoLine, true)
})

test("the auto line on the real set file buys a shop unit that shares a trait with the board", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-real-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [
        {
          level: 7,
          gold: 20,
          hp: 80,
          stage: 3,
          target: null,
          shop: [{ id: "TFT17_Briar", cost: 1, copiesOwned: 0, priority: 0 }, null, null, null, null],
          board: [{ id: "TFT17_Belveth", star: 1 }],
        },
      ],
    }),
  )
  const config = replayConfig({ TFT_REPLAY: fixture, TFT_AUTO_LINE: "1", TFT_SET_FILE: SET17 })
  const { coach } = createApp(config)
  const record = await coach.tick()
  assert.equal(record.decision.action, "buy")
  assert.equal(record.decision.slot, 0)
  assert.ok(record.reason.factors.autoLine.TFT17_Briar >= 1)
})

test("the auto line on the Set 18 file rates a shop unit that shares a trait with the board", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-set18-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [
        {
          level: 7,
          gold: 20,
          hp: 80,
          stage: 3,
          target: null,
          shop: [{ id: "DA_18_Xayah", cost: 1, copiesOwned: 0, priority: 0 }, null, null, null, null],
          board: [{ id: "DA_18_Ornn", star: 1 }],
        },
      ],
    }),
  )
  const config = replayConfig({ TFT_REPLAY: fixture, TFT_AUTO_LINE: "1", TFT_SET_FILE: path.join(import.meta.dirname, "data", "set18.json") })
  const { coach } = createApp(config)
  const record = await coach.tick()
  assert.equal(record.decision.action, "buy")
  assert.equal(record.decision.slot, 0)
  assert.ok(record.reason.factors.autoLine.DA_18_Xayah >= 1)
})

test("auto line reports shop or board ids that the set file does not know", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-mismatch-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [
        {
          level: 7,
          gold: 20,
          hp: 80,
          stage: 3,
          target: null,
          shop: [{ id: "DA_18_Xayah", cost: 1, copiesOwned: 0, priority: 0 }, null, null, null, null],
          board: [{ id: "TFT17_Belveth", star: 1 }],
        },
      ],
    }),
  )
  const config = replayConfig({ TFT_REPLAY: fixture, TFT_AUTO_LINE: "1", TFT_SET_FILE: SET17 })
  const { coach } = createApp(config)
  const record = await coach.tick()
  assert.deepEqual(record.reason.factors.setMismatch, { count: 1, ids: ["DA_18_Xayah"], missingId: 0, boardMissing: false })
  assert.ok(record.reason.caveats.some((c) => c.includes("bỏ qua")))
})

test("TFT_RULES parses names into flags, rejects unknown names, and is null when unset", () => {
  assert.equal(parseRules(undefined), null)
  assert.equal(parseRules(""), null)
  assert.deepEqual(parseRules("keepInterest, guideLevels"), { keepInterest: true, earlyLevel: false, guideLevels: true })
  assert.throws(() => parseRules("keepInterest,nope"), /nope/)
})

// One frame, no target: rule 3 pin state (level 7, stage 4, 50 gold, empty shop).
function guideFrame() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-rules-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({ frames: [{ level: 7, gold: 50, hp: 80, stage: 4, target: null, shop: [null, null, null, null, null] }] }),
  )
  return fixture
}

test("with TFT_RULES unset the tick levels up and no rules are reported", async () => {
  const { coach } = createApp(replayConfig({ TFT_REPLAY: guideFrame() }))
  const record = await coach.tick()
  assert.equal(record.decision.action, "xp")
  assert.equal(record.reason.factors.rules, undefined)
  assert.equal(coach.getState().rules, null)
})

test("with TFT_RULES=guideLevels the tick holds and reports the rule", async () => {
  const { coach } = createApp(replayConfig({ TFT_REPLAY: guideFrame(), TFT_RULES: "guideLevels" }))
  const record = await coach.tick()
  assert.equal(record.decision.action, "hold")
  assert.equal(record.reason.factors.rules.guideLevels, true)
  assert.equal(coach.getState().rules.guideLevels, true)
})

test("a profile file reaches the decision through createApp; TFT_PATCH picks the overlay and the odds caveat names it", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-profile-"))
  const profilePath = path.join(dir, "set.json")
  const shop17 = [0, [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [0.75, 0.25, 0, 0, 0], [0.55, 0.3, 0.15, 0, 0], [0.45, 0.33, 0.2, 0.02, 0], [0.3, 0.4, 0.25, 0.05, 0], [0.19, 0.3, 0.4, 0.1, 0.01], [0.15, 0.2, 0.32, 0.3, 0.03], [0.1, 0.17, 0.25, 0.33, 0.15]]
  fs.writeFileSync(
    profilePath,
    JSON.stringify({
      set: "TEST",
      base: { shopOdds: shop17, poolCopies: [0, 30, 25, 18, 10, 9], champsPerCost: [0, 13, 13, 13, 12, 8] },
      patches: [{ version: "16.9" }, { version: "16.20", shopOdds: { 8: [0.5, 0.2, 0.1, 0.1, 0.1] } }],
    }),
  )
  const frame = path.join(dir, "frame.json")
  fs.writeFileSync(frame, JSON.stringify({ frames: [{ level: 8, gold: 30, hp: 80, stage: 5, target: null, shop: [{ id: "X", cost: 1, copiesOwned: 0, priority: 1 }, null, null, null, null] }] }))
  const base = { TFT_SOURCE: "replay", TFT_REPLAY: frame, TFT_LOG: path.join(dir, "d.jsonl"), TFT_PROFILE_FILE: profilePath }

  const older = createApp(loadConfig({ ...base, TFT_PATCH: "16.9" }))
  const newer = createApp(loadConfig({ ...base, TFT_PATCH: "16.20" }))
  const a = await older.coach.tick()
  const b = await newer.coach.tick()
  assert.equal(newer.coach.getState().profile.requested, "16.20")
  assert.equal(newer.coach.getState().profile.applied, "16.20")
  assert.equal(b.reason.factors.profile.set, "TEST")
  assert.notEqual(a.decision.hit, b.decision.hit)
  assert.ok(b.reason.caveats.some((c) => /set TEST, bản yêu cầu 16.20, bản áp dụng 16.20/.test(c)))

  assert.throws(() => createApp(loadConfig({ TFT_SOURCE: "replay", TFT_PATCH: "16.20", TFT_LOG: path.join(dir, "e.jsonl") })), /TFT_PROFILE_FILE/)
})

test("auto line reports board units that have no id at all", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-noid-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [
        {
          level: 7,
          gold: 20,
          hp: 80,
          stage: 3,
          target: null,
          shop: [{ id: "TFT17_Briar", cost: 1, copiesOwned: 0, priority: 0 }, null, null, null, null],
          board: [{ star: 1 }],
        },
      ],
    }),
  )
  const config = replayConfig({ TFT_REPLAY: fixture, TFT_AUTO_LINE: "1", TFT_SET_FILE: SET17 })
  const { coach } = createApp(config)
  const record = await coach.tick()
  assert.equal(record.reason.factors.setMismatch.missingId, 1)
  assert.ok(record.reason.caveats.some((c) => c.includes("không có id")))
})

test("auto line rates a shop unit against a standalone-shaped board (championName, starLevel)", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-standalone-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [
        {
          level: 7,
          gold: 20,
          hp: 80,
          stage: 3,
          target: null,
          shop: [{ id: "DA_18_Xayah", cost: 1, copiesOwned: 0, priority: 0 }, null, null, null, null],
          board: [{ championName: "DA_18_Ornn", starLevel: 1, price: 1 }],
        },
      ],
    }),
  )
  const config = replayConfig({ TFT_REPLAY: fixture, TFT_AUTO_LINE: "1", TFT_SET_FILE: path.join(import.meta.dirname, "data", "set18.json") })
  const { coach } = createApp(config)
  const record = await coach.tick()
  assert.ok(record.reason.factors.autoLine.DA_18_Xayah >= 1)
  assert.equal(record.reason.factors.setMismatch, undefined)
})

test("auto line says so when the source sends no board at all", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-noboard-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [{ level: 7, gold: 20, hp: 80, stage: 3, target: null, shop: [{ id: "TFT17_Briar", cost: 1, copiesOwned: 0, priority: 0 }, null, null, null, null] }],
    }),
  )
  const config = replayConfig({ TFT_REPLAY: fixture, TFT_AUTO_LINE: "1", TFT_SET_FILE: SET17 })
  const { coach } = createApp(config)
  const record = await coach.tick()
  assert.equal(record.reason.factors.setMismatch.boardMissing, true)
  assert.ok(record.reason.caveats.some((c) => c.includes("không gửi bàn đấu")))
})

// Riot 18.7 moved Ivern to Elderwood (add-only overlay). Without the overlay Ivern shares no trait with
// an Ornn board, so the auto line does not rate it; with the overlay it does.
function ivernFrame() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-overlay-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [
        {
          level: 7,
          gold: 20,
          hp: 80,
          stage: 3,
          target: null,
          shop: [{ id: "DA_18_Ivern", cost: 5, copiesOwned: 0, priority: 0 }, null, null, null, null],
          board: [{ id: "DA_18_Ornn", star: 1 }],
        },
      ],
    }),
  )
  return fixture
}

const SET18 = path.join(import.meta.dirname, "data", "set18.json")
const OVERLAY = path.join(import.meta.dirname, "data", "overlays", "set18-riot-18-7.json")

test("the trait overlay is off by default: Ivern shares no trait with an Ornn board", async () => {
  const { coach, traitOverlay } = createApp(replayConfig({ TFT_REPLAY: ivernFrame(), TFT_AUTO_LINE: "1", TFT_SET_FILE: SET18 }))
  const record = await coach.tick()
  assert.equal(record.reason.factors.autoLine?.DA_18_Ivern, undefined)
  assert.equal(traitOverlay, null)
  assert.equal(record.reason.factors.traitOverlay, undefined)
  assert.equal(coach.getState().traitOverlay, null)
})

test("TFT_TRAIT_OVERLAY adds Elderwood to Ivern and the auto line rates it", async () => {
  const config = replayConfig({ TFT_REPLAY: ivernFrame(), TFT_AUTO_LINE: "1", TFT_SET_FILE: SET18, TFT_TRAIT_OVERLAY: OVERLAY })
  const { coach, traitOverlay } = createApp(config)
  const record = await coach.tick()
  assert.ok(record.reason.factors.autoLine.DA_18_Ivern >= 1)
  assert.deepEqual(traitOverlay, { set: "18", verified: false, applied: 2, file: OVERLAY })
  assert.deepEqual(record.reason.factors.traitOverlay, { set: "18", verified: false, applied: 2 })
  assert.ok(record.reason.caveats.some((c) => c.includes("chưa xác minh")))
  assert.deepEqual(coach.getState().traitOverlay, { set: "18", verified: false, applied: 2 })
})

test("TFT_TRAIT_OVERLAY without TFT_AUTO_LINE is refused", () => {
  assert.throws(() => createApp(replayConfig({ TFT_TRAIT_OVERLAY: OVERLAY })), /TFT_AUTO_LINE/)
})

// HUD reader frame with unreadable gold (standalone contract): no buy, no roll, no xp, and the flag reaches the record.
test("a frame with unknown gold holds and records the flag; a null price is not bought", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-hudgold-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [
        {
          level: 7,
          gold: null,
          hudGoldUnknown: true,
          hp: 80,
          stage: 3,
          freeRolls: 2,
          target: { id: "DA_18_Ivern", cost: 5, copiesLeft: 10, priority: 1, champsAtCost: 13 },
          shop: [{ id: "DA_18_Ornn", cost: 1, price: null, copiesOwned: 0, priority: 1 }, null, null, null, null],
          board: [{ id: "DA_18_Ornn", star: 1 }],
        },
      ],
    }),
  )
  const { coach } = createApp(replayConfig({ TFT_REPLAY: fixture }))
  const record = await coach.tick()
  assert.equal(record.decision.action, "hold")
  assert.equal(record.state.hudGoldUnknown, true)
})

// Standalone source with no HUD and no snapshot: gold and level are estimates, and the record must say so in its caveats.
test("standalone without a HUD reader: gold and level are unknown (null), named in the caveats, not estimated", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-nohud-"))
  const config = {
    ...replayConfig({}),
    source: "standalone",
    standaloneOptions: { eogPath: path.join(dir, "no-eog.json"), hudPath: path.join(dir, "no-hud.json") },
  }
  const { coach } = createApp(config)
  const record = await coach.tick()
  const caveat = record.reason.caveats.find((c) => c.startsWith("thiếu trường từ nguồn"))
  assert.ok(caveat, "a missing-field caveat is present")
  assert.ok(caveat.includes("gold") && caveat.includes("level"))
  assert.equal(record.state.gold, null)
  assert.equal(record.state.level, null)
  assert.ok(record.reason.text.includes("vàng chưa biết nên không mua, roll hay xp"))
  assert.ok(record.reason.text.includes("cấp chưa biết nên không roll hay xp"))
  assert.ok(!record.reason.text.includes("mặc định cho gold"))
})

// Bare nulls from a source (no flags): the coach sets the flags, so nothing is rolled, bought or leveled on a zero.
test("bare null gold and level (no flags) reach the record as unknown and decide nothing", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-barenull-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [
        {
          level: null,
          gold: null,
          hp: 80,
          stage: 3,
          freeRolls: 2,
          target: { id: "DA_18_Ivern", cost: 1, copiesLeft: 10, priority: 1, champsAtCost: 13 },
          shop: [{ id: "DA_18_Ivern", cost: 1, price: 1, copiesOwned: 0, priority: 1 }, null, null, null, null],
        },
      ],
    }),
  )
  const { coach } = createApp(replayConfig({ TFT_REPLAY: fixture }))
  const record = await coach.tick()
  assert.equal(record.state.hudGoldUnknown, true)
  assert.equal(record.state.hudLevelUnknown, true)
  assert.equal(record.decision.action, "hold")
  assert.equal(record.decision.hit, null)
  assert.equal(record.reason.factors.gold, null)
  assert.equal(record.reason.factors.level, null)
})

// Hand-read frames from third-party VOD 2924500482 (boxbox, patch 18.6), 1505 s, 2105 s, 2705 s. Names read from the
// cards and matched to set18.json; the HUD shows the cost on each card, which equals the tier, so no price is given.
// Gold, level, HP and stage are read from the HUD. The rightmost slot in frame 3 is empty because a Wisp card was bought there (gold 14 to 10 at 2701 s), not a price.
test("hand-read 18.6 frames replay: level, gold and shop are read; the buy is on a readable slot", async () => {
  const fixture = path.join(import.meta.dirname, "data", "fixtures", "handread-18-6.json")
  const { coach } = createApp(replayConfig({ TFT_REPLAY: fixture }))
  const first = await coach.tick()
  assert.equal(first.state.level, 7)
  assert.equal(first.state.gold, 50)
  assert.equal(first.reason.factors.shopKnown, true)
  assert.equal(typeof first.decision.hit, "number")
  const second = await coach.tick()
  assert.equal(second.state.level, 9)
  assert.equal(second.state.gold, 14)
  assert.ok(second.state.shop.some((u) => u?.id === "DA_Brambleback18"))
  const third = await coach.tick()
  assert.equal(third.state.gold, 10)
  assert.equal(third.decision.action, "buy")
  assert.equal(third.decision.slot, 0)
})

// Gold and level keys omitted (no flag, no null): no roll or xp on the coerced zero, even with free rolls. Gold 30 with level unknown still buys (the engine's contract), with hit null.
test("omitted gold and level keys: no roll or xp; a buy with known gold is allowed and carries no probability", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-omitted-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [
        {
          hp: 80,
          stage: 3,
          freeRolls: 2,
          target: { id: "DA_18_Zed", cost: 1, copiesLeft: 10, priority: 1, champsAtCost: 13 },
          shop: [{ id: "DA_18_Ivern", cost: 1, copiesOwned: 0, priority: 1 }, null, null, null, null],
        },
        {
          hp: 80,
          stage: 3,
          gold: 30,
          freeRolls: 0,
          target: { id: "DA_18_Zed", cost: 1, copiesLeft: 10, priority: 1, champsAtCost: 13 },
          shop: [{ id: "DA_18_Ivern", cost: 1, copiesOwned: 0, priority: 1 }, null, null, null, null],
        },
      ],
    }),
  )
  const { coach } = createApp(replayConfig({ TFT_REPLAY: fixture }))
  const first = await coach.tick()
  assert.equal(first.decision.action, "hold")
  const second = await coach.tick()
  assert.equal(second.decision.action, "buy")
  assert.equal(second.decision.slot, 0)
  assert.equal(second.reason.factors.level, null)
  assert.equal(second.decision.hit, null)
  // Gold is known here, so the buy stands; the caveat must say only what is unknown.
  assert.match(second.reason.text, /cấp chưa biết nên không roll hay xp/)
  assert.doesNotMatch(second.reason.text, /vàng chưa biết/)
})

// Level unknown (HUD): the buy is still allowed, but no probability is reported or computed.
test("unknown level: decision.hit is null and the reason text states no probability", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-hudlevel-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [
        {
          level: null,
          hudLevelUnknown: true,
          gold: 50,
          hp: 80,
          stage: 3,
          target: { id: "DA_18_Ivern", cost: 5, copiesLeft: 10, priority: 1, champsAtCost: 13 },
          shop: [{ id: "DA_18_Ornn", cost: 1, price: 1, copiesOwned: 0, priority: 1 }, null, null, null, null],
          board: [{ id: "DA_18_Ornn", star: 1 }],
        },
      ],
    }),
  )
  const { coach } = createApp(replayConfig({ TFT_REPLAY: fixture }))
  const record = await coach.tick()
  assert.equal(record.decision.action, "buy")
  assert.equal(record.decision.hit, null)
  assert.ok(!record.reason.text.includes("%"))
  assert.ok(record.reason.text.includes("chưa đọc được cấp"))
})

// Partial HUD (from the handoff's contract): gold confirmed, level unknown, three shop slots unreadable.
test("partial HUD: level and unreadable shop slots are reported as unknown, not as numbers", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-partial-"))
  const fixture = path.join(dir, "frame.json")
  fs.writeFileSync(
    fixture,
    JSON.stringify({
      frames: [
        {
          level: null,
          hudLevelUnknown: true,
          gold: 55,
          hp: 80,
          stage: 3,
          shopUnknownSlots: [0, 2, 4],
          target: { id: "DA_18_Ornn", cost: 1, copiesLeft: 30, priority: 10, champsAtCost: 14 },
          shop: [null, { id: "DA_18_Ornn", cost: 1, price: 1, copiesOwned: 0, priority: 4 }, null, { id: "DA_18_Varus", cost: 1, price: 1, copiesOwned: 0, priority: 0 }, null],
          board: [{ id: "DA_18_Ornn", star: 1 }],
        },
      ],
    }),
  )
  const { coach } = createApp(replayConfig({ TFT_REPLAY: fixture, TFT_AUTO_LINE: "1", TFT_SET_FILE: SET18 }))
  const record = await coach.tick()
  assert.equal(record.reason.factors.level, null)
  assert.equal(record.reason.factors.gold, 55)
  assert.equal(record.reason.factors.shopKnown, false)
  assert.equal(record.known.shop, false)
  assert.equal(record.decision.action, "buy")
  assert.equal(record.decision.slot, 1)
  assert.equal(record.decision.hit, null)
})

test("a shop slot the reader could not read is named in the caveat, and the buy stays on a readable slot", async () => {
  const fixture = JSON.parse(fs.readFileSync(path.join(import.meta.dirname, "data", "fixtures", "handread-18-6.json"), "utf8"))
  fixture.frames = [{ ...fixture.frames[2], shopUnknownSlots: [4] }]
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-unk-"))
  const file = path.join(dir, "unk.json")
  fs.writeFileSync(file, JSON.stringify(fixture))
  const { coach } = createApp(loadConfig({ TFT_SOURCE: "replay", TFT_REPLAY: file, TFT_LOG: path.join(dir, "d.jsonl") }))
  const record = await coach.tick()
  assert.equal(record.reason.factors.shopKnown, false)
  assert.match(record.reason.text, /ô shop chưa đọc được: ô 5/)
  assert.ok(record.reason.caveats.some((c) => c.includes("ô 5")))
  assert.equal(record.decision.action, "buy")
  assert.equal(record.decision.slot, 0)
  assert.doesNotMatch(record.reason.text, /roll sẽ bỏ/)
})

test("the same frame without an unread-slot flag has no unread-slot caveat", async () => {
  const fixture = JSON.parse(fs.readFileSync(path.join(import.meta.dirname, "data", "fixtures", "handread-18-6.json"), "utf8"))
  fixture.frames = [fixture.frames[2]]
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "tft-noflag-"))
  const file = path.join(dir, "noflag.json")
  fs.writeFileSync(file, JSON.stringify(fixture))
  const { coach } = createApp(loadConfig({ TFT_SOURCE: "replay", TFT_REPLAY: file, TFT_LOG: path.join(dir, "d.jsonl") }))
  const record = await coach.tick()
  assert.equal(record.reason.factors.shopKnown, true)
  assert.doesNotMatch(record.reason.text, /ô shop chưa đọc được/)
  assert.ok(!record.reason.caveats.some((c) => c.includes("ô shop chưa đọc")))
})
