"""OCR regression tests. Set TFT_SET18_ART_ZIP to the asset archive in docs/hud-reader.md."""

from io import BytesIO
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image, ImageDraw, ImageFont, ImageOps

from hud_ocr import DESKTOP_PROFILE, HudReader, price_tiles


class HudParsingTests(unittest.TestCase):
    def test_does_not_invent_data_for_missing_or_uncertain_fields(self):
        reader = HudReader()
        rows = [("0", 95), ("Lvl. 10", 96), ("Ornn", 99), ("Karma", 15),
                ("Other season", 99), ("", 0), ("Varus", 90)]
        result = reader.parse(rows)
        self.assertTrue(result["hudDetected"])
        self.assertEqual((result["gold"], result["level"]), (0, 10))
        self.assertIsNone(result["shop"])
        self.assertEqual([s["id"] if s else None for s in result["shopSlots"]],
                         ["DA_18_Ornn", None, None, None, "DA_18_Varus"])
        rows[1] = ("Buy XP 4", 99)
        partial = reader.parse(rows)
        self.assertTrue(partial["hudDetected"])
        self.assertEqual(partial["gold"], 0)
        self.assertIsNone(partial["level"])
        self.assertEqual(partial["shopSlots"], result["shopSlots"])
        rows[-1] = ("", 0)
        result = reader.parse(rows)
        self.assertFalse(result["hudDetected"])
        self.assertIsNone(result["gold"])
        self.assertEqual(result["shopSlots"], [None] * 5)

    def test_agreement_recovers_level_and_conflicting_digits_stay_unknown(self):
        reader = HudReader()
        rows = [("4", 90), ("Lvl. 7", 34), ("Karma", 80), ("Varus", 85),
                ("Revenge", 96), ("", 0), ("", 0), ("Lvl.7", 31)]
        result = reader.parse(rows)
        self.assertEqual(result["level"], 7)
        self.assertEqual(result["gold"], 4)
        self.assertIsNone(result["shopSlots"][2])
        rows[-1] = ("Lvl. 1", 88)
        result = reader.parse(rows)
        self.assertIsNone(result["level"])
        self.assertEqual(result["gold"], 4)
        rows[0] = ("", 0)
        rows[-1] = ("Lvl.7", 85)
        result = reader.parse(rows)
        self.assertTrue(result["hudDetected"])
        self.assertEqual(result["level"], 7)
        self.assertIsNone(result["gold"])

    def test_retry_requires_consistent_level_evidence(self):
        reader = HudReader()
        primary = [("Lvl. 5", 1), ("Lvi. 5", 48)]
        self.assertEqual(reader.recover_level(primary, [("Lvl. 5", 31)]), 5)
        self.assertIsNone(reader.recover_level(primary, [("Lvl. 6", 91)]))
        self.assertIsNone(reader.read_gold(("S2", 98), 60))
        self.assertEqual(reader.read_gold(("0", 93), 82), 0)

    def test_gold_retry_confirms_a_low_confidence_number(self):
        reader = HudReader()
        self.addCleanup(reader.close)
        region = Image.new("L", (23, 24))
        weak = ("17", 57)
        with patch.object(reader, "recognize", return_value=[("17", 40), ("17", 96), ("17", 94)]):
            self.assertEqual(reader.retry_gold(region, weak), 17)
        with patch.object(reader, "recognize", return_value=[("17", 40), ("17", 96), ("7", 96)]):
            self.assertIsNone(reader.retry_gold(region, weak))
        with patch.object(reader, "recognize", return_value=[("17", 95), ("7", 90), ("7", 90)]):
            self.assertEqual(reader.retry_gold(region, weak), 17)
        with patch.object(reader, "read_line", return_value=("", 0)), patch.object(
                reader, "recognize", return_value=[("", 0), ("1", 96), ("1", 94)]):
            self.assertIsNone(reader.retry_gold(region, ("J", 44)))
            self.assertEqual(reader.retry_gold(region, ("J", 44), corroborated=True), 1)

    def test_price_uses_digit_width_and_resolves_conflicting_masks(self):
        reader = HudReader()
        self.assertEqual(reader.accept_price([("3", 96), ("3", 95), ("4", 83)], False, 75), 3)
        self.assertIsNone(reader.accept_price([("3", 96), ("4", 83)], False, 75))
        self.assertIsNone(reader.accept_price([("5", 97)], True, 75))
        self.assertEqual(reader.accept_price([("15", 95)], True, 75), 15)
        self.assertEqual(reader.accept_price([("0", 95)], False, 75), 0)

    def test_cropped_gold_retry_needs_hud_and_agreeing_digits(self):
        reader = HudReader()
        self.addCleanup(reader.close)
        region = Image.new("RGB", (23, 24))
        ImageDraw.Draw(region).rectangle((9, 3, 14, 16), fill="white")
        primary = ("$1", 68)
        failed_full_crop = [("", 0), ("51", 41), ("1", 45)]
        with patch.object(reader, "recognize", side_effect=[failed_full_crop, [("51", 94), ("51", 93)]]):
            self.assertEqual(reader.retry_gold(region, primary, corroborated=True), 51)
        with patch.object(reader, "recognize", side_effect=[failed_full_crop, [("51", 94), ("31", 93)]]):
            self.assertIsNone(reader.retry_gold(region, primary, corroborated=True))
        with patch.object(reader, "recognize", return_value=[("", 0)]) as recognize:
            self.assertIsNone(reader.retry_gold(region, primary))
            self.assertEqual(recognize.call_count, 1)

    def test_price_retry_requires_two_confident_votes(self):
        reader = HudReader()
        self.addCleanup(reader.close)
        self.assertIsNone(reader.accept_price([("3", 97), ("3", 75)], False, 85, minimum_votes=2))
        self.assertIsNone(reader.accept_price([("3", 97), ("4", 95)], False, 85, minimum_votes=2))
        self.assertEqual(reader.accept_price([("3", 97), ("3", 95)], False, 85, minimum_votes=2), 3)

    def test_native_price_reads_only_unresolved_masks_after_the_first_batch(self):
        reader = HudReader()
        self.addCleanup(reader.close)
        masks = [Image.new("L", (10, 10), color) for color in range(6)]
        groups = [(masks[:3], False), (masks[3:], False)]
        first_batch = [("3", 95), ("3", 95), ("4", 95), ("5", 95)]
        with patch.object(reader, "native", object()), patch.object(
                reader, "recognize", side_effect=[first_batch, [("5", 95)]]) as recognize:
            self.assertEqual(reader.cached_prices(groups), [3, 5])
            self.assertEqual(reader.cached_prices(groups), [3, 5])
        self.assertEqual([call.args[1] for call in recognize.call_args_list], [4, 1])

    def test_highlighted_title_retry_confirms_the_original_name(self):
        reader = HudReader()
        self.addCleanup(reader.close)
        tile = Image.new("RGB", (152, 30), "#202b32")
        draw = ImageDraw.Draw(tile)
        draw.rectangle((15, 5, 25, 21), fill="white")
        draw.rectangle((145, 28, 151, 29), fill="white")
        slots = [None] * 5
        rows = [("6", 97), ("Lvl. 5", 95), ("Xayah _", 0)]
        boxes = [None, None, (0, 0, *tile.size)]
        prices = [1, None, None, None, None]
        with patch.object(reader, "recognize", return_value=[("Yorick", 97), ("Yorick", 95)]):
            reader.retry_visible_shop(tile, boxes, rows, slots, prices)
        self.assertIsNone(slots[0])
        with patch.object(reader, "recognize", return_value=[("Xayah", 97), ("Xayah", 95)]):
            reader.retry_visible_shop(tile, boxes, rows, slots, prices)
        self.assertEqual(slots[0], reader.roster["xayah"])

    def test_pale_coin_is_shorter_than_a_leading_price_digit(self):
        price = Image.new("RGB", (21, 10), "#14212b")
        draw = ImageDraw.Draw(price)
        draw.rectangle((15, 1, 17, 8), fill="white")
        draw.ellipse((3, 3, 8, 5), fill="#bcb8ae")
        tiles, wide = price_tiles(price)
        self.assertTrue(tiles)
        self.assertFalse(wide)

        draw.rectangle((8, 1, 9, 8), fill="white")
        tiles, wide = price_tiles(price)
        self.assertTrue(tiles)
        self.assertTrue(wide)


