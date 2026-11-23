import assert from "node:assert/strict"
import test from "node:test"
import { autoLine, createSetIndex } from "./autoline.js"

const SET = {
  champions: [
    { id: "a1", traits: ["Alpha", "Beta"] },
    { id: "a2", traits: ["Alpha"] },
    { id: "a3", traits: ["Alpha", "Gamma"] },
    { id: "b1", traits: ["Beta"] },
    { id: "g1", traits: ["Gamma"] },
    { id: "d1", traits: ["Delta"] },
    { id: "x3", traits: ["Alpha", "Gamma", "Delta"] },
    { id: "u1", traits: ["Solo"] },
  ],
  traits: [
    { name: "Alpha", breakpoints: [2, 4] },
    { name: "Beta", breakpoints: [3] },
    { name: "Gamma", breakpoints: [2] },
    { name: "Delta", breakpoints: [2] },
    { name: "Solo", breakpoints: [1] },
  ],
}
const index = createSetIndex(SET)
const unit = (id) => ({ id, cost: 1, copiesOwned: 0, priority: 0 })
const rate = (state) => Object.fromEntries(autoLine(index, state))

test("a shop unit sharing a breakpoint with the board, and the board unit itself, are rated 2", () => {
  const state = {
    board: [{ id: "a1", star: 1 }],
    shop: [unit("a2"), unit("g1"), unit("u1"), unit("a1"), unit("zz")],
  }
  assert.deepEqual(rate(state), { a2: 2, a1: 2 })
})

test("a shared trait below its next breakpoint is rated 1 per trait", () => {
  const state = { board: [{ id: "a1", star: 1 }, { id: "a2", star: 1 }], shop: [unit("a3"), unit("b1")] }
  assert.deepEqual(rate(state), { a3: 1, b1: 1 })
})

test("two shared traits that both hit a breakpoint add up to 4", () => {
  const state = { board: [{ id: "a2", star: 1 }, { id: "g1", star: 1 }], shop: [unit("a3")] }
  assert.deepEqual(rate(state), { a3: 4 })
})

test("a board with no usable ids gives an empty line", () => {
  assert.deepEqual(rate({ board: [{ championName: "a1" }], shop: [unit("a2")] }), {})
})

test("bench units are rated against the board; units that do not fit get nothing", () => {
  const state = { board: [{ id: "a1", star: 1 }], bench: [unit("g1"), unit("a2"), null] }
  assert.deepEqual(rate(state), { a2: 2 })
})

test("ratings are capped at 5", () => {
  const state = { board: [{ id: "a2", star: 1 }, { id: "g1", star: 1 }, { id: "d1", star: 1 }], shop: [unit("x3")] }
  assert.deepEqual(rate(state), { x3: 5 })
})
