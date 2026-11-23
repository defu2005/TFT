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

from PIL import Image, ImageChops, ImageOps

from hud_tesseract import native_reader


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
MIN_SHOP_RETRY_BRIGHTNESS = 120
PRICE_CONFIDENCE = 75
PRICE_RETRY_CONFIDENCE = 85


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


def pixel_box(box, size):
    return tuple(round(coord * dimension) for coord, dimension in zip(box, size * 2))


def crop(im, box):
    return im.crop(pixel_box(box, im.size))


def text_row(region, threshold=170, height=48):
    gray = region if region.mode == "L" else ImageOps.grayscale(region)
    if min(gray.size) < 2:
        return Image.new("L", (1, 1), 255)
    scale = min(height / gray.height, (ROW_WIDTH - 28) / gray.width)
    gray = gray.resize(tuple(max(1, round(n * scale)) for n in gray.size), Image.Resampling.BICUBIC)
    # HUD glyphs are light. Keep the light strokes and suppress background art.
    return gray.point(lambda shade: 0 if shade >= threshold else 255)


def recognize_cli(sheet, language, tesseract, single_line, digits):
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
    for word in csv.DictReader(StringIO(result.stdout.decode()), delimiter="\t", quoting=csv.QUOTE_NONE):
        yield (int(word["page_num"]) - 1, int(word["left"]), int(word["top"]), int(word["height"]),
               word["text"], float(word["conf"]))


def recognize_rows(words, rows, multiple, single_line):
    lines = [[] for _ in range(rows)]
    for page, left, top, height, text, confidence in words:
        text = text.strip()
        if confidence < 0 or not text:
            continue
        center = top + height // 2
        index = page if multiple else 0 if single_line else center // ROW_HEIGHT
        if 0 <= index < len(lines):
            lines[index].append((left, text, confidence))
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


def single_price_retry_tiles(region):
    split = round(region.width * 11 / 21)
    right = region.crop((split, 0, region.width, region.height)).convert("RGB")
    gray = ImageOps.grayscale(right)
    width, height = right.size
    # Some cards have a bright frame at the outer edge. A price glyph has
    # top and bottom padding, whereas that edge spans the entire crop.
    if width > 2 and gray.crop((width - 1, 0, width, height)).getextrema()[0] >= 155:
        right = right.crop((0, 0, width - 1, height))
        gray = gray.crop((0, 0, width - 1, height))
    tiles = [text_row(gray, threshold=threshold, height=scale)
             for threshold, scale in ((145, 46), (155, 32), (170, 32))]
    # The darkest color channel suppresses a saturated card background.
    red, green, blue = right.split()
    neutral = ImageChops.darker(red, ImageChops.darker(green, blue))
    darkest, brightest = neutral.getextrema()
    if brightest - darkest >= 40:
        contrast = ImageOps.autocontrast(neutral)
        tiles.extend(text_row(contrast, threshold=185, height=scale) for scale in (40, 46))
    return list({(tile.size, tile.tobytes()): tile for tile in tiles if tile.getextrema()[0] == 0}.values())


