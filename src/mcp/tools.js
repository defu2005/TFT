import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { z } from "zod"
import { decide } from "../engine/decide.js"
import { explain, CAVEAT_ODDS } from "../engine/reason.js"
import { hitChance, interestGold } from "../engine/odds.js"
import * as tables from "../data/profile.js"

const HERE = path.dirname(fileURLToPath(import.meta.url))

// Same wording as the coach uses for a profile file.
const PROFILE_CAVEAT = (p) => `bảng tỉ lệ shop của set ${p.set}, bản yêu cầu ${p.requested ?? "mới nhất"}, bản áp dụng ${p.applied ?? "không có"}, từ file hồ sơ, chưa xác minh`
const SET_FILE = path.join(HERE, "..", "data", "set17.json")

const targetSchema = z
  .object({
    id: z.string().optional(),
    cost: z.number().int().min(1).max(5),
    copiesLeft: z.number().int().min(0),
    priority: z.number().min(0),
    champsAtCost: z.number().int().min(1).optional(),
  })
  .nullable()

const unitSchema = z
  .object({
    id: z.string(),
    cost: z.number().int().min(1).max(5),
    copiesOwned: z.number().int().min(0).default(0),
    priority: z.number().min(0).default(0),
    poolCopies: z.number().int().min(0).optional(),
    champsAtCost: z.number().int().min(1).optional(),
    takenByOthers: z.number().int().min(0).optional(),
  })
  .nullable()

const ownedSchema = z
  .object({
    id: z.string(),
    star: z.number().int().min(1).max(3).optional(),
    priority: z.number().min(0).optional(),
    sellValue: z.number().min(0).optional(),
  })
  .nullable()

const stateSchema = {
  level: z.number().int().min(1).max(11),
  gold: z.number().int().min(0),
  hp: z.number().min(0),
  stage: z.number().int().min(1),
  shop: z.array(unitSchema).length(5).nullable().optional(),
  target: targetSchema.optional(),
  board: z.array(ownedSchema).nullable().optional(),
  freeRolls: z.number().int().min(0).optional(),
  bench: z.array(ownedSchema).nullable().optional(),
}

function asText(value) {
  return { content: [{ type: "text", text: JSON.stringify(value, null, 2) }] }
}

function loadSetSummary() {
  try {
    const data = JSON.parse(fs.readFileSync(SET_FILE, "utf8"))
    return {
      set: data.set,
      name: data.name,
      championCount: data.championCount,
      traitCount: data.traitCount,
      championsByCost: data.championsByCost,
      note: "Dữ liệu Set 17 (set cũ). Không phải set đang chơi; dùng để tham khảo cấu trúc.",
    }
  } catch (error) {
    return { error: `không đọc được ${SET_FILE}: ${error.message}` }
  }
}

