"""HUD reader v1 for TFT 1280x720 frames. Abstains (null) unless two crops agree.

Design: every field is read from two slightly different boxes. A value is
emitted only when both reads give the same valid value. XP is parsed from
digits only and emitted only when exactly one split (x < y, y a known
denominator) is possible. Otherwise null. Never guesses.
"""
import re
import sys
from PIL import Image, ImageOps

sys.path.insert(0, '/home/user/TFT/scripts')
import hud_tesseract as h

_NR = None


def _nr():
    global _NR
    if _NR is None:
        _NR = h.native_reader('eng', 'tesseract')
    return _NR


def _txt(im, box, scale=4, pad=0):
    c = ImageOps.grayscale(im.crop(box))
    if pad:
        c = ImageOps.expand(c, border=pad, fill=0)
    c = c.resize((c.width * scale, c.height * scale))
    c = ImageOps.autocontrast(c)
    return ''.join(w[4] for w in _nr().words(c, True, True))


def _agree(im, boxes, check):
    """Return the value only if every read gives the same valid string.

    Each entry is a box, or (box, scale, pad) for a second read of the same box.
    """
    vals = []
    for entry in boxes:
        if isinstance(entry[0], tuple):
            box, scale, pad = entry
        else:
            box, scale, pad = entry, 4, 0
        vals.append(_txt(im, box, scale=scale, pad=pad))
    if all(v == vals[0] for v in vals) and check(vals[0]):
        return vals[0]
    return None


STAGE_BOXES = [(495, 3, 580, 21), (490, 1, 586, 23)]
TIMER_BOXES = [((756, 3, 780, 21), 4, 0), ((756, 3, 780, 21), 3, 8)]
GOLD_BOXES = [(612, 590, 635, 614), (606, 588, 640, 616)]
LEVEL_BOXES = [(190, 588, 212, 608), (186, 586, 216, 610)]
XP_BOXES = [(240, 588, 290, 608), (234, 586, 296, 610)]
STREAK_BOXES = [(690, 586, 708, 604), (684, 584, 714, 606)]
XP_DENOMS = {2, 6, 10, 20, 34, 36, 54, 56, 66, 68}


def _stage(im):
    s = _agree(im, STAGE_BOXES, lambda v: re.fullmatch(r'[1-7][1-7]', v) is not None)
    return f'{s[0]}-{s[1]}' if s else None


def _timer(im):
    s = _agree(im, TIMER_BOXES, lambda v: re.fullmatch(r'\d{1,2}', v) is not None and 0 <= int(v) <= 60)
    return int(s) if s is not None else None


def _gold(im):
    s = _agree(im, GOLD_BOXES, lambda v: re.fullmatch(r'\d{1,3}', v) is not None)
    return int(s) if s is not None else None


def _level(im):
    s = _agree(im, LEVEL_BOXES, lambda v: re.fullmatch(r'\d{1,2}', v) is not None and 1 <= int(v) <= 10)
    return int(s) if s is not None else None


def _raw_any(im, box, scale, pad):
    """OCR with no character whitelist, so the slash can survive."""
    c = ImageOps.grayscale(im.crop(box))
    if pad:
        c = ImageOps.expand(c, border=pad, fill=0)
    c = ImageOps.autocontrast(c.resize((c.width * scale, c.height * scale)))
    return ''.join(w[4] for w in _nr().words(c, True, False))


def _xp_slash(im):
    """Accept x/yy only when two unrestricted reads give the same text."""
    box = XP_BOXES[0][0] if isinstance(XP_BOXES[0], tuple) and isinstance(XP_BOXES[0][0], tuple) else XP_BOXES[0]
    reads = [_raw_any(im, box, 4, 0), _raw_any(im, box, 3, 8)]
    m = [re.fullmatch(r'(\d{1,2})/(\d{2})', x) for x in reads]
    if not all(m) or reads[0] != reads[1]:
        return None
    x, y = int(m[0].group(1)), int(m[0].group(2))
    return [x, y] if x < y and y in XP_DENOMS else None


def _xp(im):
    slash = _xp_slash(im)
    if slash is not None:
        return slash
    s = _agree(im, XP_BOXES, lambda v: re.fullmatch(r'\d{2,4}', v) is not None)
    if s is None:
        return None
    # OCR drops the slash, so a digit string can split more than one way.
    # Accept only the layout seen in every frame tested: one x digit and a
    # two-digit denominator (e.g. "468" -> 4/68), and only if y is a known
    # denominator. Two-digit x values are abstained, never guessed.
    if len(s) != 3 or s[0] == '0' or s[1] == '0':
        return None
    x, y = int(s[0]), int(s[1:])
    return [x, y] if x < y and y in XP_DENOMS else None


def _streak(im):
    s = _agree(im, STREAK_BOXES, lambda v: re.fullmatch(r'\d', v) is not None)
    return int(s) if s is not None else None


def read(im):
    return {'stage': _stage(im), 'timer': _timer(im), 'gold': _gold(im),
            'level': _level(im), 'xp': _xp(im), 'streak': _streak(im)}


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(p, read(Image.open(p).convert('RGB')))
