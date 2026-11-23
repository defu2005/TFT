import { createApp } from "../src/app.js"

const app = createApp(
  {
    source: "standalone",
    logPath: "logs/decisions-live-test.jsonl",
    intervalMs: 200,
  },
  {
    onTick: (record) => {
      console.log(`[LIVE ENGINE TICK] Action: ${record.decision.action.toUpperCase()} (Slot ${record.decision.slot})`)
      console.log(`  State: Level ${record.state.level} | Gold ${record.state.gold}g | HP ${record.state.hp} | Stage ${record.state.stage}`)
      console.log(`  Reason: ${record.reason.text}`)
      console.log(`  Time: ${record.ts}`)
      app.coach.stop()
      process.exit(0)
    },
    onError: (err) => {
      console.error("Coach error:", err)
      process.exit(1)
    }
  }
)

console.log("Khởi động Coach Engine với nguồn Standalone Live...")
app.coach.start()
