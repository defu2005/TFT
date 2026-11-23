import fs from "node:fs"

const html = fs.readFileSync(process.env.TEMP + "/tft-dl.html", "utf8")
const urls = new Set()
for (const match of html.matchAll(/https?:\/\/[^"'\\\s<>]+/g)) urls.add(match[0])
for (const url of urls) {
  if (/exe|zip|installer|riotcdn/i.test(url)) console.log(url)
}