class HudReader:
    def __init__(self, profile=None, language="eng", tesseract="tesseract", min_confidence=60):
        self.profile = load_profile(profile)
        self.language = language
        self.tesseract = tesseract
        self.native = native_reader(language, tesseract)
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

    def close(self):
        self.retries.shutdown()
        if self.native is not None:
            self.native.close()

    def recognize(self, sheet, rows, single_line=False, digits=False):
        multiple = isinstance(sheet, list)
        if self.native is not None:
            try:
                return recognize_rows(self.native.words(sheet, single_line, digits), rows, multiple, single_line)
            except OSError:
                # New installations can have different CLI and library data paths.
                pass
        words = recognize_cli(sheet, self.language, self.tesseract, single_line, digits)
        return recognize_rows(words, rows, multiple, single_line)

    def read(self, im):
        viewport = crop(im, self.profile["viewport"])
        return self.read_crops(viewport, [pixel_box(box, viewport.size) for box in self.hud_boxes()])

    def hud_boxes(self):
        return [self.profile["gold"], self.profile["level"], *self.profile["shop"],
                *(self.profile["shop_price"] or [])]

    def video_crops(self, size):
        left, top, right, bottom = pixel_box(self.profile["viewport"], size)
        viewport_size = right - left, bottom - top
        boxes = [pixel_box(box, viewport_size) for box in self.hud_boxes()]
        x1 = left + min(box[0] for box in boxes)
        y1 = top + min(box[1] for box in boxes)
        x2 = left + max(box[2] for box in boxes)
        y2 = top + max(box[3] for box in boxes)
        if x1 == x2 or y1 == y2:
            x1, y1, x2, y2 = 0, 0, *size
        local = [(left + a - x1, top + b - y1, left + c - x1, top + d - y1) for a, b, c, d in boxes]
        return (x1, y1, x2, y2), local

    def read_crops(self, im, boxes):
        gold_crop, level_crop = (im.crop(box) for box in boxes[:2])
        shop_crops = [ImageOps.grayscale(im.crop(box)) for box in boxes[2:7]]
        shop_tiles = [text_row(region) for region in shop_crops]
        shop_brightness = [region.getextrema()[1] if min(region.size) >= 2 else 0 for region in shop_crops]
        price_job = None
        if len(boxes) > 7:
            # A blank name mask below the retry threshold cannot yield a shop name.
            price_indexes = [i for i, (tile, brightest) in enumerate(zip(shop_tiles, shop_brightness))
                             if brightest >= MIN_SHOP_RETRY_BRIGHTNESS or tile.getextrema()[0] == 0]
            if price_indexes:
                price_crops = [im.crop(boxes[7 + i]) for i in price_indexes]
                price_job = self.retries.submit(self.read_prices, price_crops)
        regions = [text_row(gold_crop, threshold=190), text_row(level_crop)]
        regions.extend(shop_tiles)
        regions.append(text_row(level_crop, threshold=140, height=38))
        rows = self.recognize(combine_rows(regions), len(regions))
        gold, level, slots = self.fields(rows)
        prices = [None] * 5
        price_error = None
        try:
            if price_job:
                for i, value in zip(price_indexes, price_job.result()):
                    prices[i] = value
        except (OSError, subprocess.SubprocessError) as error:
            price_error = str(error)
        if gold is None and level is None and not any(slots):
            return self.result(rows, gold, level, slots)

        gold_retry = text_retry = None
        if gold is None and min(gold_crop.size) >= 2:
            corroborated = level is not None and sum(slot is not None for slot in slots) >= 2
            gold_retry = self.retries.submit(self.retry_gold, gold_crop, rows[0], corroborated)
        needs_level = level is None and any(self.level_number(row[0]) is not None for row in (rows[1], rows[7]))
        tiles = [text_row(level_crop, threshold=threshold, height=height)
                 for threshold, height in ((177, 40), (170, 48), (155, 40))] if needs_level else []
        level_retry_count = len(tiles)
        shop_indexes = []
        for i, (slot, region, brightest) in enumerate(zip(slots, shop_crops, shop_brightness)):
            if slot is not None or min(region.size) < 2:
                continue
            if brightest >= 180:
                shop_indexes.append((i, 1))
                tiles.append(text_row(region, threshold=145, height=55))
            elif brightest >= MIN_SHOP_RETRY_BRIGHTNESS and gold is not None and level is not None:
                # A shop transition can dim the label considerably. Try the
                # full line and its left portion, where short names align.
                dim = text_row(region, threshold=max(55, round(brightest * .48)))
                shop_indexes.append((i, 2))
                tiles.extend((dim, dim.crop((0, 0, round(dim.width * .56), dim.height))))
        if tiles:
            pages = [ImageOps.expand(tile, border=16, fill=255) for tile in tiles]
            text_retry = self.retries.submit(self.recognize, pages, len(pages), single_line=True)

        if gold_retry:
            gold = gold_retry.result()
        if text_retry:
            alternatives = text_retry.result()
            if needs_level:
                level = self.recover_level([rows[1], rows[7]], alternatives[:level_retry_count])
                alternatives = alternatives[level_retry_count:]
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

    def retry_gold(self, region, primary, corroborated=False):
        gray = ImageOps.grayscale(region)
        width = max(1, round(gray.width * 48 / gray.height))
        inverted = ImageOps.invert(gray.resize((width, 48), Image.Resampling.BICUBIC))
        threshold = max(self.min_confidence, 82)
        expected = self.read_gold(primary, max(0, self.min_confidence - 10))
        if expected is None and not corroborated:
            return self.read_gold(self.read_line(inverted, digits=True), threshold)

        tiles = [inverted, text_row(gray, threshold=175, height=40), text_row(gray, threshold=195)]
        pages = [ImageOps.expand(tile, border=16, fill=255) for tile in tiles]
        original, first, second = self.recognize(pages, len(pages), single_line=True, digits=True)
        gold = self.read_gold(original, threshold)
        if gold is not None:
            return gold
        candidate = self.read_gold(first, threshold)
        if candidate is not None and expected in (None, candidate) and candidate == self.read_gold(second, threshold):
            return candidate
        return None

    def read_prices(self, regions):
        groups = [price_tiles(region) for region in regions]
        prices = self.cached_prices(groups)
        uncertain = [i for i, ((tiles, wide), price) in enumerate(zip(groups, prices))
                     if tiles and not wide and price is None]
        retry = [(single_price_retry_tiles(regions[i]), False) for i in uncertain]
        for i, price in zip(uncertain, self.cached_prices(retry, retry=True)):
            prices[i] = price
        return prices

    def cached_prices(self, groups, retry=False):
        keys, pending = [], {}
        for tiles, wide in groups:
            key = (wide, retry, tuple((tile.size, tile.tobytes()) for tile in tiles)) if tiles else None
            keys.append(key)
            if key is not None and key not in self.price_cache:
                pending[key] = tiles

        if pending:
            pages = [ImageOps.expand(tile, border=16, fill=255) for tiles in pending.values() for tile in tiles]
            found = iter(self.recognize(pages, len(pages), single_line=True, digits=True))
            threshold = max(self.min_confidence, PRICE_RETRY_CONFIDENCE if retry else PRICE_CONFIDENCE)
            for key, tiles in pending.items():
                self.price_cache[key] = self.accept_price([next(found) for _ in tiles], key[0], threshold,
                                                          minimum_votes=2 if retry else 1)

        prices = []
        for key in keys:
            prices.append(self.price_cache.get(key))
            if key is not None:
                self.price_cache.move_to_end(key)
        while len(self.price_cache) > 256:
            self.price_cache.popitem(last=False)
        return prices

    def accept_price(self, rows, wide, threshold, minimum_votes=1):
        values = Counter()
        for row in rows:
            value = self.read_gold(row, threshold)
            if value is not None and (value >= 10) == wide and row[0] == str(value):
                values[value] += 1
        if not values:
            return None
        value, votes = values.most_common(1)[0]
        return value if votes >= minimum_votes and votes > sum(values.values()) / 2 else None

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
        return self.recognize(ImageOps.expand(tile, border=16, fill=255), 1, single_line=True, digits=digits)[0]

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
