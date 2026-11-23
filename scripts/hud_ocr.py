"""Read the TFT HUD from a PIL image, independently of capture and scheduling."""

from collections import Counter, OrderedDict
from concurrent.futures import ThreadPoolExecutor
import csv
from io import BytesIO, StringIO
import json
import math
import os
from pathlib import Path
import re
import subprocess
import unicodedata

from PIL import Image, ImageOps


# Coordinates relative to the visible game viewport. Profiles can override these
# for a different shop layout, HUD scale, crop, or language.
DESKTOP_PROFILE = {
    "viewport": [0, 0, 1, 1],
    "gold": [612 / 1280, 590 / 720, 635 / 1280, 614 / 720],
    "level": [159 / 1280, 596 / 720, 208 / 1280, 609 / 720],
    "shop": [[(299 + i * 135) / 1280, 700 / 720, (400 + i * 135) / 1280, 1] for i in range(5)],
    "shop_price": [[(401 + i * 135) / 1280, 704 / 720, (422 + i * 135) / 1280, 714 / 720]
                   for i in range(5)],
    "level_labels": ["Lvl", "Level", "Cấp"],
}
CATALOG = Path(__file__).resolve().parents[1] / "src/data/set18-hud.json"
ROW_HEIGHT = 78
ROW_WIDTH = 440
LEVEL_AGREEMENT_CONFIDENCE = 25
PRICE_CONFIDENCE = 75


def normalize(text):
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", text.casefold())
        if ch.isalnum()
    )


def load_profile(path):
    overrides = json.loads(Path(path).read_text()) if path else {}
    profile = {**DESKTOP_PROFILE, **overrides}
    if "shop" in overrides and "shop_price" not in overrides:
        profile["shop_price"] = None
    if len(profile["shop"]) != 5 or not profile["level_labels"]:
        raise ValueError("HUD profile needs five shop boxes and at least one level label")
    prices = profile["shop_price"]
    if prices is not None and len(prices) != 5:
        raise ValueError("HUD profile needs five shop_price boxes or null")
    for box in [profile["viewport"], profile["gold"], profile["level"], *profile["shop"], *(prices or [])]:
        if len(box) != 4:
            raise ValueError("HUD boxes need four coordinates")
        x1, y1, x2, y2 = box
        if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
            raise ValueError("HUD boxes must use increasing normalized coordinates")
    return profile


def crop(im, box):
    return im.crop(tuple(round(coord * size) for coord, size in zip(box, im.size * 2)))


def text_row(region, threshold=170, height=48):
    gray = ImageOps.grayscale(region)
    if min(gray.size) < 2:
        return Image.new("L", (1, 1), 255)
    scale = min(height / gray.height, (ROW_WIDTH - 28) / gray.width)
    gray = gray.resize(tuple(max(1, round(n * scale)) for n in gray.size), Image.Resampling.BICUBIC)
    # HUD glyphs are light. Keep the light strokes and suppress background art.
    return gray.point(lambda shade: 0 if shade >= threshold else 255)


def recognize(sheet, rows, language, tesseract, single_line=False, digits=False):
    encoded = BytesIO()
    multiple = isinstance(sheet, list)
    if multiple:
        # One single-line OCR pass per TIFF page, with one Tesseract process.
        sheet[0].save(encoded, format="TIFF", save_all=True, append_images=sheet[1:])
    else:
        sheet.save(encoded, format="PNG")
    command = [tesseract, "stdin", "stdout", "--psm", "7" if single_line else "6", "-l", language]
    if digits:
        command += ["-c", "tessedit_char_whitelist=0123456789"]
    result = subprocess.run(
        [*command, "tsv"],
        input=encoded.getvalue(), capture_output=True, timeout=5, check=True,
        env={"OMP_THREAD_LIMIT": "1", **os.environ},
    )
    lines = [[] for _ in range(rows)]
    for word in csv.DictReader(StringIO(result.stdout.decode()), delimiter="\t", quoting=csv.QUOTE_NONE):
        confidence = float(word["conf"])
        if confidence < 0 or not word["text"].strip():
            continue
        center = int(word["top"]) + int(word["height"]) // 2
        index = int(word["page_num"]) - 1 if multiple else 0 if single_line else center // ROW_HEIGHT
        if 0 <= index < len(lines):
            lines[index].append((int(word["left"]), word["text"].strip(), confidence))
    return [(" ".join(t for _, t, _ in sorted(row)), min((c for _, _, c in row), default=0))
            for row in lines]


