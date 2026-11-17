"""Terminal interface: colors, banner, boxes, prompts, meters."""

from __future__ import annotations

import os
import platform as _platform
import shutil
import sys

from . import __version__

__all__ = [
    "C", "init", "set_ascii", "paint", "cprint", "clear", "term_width",
    "rule", "header", "footer", "banner", "item", "kv", "ok", "warn",
    "err", "info", "pause", "ask", "ask_int", "ask_yes", "read_secret", "bar",
]


class C:
    """ANSI palette (256-color, degrades gracefully)."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[38;5;196m"
    BLOOD = "\033[38;5;160m"
    DARK = "\033[38;5;88m"
    ASH = "\033[38;5;245m"
    WHITE = "\033[38;5;255m"
    GREEN = "\033[38;5;46m"
    YELLOW = "\033[38;5;220m"
    CYAN = "\033[38;5;51m"
    ON_RED = "\033[48;5;160m\033[38;5;231m"


_COLOR = True
_ASCII = False

_ART_BLOCK = (
    " ██╗   ██╗███████╗██████╗ ",
    " ██║   ██║██╔════╝██╔══██╗",
    " ██║   ██║███████╗██████╔╝",
    " ██║   ██║╚════██║██╔══██╗",
    " ╚██████╔╝███████║██████╔╝",
    "  ╚═════╝ ╚══════╝╚═════╝ ",
)

_ART_ASCII = (
    " _   _ ____  ____  ",
    "| | | / ___|| __ ) ",
    "| | | \\___ \\|  _ \\ ",
    "| |_| |___) | |_) |",
    " \\___/|____/|____/ ",
)


def init(force=None):
    """Decide whether ANSI colors are used. force=True/False overrides."""
    global _COLOR
    if force is not None:
        _COLOR = bool(force)
    else:
        if os.environ.get("NO_COLOR"):
            _COLOR = False
        elif os.environ.get("TERM", "").lower() == "dumb":
            _COLOR = False
        else:
            _COLOR = True
    if os.name == "nt":
        try:  # enable VT sequences on legacy Windows consoles
            import ctypes

            handle = ctypes.windll.kernel32.GetStdHandle(-11)
            ctypes.windll.kernel32.SetConsoleMode(handle, 7)
        except Exception:
            pass
    return _COLOR


def set_ascii(flag):
    global _ASCII
    _ASCII = bool(flag)


def paint(text, *styles):
    if not _COLOR or not styles:
        return str(text)
    return "".join(styles) + str(text) + C.RESET


def cprint(text="", *styles, end="\n"):
    print(paint(text, *styles), end=end)


def clear():
    if sys.stdout.isatty():
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()


def term_width(default=66):
    try:
        width = shutil.get_terminal_size((default, 24)).columns
    except Exception:
        width = default
    return max(40, min(width, 120))


def rule(char="─", style=None):
    cprint(char * (term_width() - 2), style or C.DARK)


def header(title):
    line = "┌─[ " + str(title).upper() + " ]"
    pad = max(0, term_width() - len(line) - 1)
    print()
    cprint(line + "─" * pad, C.DARK, C.BOLD)


def footer():
    cprint("└" + "─" * (term_width() - 3), C.DARK)


def _box_line(text, inner, body=None):
    pad = " " * max(0, inner - len(text))
    print("  " + paint("║", C.DARK) + paint(text + pad, body or C.WHITE) + paint("║", C.DARK))


def banner():
    art = _ART_ASCII if (_ASCII or term_width() < 46) else _ART_BLOCK
    print()
    for line in art:
        cprint("   " + line, C.BLOOD, C.BOLD)
    print()
    inner = 49
    cprint("  ╔" + "═" * inner + "╗", C.DARK, C.BOLD)
    _box_line("   BRUTEFORCE LAB  X   ·   ULTIMATE", inner)
    _box_line("   USB PASSWORD SECURITY AUDITOR  v" + __version__, inner)
    cprint("  ╚" + "═" * inner + "╝", C.DARK, C.BOLD)
    cprint(
        "   {}  ·  python {}  ·  {}".format(
            _platform.system() or "unknown",
            _platform.python_version(),
            _platform.node() or "device",
        ),
        C.ASH,
    )
    cprint("   offline lab - no device is ever sent passwords", C.DARK)
    print()


def item(key, label, hint=""):
    line = "  {} {}".format(
        paint("[" + str(key) + "]", C.BLOOD, C.BOLD), paint(label, C.WHITE)
    )
    if hint:
        line += " " + paint("· " + hint, C.ASH)
    print(line)


def kv(key, value, width=16):
    print("  " + paint(str(key).ljust(width), C.ASH) + " " + paint(value, C.WHITE))


def ok(message):
    print("  " + paint("[+]", C.GREEN, C.BOLD) + " " + paint(message, C.WHITE))


def warn(message):
    print("  " + paint("[!]", C.YELLOW, C.BOLD) + " " + paint(message, C.YELLOW))


def err(message):
    print("  " + paint("[-]", C.RED, C.BOLD) + " " + paint(message, C.RED))


def info(message):
    print("  " + paint("[i]", C.ASH) + " " + paint(message, C.ASH))


def pause(text="press ENTER to continue"):
    try:
        input("  " + paint("↵ " + text, C.DARK) + " ")
    except (EOFError, KeyboardInterrupt):
        print()


def ask(prompt, default=""):
    suffix = " [{}]".format(default) if default not in ("", None) else ""
    try:
        raw = input("  {} {}{}: ".format(paint(">", C.RED, C.BOLD), prompt, suffix))
    except EOFError:
        return default
    raw = raw.strip()
    return raw if raw else default


def ask_int(prompt, default, lo=None, hi=None):
    while True:
        raw = ask(prompt, str(default))
        try:
            value = int(raw)
        except (TypeError, ValueError):
            warn("enter a whole number")
            continue
        if lo is not None and value < lo:
            warn("minimum is {}".format(lo))
            continue
        if hi is not None and value > hi:
            warn("maximum is {}".format(hi))
            continue
        return value


def ask_yes(prompt, default=False):
    raw = ask(prompt + (" [Y/n]" if default else " [y/N]"), "")
    if not raw:
        return default
    return raw.lower().startswith("y")


def read_secret(prompt="password"):
    try:
        import getpass

        value = getpass.getpass("  {} {} (hidden): ".format(paint(">", C.RED, C.BOLD), prompt))
        if value:
            return value
    except Exception:
        pass
    return ask(prompt)


def bar(fraction, width=20, color=None):
    try:
        fraction = float(fraction)
    except (TypeError, ValueError):
        fraction = 0.0
    fraction = max(0.0, min(1.0, fraction))
    filled = int(round(fraction * width))
    return paint("█" * filled, color or C.RED) + paint("░" * (width - filled), C.DARK)