ART = os.environ.get("TFT_SET18_ART_ZIP")
SHOP_A = ["Ornn", "Karma", "Varus", "Yunara", "Warwick"]
SHOP_B = ["Akali", "Camille", "Leona", "Teemo", "Ashe"]
ROOT = Path(__file__).resolve().parent


@unittest.skipUnless(ART and shutil.which("tesseract"), "requires Tesseract and TFT_SET18_ART_ZIP")
class HudImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader = HudReader()
        cls.addClassCleanup(cls.reader.close)
        with zipfile.ZipFile(ART) as archive:
            cls.art = {}
            for name in SHOP_A + SHOP_B:
                member = next(p for p in archive.namelist() if p.endswith(f"/Champions/{name}/{name}_tileIcon.png"))
                cls.art[name] = Image.open(BytesIO(archive.read(member))).convert("RGB")

    def render(self, gold, level, names, tint, mascot_x, variant=0):
        # The board, mascot, and UI geometry are synthetic. Shop portraits
        # come from the pinned Set 18 archive.
        width, height = 1920, 1080
        image = Image.new("RGB", (width, height), tint)
        draw = ImageDraw.Draw(image)
        for row in range(6):
            for col in range(7):
                x, y = 300 + col * 181, 150 + row * 103
                draw.rounded_rectangle((x, y, x + 160, y + 87), radius=variant * 12,
                                       outline=["lightgray", "tan", "darkcyan"][variant], width=3)
        if variant == 1:
            draw.polygon([(mascot_x, 680), (mascot_x + 60, 594), (mascot_x + 120, 680)], fill="aqua")
        elif variant == 2:
            draw.rounded_rectangle((mascot_x, 653, mascot_x + 120, 748), radius=25, fill="magenta")
        else:
            draw.ellipse((mascot_x, 592, mascot_x + 72, 690), fill="gold", outline="white", width=6)
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 19)
        draw.rectangle((220, 872, 1510, 1079), fill="#101c2b")
        for index, name in enumerate(names):
            if name is None:
                continue
            x1, y1, x2, y2 = DESKTOP_PROFILE["shop"][index]
            x = round(x1 * width)
            image.paste(ImageOps.fit(self.art[name], (round((x2 - x1) * width), 104)), (x, 929))
            draw.text((x + 5, round((y1 + y2) * height / 2)), name, font=font, fill="white", anchor="lm")
        for field, label in (("gold", str(gold)), ("level", f"Lvl. {level}")):
            x1, y1, x2, y2 = DESKTOP_PROFILE[field]
            center = (round((x1 + x2) * width / 2), round((y1 + y2) * height / 2))
            draw.text(center, label, font=font, fill="white", anchor="mm")
        return image

    def check_hud(self, result, gold, level, names):
        self.assertEqual((result["gold"], result["level"]), (gold, level), result["ocr"])
        expected = [self.reader.roster[name.lower()] if name else None for name in names]
        slots = result["shopSlots"]
        self.assertEqual([{"id": slot["id"], "cost": slot["cost"]} if slot else None for slot in slots],
                         expected, result["ocr"])
        self.assertEqual(result["shop"], slots if all(expected) else None)

    def test_resolution_board_mascot_and_letterbox(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.json"
            profile.write_text(json.dumps({"viewport": [.125, 0, .875, 1]}))
            wide_reader = HudReader(profile)
            self.addCleanup(wide_reader.close)
            image = self.render(7, 3, SHOP_A, "#456242", 440)
            self.check_hud(self.reader.read(image), 7, 3, SHOP_A)
            image = self.render(24, 6, SHOP_B, "#4c385f", 755, variant=1)
            image = image.resize((1280, 720), Image.Resampling.LANCZOS)
            self.check_hud(self.reader.read(image), 24, 6, SHOP_B)
            wide = Image.new("RGB", (2560, 1080))
            wide.paste(self.render(50, 8, SHOP_A, "#8f734f", 1210, variant=2), (320, 0))
            self.check_hud(wide_reader.read(wide), 50, 8, SHOP_A)
            bounds, boxes = wide_reader.video_crops(wide.size)
            self.assertEqual(wide_reader.read_crops(wide.crop(bounds), boxes), wide_reader.read(wide))

    def test_native_session_keeps_text_and_digits_separate(self):
        if self.reader.native is None:
            self.skipTest("requires the Linux system Tesseract library")
        cli = HudReader(tesseract=shutil.which("tesseract"))
        self.addCleanup(cli.close)
        image = self.render(50, 8, SHOP_A, "#456242", 440)
        expected = cli.read(image)
        digits = Image.new("L", (150, 55), 255)
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)
        ImageDraw.Draw(digits).text((15, 1), "23", fill=0, font=font)
        for _ in range(2):
            self.assertEqual(self.reader.read_line(digits, digits=True)[0], "23")
            self.assertEqual(self.reader.read(image), expected)

    def test_occlusion_and_empty_slot(self):
        names = ["Ornn", None, "Varus", "Yunara", "Warwick"]
        image = self.render(0, 4, names, "#448591", 1470)
        with patch.object(self.reader, "read_prices", return_value=[1, 1, 2, 2]) as prices:
            result = self.reader.read(image)
        self.check_hud(result, 0, 4, names)
        self.assertEqual(len(prices.call_args.args[0]), 4)
        self.assertEqual([slot["price"] if slot else None for slot in result["shopSlots"]], [1, None, 1, 2, 2])
        ImageDraw.Draw(image).rectangle((225, 875, 326, 929), fill="black")
        self.check_hud(self.reader.read(image), 0, None, names)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires ffmpeg")
    def test_paced_video_measures_latency_and_reads_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            for i in range(16):
                gold, level, names = (7, 3, SHOP_A) if i < 8 else (24, 6, SHOP_B)
                image = self.render(gold, level, names, "#456242" if i < 8 else "#4c385f",
                                    440 + i * 30, variant=int(i >= 8))
                image.resize((1280, 720), Image.Resampling.LANCZOS).save(path / f"{i:02d}.png")
            video = path / "match.mp4"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-framerate", "4", "-i", str(path / "%02d.png"),
                            "-threads", "2", "-pix_fmt", "yuv420p", str(video)], check=True)
            output = path / "hud.json"
            result = subprocess.run([sys.executable, str(ROOT / "hud-reader.py"), "--video", str(video),
                                     "--output", str(output)],
                                    capture_output=True, text=True, check=True, timeout=20)
            records = [json.loads(line) for line in result.stdout.splitlines()]
            self.assertGreaterEqual(len(records), 2)
            self.assertEqual({record["gold"] for record in records}, {7, 24})
            for record in records:
                expected = (7, 3, SHOP_A) if record["mediaTimeMs"] < 2000 else (24, 6, SHOP_B)
                self.check_hud(record, *expected)
                self.assertGreater(record["recognitionLatencyMs"], 0)
                self.assertGreaterEqual(record["endToEndLatencyMs"], record["processingLatencyMs"])
            self.assertEqual(json.loads(output.read_text())["frame"], records[-1]["frame"])
            first = subprocess.run([sys.executable, str(ROOT / "hud-reader.py"), "--video", str(video), "--once"],
                                   capture_output=True, text=True, check=True, timeout=20)
            first_record = json.loads(first.stdout)
            self.assertEqual(first_record["frame"], 0)
            self.assertEqual(first_record["resolution"], [1280, 720])
            self.check_hud(first_record, 7, 3, SHOP_A)
            latencies = sorted(record["endToEndLatencyMs"] for record in records)
            print(f"4 Hz replay: {len(records)}/16 samples, p50={latencies[len(latencies)//2]} ms, "
                  f"p95={latencies[(95 * len(latencies) - 1) // 100]} ms, "
                  f"deadline misses={sum(r['deadlineMissed'] for r in records)}, "
                  f"skipped between samples={records[-1]['droppedFrames']}")


if __name__ == "__main__":
    unittest.main()