// Registers every capability as an MCP tool. Tools read cached state from the coach;
// none of them triggers a read from the state source.
export function registerTools(server, { coach, rules = null, profile = null }) {
  const caveat = profile ? PROFILE_CAVEAT(profile) : CAVEAT_ODDS
  server.registerTool(
    "tft_status",
    {
      title: "Trạng thái nguồn và bộ nhớ đệm",
      description: "Nguồn dữ liệu (live hay replay), lỗi gần nhất, số lần đọc, trạng thái cache. Không đọc lại nguồn.",
      inputSchema: {},
    },
    async () => asText(coach.getState()),
  )

  server.registerTool(
    "tft_current_decision",
    {
      title: "Quyết định hiện tại kèm lý do",
      description:
        "Quyết định mới nhất từ vòng lặp realtime, lý do bằng tiếng Việt, các ứng viên và điểm số. Đọc từ cache.",
      inputSchema: {},
    },
    async () => {
      const s = coach.getState()
      if (!s.decision) return asText({ ready: false, source: s.source, note: "chưa có quyết định nào" })
      return asText({
        ready: true,
        source: s.source,
        decision: s.decision,
        reason: s.reason,
        stateHash: s.stateHash,
        latencyMs: s.latencyMs,
        updatedAt: s.updatedAt,
      })
    },
  )

  server.registerTool(
    "tft_evaluate_state",
    {
      title: "Chấm điểm một trạng thái giả định",
      description:
        "Chạy engine trên trạng thái người dùng cung cấp và trả về quyết định, lý do và ứng viên. Không ghi đè cache và không ghi log.",
      inputSchema: stateSchema,
    },
    async (args) => {
      const state = normalizeState(args)
      const out = { action: 0, slot: -1, score: 0, hit: 0, bench: -1 }
      const trace = []
      decide(state, out, trace, rules, profile)
      return asText(explain(state, out, trace, caveat))
    },
  )

  server.registerTool(
    "tft_hit_chance",
    {
      title: "Xác suất gặp tướng trong shop",
      description: "Xác suất có ít nhất một bản của tướng xuất hiện trong shop 5 ô. " + CAVEAT_ODDS + ".",
      inputSchema: {
        level: z.number().int().min(1).max(11),
        cost: z.number().int().min(1).max(5),
        copiesLeft: z.number().int().min(0),
        champsAtCost: z.number().int().min(1).optional(),
      },
    },
    async ({ level, cost, copiesLeft, champsAtCost }) =>
      asText({ hitChance: round(hitChance(level, cost, copiesLeft, champsAtCost, profile)), caveat }),
  )

  server.registerTool(
    "tft_interest",
    {
      title: "Lãi theo vàng",
      description: "Số lãi nhận được ở cuối vòng với số vàng cho trước, theo MAX_INTEREST trong rules.js.",
      inputSchema: { gold: z.number().int().min(0) },
    },
    async ({ gold }) => {
      const interest = interestGold(gold)
      const nextThreshold = interest >= tables.MAX_INTEREST ? null : (interest + 1) * 10
      return asText({ gold, interest, nextThreshold })
    },
  )

  server.registerTool(
    "tft_rules",
    {
      title: "Dữ liệu luật và bộ tướng",
      description: "Bảng tỉ lệ shop, số bản trong pool, số tướng theo cost, mốc level theo stage, và tóm tắt Set 17. Bảng tỉ lệ chưa xác minh cho Set 18.",
      inputSchema: {},
    },
    async () =>
      asText({
        shopOdds: profile ? profile.shopOdds : tables.SHOP_ODDS,
        poolCopies: profile ? profile.poolCopies : tables.POOL_COPIES,
        champsPerCost: profile ? profile.champsPerCost : tables.CHAMPS_PER_COST,
        levelByStage: tables.LEVEL_BY_STAGE,
        buyXpCost: tables.BUY_XP_COST,
        rerollCost: tables.REROLL_COST,
        maxInterest: tables.MAX_INTEREST,
        profile: profile ? { set: profile.set, requested: profile.requested, applied: profile.applied } : null,
        rules,
        verified: false,
        caveat,
        set17: loadSetSummary(),
      }),
  )

  server.registerTool(
    "tft_recent_decisions",
    {
      title: "Các quyết định đã ghi log gần nhất",
      description: "Đọc các dòng cuối của log quyết định (JSONL), mới nhất trước.",
      inputSchema: { limit: z.number().int().min(1).max(200).default(20) },
    },
    async ({ limit }) => asText({ entries: coach.recent(limit) }),
  )

  server.registerTool(
    "tft_set_target",
    {
      title: "Đặt mục tiêu tướng",
      description: "Đặt tướng đang nhắm tới (cost, số bản còn lại, ưu tiên). Gửi null để xóa. Ảnh hưởng vòng lặp kế tiếp.",
      inputSchema: { target: targetSchema },
    },
    async ({ target }) => asText({ target: coach.setTarget(target ?? null) }),
  )

  server.registerTool(
    "tft_set_line",
    {
      title: "Đặt priority cho một tướng trong line",
      description:
        "Đặt priority cho tướng (theo id trong shop). priority > 0 đưa tướng vào line để engine có thể mua; null hoặc 0 để bỏ. Ảnh hưởng vòng lặp kế tiếp. Trả về toàn bộ line hiện tại.",
      inputSchema: {
        unitId: z.string().min(1),
        priority: z.number().min(0).nullable(),
      },
    },
    async ({ unitId, priority }) => asText({ lines: coach.setLine(unitId, priority) }),
  )
}

function normalizeState(args) {
  return {
    level: args.level,
    gold: args.gold,
    hp: args.hp,
    stage: args.stage,
    shop: args.shop ?? null,
    target: args.target ?? null,
    board: args.board ?? null,
    freeRolls: args.freeRolls ?? 0,
    bench: args.bench ?? null,
  }
}

function round(value) {
  return Math.round(value * 1000) / 1000
}