def combine_rows(regions):
    sheet = Image.new("L", (ROW_WIDTH, ROW_HEIGHT * len(regions)), 255)
    for i, row in enumerate(regions):
        sheet.paste(row, (14, i * ROW_HEIGHT + (ROW_HEIGHT - row.height) // 2))
    return sheet


def price_tiles(region):
    if min(region.size) < 2:
        return [], False
    # Prices sit to the right of a coin that can turn pale during animation.
    # A leading digit should light up nearly as many rows as the last digit.
    region = region.convert("RGB")
    split = round(region.width * 11 / 21)
    neutral = Image.new("L", region.size)
    pixels = (region.getpixel((x, y)) for y in range(region.height) for x in range(region.width))
    neutral.putdata([min(p) if max(p) - min(p) <= 55 else 0 for p in pixels])
    leading_rows = sum(neutral.crop((0, y, split, y + 1)).getextrema()[1] >= 170
                       for y in range(region.height))
    trailing_rows = sum(neutral.crop((split, y, region.width, y + 1)).getextrema()[1] >= 170
                        for y in range(region.height))
    wide = leading_rows >= max(math.ceil(region.height * .3), math.ceil(trailing_rows * .75))
    if wide:
        tiles = [text_row(neutral, threshold=threshold, height=height)
                 for threshold, height in ((175, 46), (130, 32))]
        cropped = []
        for tile in tiles:
            bounds = ImageOps.invert(tile).getbbox()
            if bounds:
                cropped.append(tile.crop(bounds))
        return cropped, True
    right = region.crop((split, 0, region.width, region.height))
    tiles = [text_row(right, threshold=threshold, height=46) for threshold in (175, 185, 205)]
    return [tile for tile in tiles if tile.getextrema()[0] == 0], False


class HudReader:
    def __init__(self, profile=None, language="eng", tesseract="tesseract", min_confidence=60):
        self.profile = load_profile(profile)
        self.language = language
        self.tesseract = tesseract
        self.min_confidence = min_confidence
        self.retries = ThreadPoolExecutor(max_workers=2)
        self.price_cache = OrderedDict()
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.roster = {normalize(c["name"]): {"id": c["id"], "cost": c["cost"]}
                       for c in data["champions"]}
        for alias, name in self.profile.get("aliases", {}).items():
            canonical = normalize(name)
            key = normalize(alias)
            if canonical not in self.roster or (key in self.roster and self.roster[key] != self.roster[canonical]):
                raise ValueError(f"unknown or ambiguous champion alias: {alias}")
            self.roster[key] = self.roster[canonical]
        self.level_labels = {normalize(label) for label in self.profile["level_labels"]}

    def read(self, im):
        viewport = crop(im, self.profile["viewport"])
        gold_crop = crop(viewport, self.profile["gold"])
        level_crop = crop(viewport, self.profile["level"])
        shop_crops = [crop(viewport, box) for box in self.profile["shop"]]
        price_job = None
        if self.profile["shop_price"] is not None:
            price_crops = [crop(viewport, box) for box in self.profile["shop_price"]]
            price_job = self.retries.submit(self.read_prices, price_crops)
        regions = [text_row(gold_crop, threshold=190), text_row(level_crop)]
        regions.extend(text_row(slot) for slot in shop_crops)
        regions.append(text_row(level_crop, threshold=140, height=38))
        rows = recognize(combine_rows(regions), len(regions), self.language, self.tesseract)
        gold, level, slots = self.fields(rows)
        price_error = None
        try:
            prices = price_job.result() if price_job else [None] * 5
        except (OSError, subprocess.SubprocessError) as error:
            prices = [None] * 5
            price_error = str(error)
        if gold is None and level is None and not any(slots):
            return self.result(rows, gold, level, slots)

        gold_retry = text_retry = None
        if gold is None and min(gold_crop.size) >= 2:
            gray = ImageOps.grayscale(gold_crop)
            width = max(1, round(gray.width * 48 / gray.height))
            gray = gray.resize((width, 48), Image.Resampling.BICUBIC)
            gold_retry = self.retries.submit(self.read_line, ImageOps.invert(gray), True)
        needs_level = level is None and any(self.level_number(row[0]) is not None for row in (rows[1], rows[7]))
        tiles = [text_row(level_crop, threshold=177, height=40), text_row(level_crop)] if needs_level else []
        shop_indexes = []
        for i, (slot, region) in enumerate(zip(slots, shop_crops)):
            if slot is not None or min(region.size) < 2:
                continue
            brightest = ImageOps.grayscale(region).getextrema()[1]
            if brightest >= 180:
                shop_indexes.append((i, 1))
                tiles.append(text_row(region, threshold=145, height=55))
            elif brightest >= 120 and gold is not None and level is not None:
                # A shop transition can dim the label considerably. Try the
                # full line and its left portion, where short names align.
                dim = text_row(region, threshold=max(55, round(brightest * .48)))
                shop_indexes.append((i, 2))
                tiles.extend((dim, dim.crop((0, 0, round(dim.width * .56), dim.height))))
        if tiles:
            pages = [ImageOps.expand(tile, border=16, fill=255) for tile in tiles]
            text_retry = self.retries.submit(recognize, pages, len(pages), self.language,
                                            self.tesseract, single_line=True)

        if gold_retry:
            gold = self.read_gold(gold_retry.result(), max(self.min_confidence, 82))
        if text_retry:
            alternatives = text_retry.result()
            if needs_level:
                level = self.recover_level([rows[1], rows[7]], alternatives[:2])
                alternatives = alternatives[2:]
            start = 0
            for i, count in shop_indexes:
                names = {name for row in alternatives[start:start + count]
                         if (name := normalize(self.reliable_text(row))) in self.roster}
                primary_name = normalize(rows[i + 2][0])
                conflict = rows[i + 2][1] >= 25 and primary_name in self.roster and primary_name not in names
                if len(names) == 1 and not conflict:
                    slots[i] = self.roster[names.pop()]
                start += count
        slots = [dict(unit, price=price) if unit is not None else None for unit, price in zip(slots, prices)]
        result = self.result(rows, gold, level, slots)
        if price_error:
            result["priceOcrError"] = price_error
        return result

    def read_prices(self, regions):
        keys, pending = [], {}
        for region in regions:
            tiles, wide = price_tiles(region)
            key = (wide, tuple((tile.size, tile.tobytes()) for tile in tiles)) if tiles else None
            keys.append(key)
            if key is not None and key not in self.price_cache:
                pending[key] = tiles

        if pending:
            pages = [ImageOps.expand(tile, border=16, fill=255) for tiles in pending.values() for tile in tiles]
            found = iter(recognize(pages, len(pages), self.language, self.tesseract,
                                   single_line=True, digits=True))
            threshold = max(self.min_confidence, PRICE_CONFIDENCE)
            for key, tiles in pending.items():
                self.price_cache[key] = self.accept_price([next(found) for _ in tiles], key[0], threshold)

        prices = []
        for key in keys:
            prices.append(self.price_cache.get(key))
            if key is not None:
                self.price_cache.move_to_end(key)
        while len(self.price_cache) > 256:
            self.price_cache.popitem(last=False)
        return prices

    def accept_price(self, rows, wide, threshold):
        values = Counter()
        for row in rows:
            value = self.read_gold(row, threshold)
            if value is not None and (value >= 10) == wide and row[0] == str(value):
                values[value] += 1
        if not values:
            return None
        value, votes = values.most_common(1)[0]
        return value if len(values) == 1 or votes > sum(values.values()) / 2 else None

    def parse(self, rows):
        return self.result(rows, *self.fields(rows))

    def fields(self, rows):
        gold = self.read_gold(rows[0], self.min_confidence)
        level = self.read_level([rows[1], *rows[7:]])
        slots = [self.roster.get(normalize(self.reliable_text(row))) for row in rows[2:7]]
        return gold, level, slots

    def result(self, rows, gold, level, slots):
        shop_evidence = sum(slot is not None for slot in slots) >= 2
        # Two independent areas must confirm the HUD. Do not discard a good
        # field just because another area is obscured.
        detected = sum((gold is not None, level is not None, shop_evidence)) >= 2
        return {
            "hudDetected": detected,
            "gold": gold if detected else None,
            "level": level if detected else None,
            "shop": slots if detected and all(slots) else None,
            "shopSlots": slots if detected else [None] * 5,
            "ocr": [{"text": text, "confidence": round(confidence, 1)} for text, confidence in rows[:7]],
            "levelRetry": {"text": rows[7][0], "confidence": round(rows[7][1], 1)} if len(rows) > 7 else None,
        }

    def read_line(self, tile, digits=False):
        return recognize(ImageOps.expand(tile, border=16, fill=255), 1, self.language,
                         self.tesseract, single_line=True, digits=digits)[0]

    @staticmethod
    def read_gold(row, threshold):
        text, confidence = row
        text = text.strip()
        return int(text) if confidence >= threshold and re.fullmatch(r"[0-9]{1,3}", text) else None

    def reliable_text(self, row):
        text, confidence = row
        return text.strip() if confidence >= self.min_confidence else ""

    def read_level(self, rows):
        candidates = []
        for text, confidence in rows:
            level = self.level_number(text)
            if level is not None and confidence >= LEVEL_AGREEMENT_CONFIDENCE:
                candidates.append((level, confidence))
        if len({level for level, _ in candidates}) != 1:
            return None
        if len(candidates) >= 2 or candidates[0][1] >= self.min_confidence:
            return candidates[0][0]
        return None

    def recover_level(self, primary, alternatives):
        values = {n for row in primary + alternatives if (n := self.level_number(row[0])) is not None}
        if len(values) != 1:
            return None
        confirmed = self.read_level(primary + alternatives)
        if confirmed is not None:
            return confirmed
        for text, confidence in alternatives:
            level = self.level_number(text)
            if level is not None and confidence >= LEVEL_AGREEMENT_CONFIDENCE:
                return level
        return None

    def level_number(self, text):
        match = re.fullmatch(r"([^0-9]+)([0-9]{1,2})", text.strip())
        if match and normalize(match[1]) in self.level_labels:
            level = int(match[2])
            if 1 <= level <= 12:
                return level
        return None
