#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只抓 Strata 視窗內容（PrintWindow，不怕被遮住）
用法：python shot.py <輸出名稱>
"""
import sys
import ctypes
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

from PIL import Image

try:
    import pygetwindow as gw
except ImportError:
    gw = None

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]


def find_hwnd() -> int:
    if not gw:
        return 0
    for w in gw.getAllWindows():
        if w.title and "strata" in w.title.lower() and w.width > 300:
            return w._hWnd
    return 0


def capture(hwnd: int) -> Image.Image:
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    width, height = rect.right - rect.left, rect.bottom - rect.top
    if width <= 0 or height <= 0:
        raise RuntimeError("視窗尺寸為 0，可能已最小化")

    hdc = user32.GetWindowDC(hwnd)
    memdc = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, width, height)
    gdi32.SelectObject(memdc, bmp)
    # PW_RENDERFULLCONTENT = 2，可抓到 GPU 渲染的內容
    if not user32.PrintWindow(hwnd, memdc, 2):
        user32.PrintWindow(hwnd, memdc, 0)

    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = -height  # top-down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = 0  # BI_RGB

    buf = ctypes.create_string_buffer(width * height * 4)
    gdi32.GetDIBits(memdc, bmp, 0, height, buf, ctypes.byref(bmi), 0)

    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1).convert("RGB")

    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(memdc)
    user32.ReleaseDC(hwnd, hdc)
    return img


def main() -> None:
    out = Path(__file__).resolve().parent / "out" / "shots"
    out.mkdir(parents=True, exist_ok=True)
    name = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%H%M%S")
    path = out / f"{name}.png"

    hwnd = find_hwnd()
    if not hwnd:
        print("找不到 Strata 視窗，請確認 App 已開啟", file=sys.stderr)
        sys.exit(1)

    img = capture(hwnd)
    img.save(path)
    print(path)
    print(f"{img.width}x{img.height}")


if __name__ == "__main__":
    main()
