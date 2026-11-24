"""Reuse the Tesseract C API on Linux, with one session per OCR thread."""

import ctypes
from ctypes.util import find_library
from functools import lru_cache
import os
from pathlib import Path
import shutil
import sys
from threading import local


WORD = 3


@lru_cache(maxsize=1)
def load_api():
    library = find_library("tesseract")
    if library is None:
        return None
    os.environ.setdefault("OMP_THREAD_LIMIT", "1")
    ptr, number, string = ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p
    coordinate = ctypes.POINTER(number)
    try:
        api = ctypes.CDLL(library)
        for name, result, args in (
            ("TessBaseAPICreate", ptr, ()),
            ("TessBaseAPIDelete", None, (ptr,)),
            ("TessBaseAPIInit3", number, (ptr, string, string)),
            ("TessBaseAPISetPageSegMode", None, (ptr, number)),
            ("TessBaseAPISetVariable", number, (ptr, string, string)),
            ("TessBaseAPISetImage", None, (ptr, string, number, number, number, number)),
            ("TessBaseAPIRecognize", number, (ptr, ptr)),
            ("TessBaseAPIClear", None, (ptr,)),
            ("TessBaseAPIClearAdaptiveClassifier", None, (ptr,)),
            ("TessBaseAPIGetIterator", ptr, (ptr,)),
            ("TessResultIteratorGetPageIterator", ptr, (ptr,)),
            ("TessResultIteratorGetUTF8Text", ptr, (ptr, number)),
            ("TessResultIteratorConfidence", ctypes.c_float, (ptr, number)),
            ("TessPageIteratorBoundingBox", number, (ptr, number, coordinate, coordinate, coordinate, coordinate)),
            ("TessResultIteratorNext", number, (ptr, number)),
            ("TessResultIteratorDelete", None, (ptr,)),
            ("TessDeleteText", None, (ptr,)),
        ):
            function = getattr(api, name)
            function.restype = result
            function.argtypes = args
    except (AttributeError, OSError):
        return None
    return api


def native_reader(language, executable):
    if sys.platform != "linux" or executable != "tesseract":
        return None
    binary = shutil.which(executable)
    # Use the system library only with the system executable. An explicit
    # executable or one earlier on PATH retains its own CLI behavior.
    if binary is None or Path(binary).resolve() != Path("/usr/bin/tesseract"):
        return None
    api = load_api()
    return NativeTesseract(api, language) if api is not None else None


class NativeTesseract:
    def __init__(self, api, language):
        self.api = api
        self.language = language
        self.thread = local()

    def get_session(self):
        if not hasattr(self.thread, "session"):
            self.thread.session = Session(self.api, self.language)
        return self.thread.session

    def words(self, sheet, single_line, digits):
        session = self.get_session()
        self.api.TessBaseAPISetPageSegMode(session.handle, 7 if single_line else 6)
        whitelist = b"0123456789" if digits else b""
        if not self.api.TessBaseAPISetVariable(session.handle, b"tessedit_char_whitelist", whitelist):
            raise OSError("Unable to configure the Tesseract character whitelist")
        pages = sheet if isinstance(sheet, list) else [sheet]
        for index, tile in enumerate(pages):
            for left, top, height, text, confidence in session.words(tile):
                yield index, left, top, height, text, confidence

    def close(self):
        if hasattr(self.thread, "session"):
            del self.thread.session


class Session:
    def __init__(self, api, language):
        self.api = api
        self.handle = api.TessBaseAPICreate()
        if not self.handle or api.TessBaseAPIInit3(self.handle, None, language.encode()) != 0:
            raise OSError(f"Unable to load Tesseract language {language}")

    def __del__(self):
        if self.handle:
            self.api.TessBaseAPIDelete(self.handle)

    def words(self, tile):
        api = self.api
        width, height = tile.size
        pixels = tile.tobytes()
        api.TessBaseAPISetImage(self.handle, pixels, width, height, 1, width)
        iterator = None
        try:
            if api.TessBaseAPIRecognize(self.handle, None) != 0:
                raise OSError("Tesseract failed to recognize the page")
            iterator = api.TessBaseAPIGetIterator(self.handle)
            if not iterator:
                return
            page = api.TessResultIteratorGetPageIterator(iterator)
            left, top, right, bottom = (ctypes.c_int() for _ in range(4))
            while True:
                word = api.TessResultIteratorGetUTF8Text(iterator, WORD)
                if word:
                    try:
                        text = ctypes.string_at(word).decode()
                    finally:
                        api.TessDeleteText(word)
                    if api.TessPageIteratorBoundingBox(page, WORD, left, top, right, bottom):
                        confidence = api.TessResultIteratorConfidence(iterator, WORD)
                        yield left.value, top.value, bottom.value - top.value, text, confidence
                if not api.TessResultIteratorNext(iterator, WORD):
                    break
        finally:
            if iterator:
                api.TessResultIteratorDelete(iterator)
            api.TessBaseAPIClear(self.handle)
            # Each page follows the same recognition rules as a fresh CLI call.
            api.TessBaseAPIClearAdaptiveClassifier(self.handle)
