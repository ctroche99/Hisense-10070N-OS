#!/usr/bin/env python3
"""Reversible ADB debloat helper for the Hisense 100U70N (Google TV).

Everything is done with `pm disable-user --user 0`, never uninstall, and every
change is written to logs/changes.jsonl so `restore` can undo exactly what this
tool did. Needs Python 3.8+ and Google's platform-tools (`adb`) on your PATH.

Typical session:
    python3 tvdebloat.py connect 192.168.1.50
    python3 tvdebloat.py info
    python3 tvdebloat.py baseline
    python3 tvdebloat.py check batch1
    python3 tvdebloat.py apply batch1 --reboot
    python3 tvdebloat.py restore --all
"""

import argparse
import datetime
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACKAGES_DIR = ROOT / "packages"
LOG_DIR = ROOT / "logs"
CHANGE_LOG = LOG_DIR / "changes.jsonl"

BATCHES = {
    "batch1": "batch1-hisense.txt",
    "batch2": "batch2-google.txt",
    "batch3": "batch3-optional.txt",
    "batch4": "batch4-launcher.txt",
}
ONE_AT_A_TIME = {"batch3"}
PROJECTIVY = "com.spocky.projengmenu"
LAUNCHER_PAIR = {
    "com.google.android.apps.tv.launcherx",
    "com.google.android.tungsten.setupwraith",
}
ANIMATION_KEYS = (
    "window_animation_scale",
    "transition_animation_scale",
    "animator_duration_scale",
)
REBOOT_DELAY = 15  # an older Hisense lost changes when rebooted straight away

serial = None


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def adb(*args, check=True):
    cmd = ["adb"] + (["-s", serial] if serial else []) + list(args)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if check and proc.returncode != 0:
        die(f"{' '.join(cmd)} failed:\n{proc.stdout}{proc.stderr}")
    return proc.stdout.strip()


def shell(command, check=True):
    return adb("shell", command, check=check)


def device_serial():
    global serial
    if serial:
        return serial
    devices = [
        line.split()[0]
        for line in adb("devices").splitlines()[1:]
        if line.strip().endswith("device")
    ]
    if not devices:
        die("no TV connected. Run: python3 tvdebloat.py connect <TV-IP>")
    if len(devices) > 1:
        die(f"several devices connected ({', '.join(devices)}); pick one with -s")
    serial = devices[0]
    return serial


def package_set(flag=""):
    out = shell(f"pm list packages {flag}".strip())
    return {line[len("package:"):] for line in out.splitlines() if line.startswith("package:")}


def read_list(path):
    packages = []
    for line in path.read_text().splitlines():
        name = line.split("#", 1)[0].strip()
        if name:
            packages.append(name)
    return packages


def never_touch_rules():
    return read_list(PACKAGES_DIR / "never-touch.txt")


def is_protected(package, rules):
    if ".overlay" in package or ".rro" in package or package.endswith("overlay"):
        return True
    for rule in rules:
        if rule.endswith("*"):
            if package.startswith(rule[:-1]):
                return True
        elif package == rule:
            return True
    return False


def resolve_list(name):
    if name in BATCHES:
        return PACKAGES_DIR / BATCHES[name]
    path = Path(name)
    if path.is_file():
        return path
    die(f"unknown batch or file: {name} (choose from {', '.join(BATCHES)} or a .txt file)")


def log_change(action, package):
    LOG_DIR.mkdir(exist_ok=True)
    entry = {
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
        "device": device_serial(),
        "action": action,
        "package": package,
    }
    with CHANGE_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def disabled_by_tool():
    """Packages this tool disabled and has not re-enabled since, oldest first."""
    if not CHANGE_LOG.exists():
        return []
    state = {}
    for line in CHANGE_LOG.read_text().splitlines():
        entry = json.loads(line)
        state.pop(entry["package"], None)
        state[entry["package"]] = entry["action"]
    return [pkg for pkg, action in state.items() if action == "disable"]


def reboot_after_delay():
    print(f"Waiting {REBOOT_DELAY}s so the changes are saved, then rebooting...")
    time.sleep(REBOOT_DELAY)
    adb("reboot")
    print("Rebooting. Afterwards test: remote, Input button, every HDMI port,")
    print("picture modes, sound, CEC, AirPlay/Cast and a streaming app.")


def cmd_connect(args):
    target = args.address if ":" in args.address else f"{args.address}:5555"
    print(adb("connect", target))
    print("If the TV shows 'Allow USB debugging?', tick 'Always allow' and press OK,")
    print("then run: python3 tvdebloat.py info")


def cmd_info(args):
    print(f"device:          {device_serial()}")
    for label, prop in (
        ("model", "ro.product.model"),
        ("android version", "ro.build.version.release"),
        ("security patch", "ro.build.version.security_patch"),
        ("build", "ro.build.display.id"),
    ):
        print(f"{label + ':':<17}{shell(f'getprop {prop}')}")
    total = shell("grep MemTotal /proc/meminfo", check=False)
    avail = shell("grep MemAvailable /proc/meminfo", check=False)
    print(f"{'memory:':<17}{total.split(':')[-1].strip()} total, {avail.split(':')[-1].strip()} available")
    vt = sum(p.startswith("com.vt.") for p in package_set())
    print(f"{'com.vt.* pkgs:':<17}{vt}" + ("" if vt else "  (none: firmware differs from the U8N lists, check names carefully)"))


def cmd_baseline(args):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = LOG_DIR / f"baseline-{stamp}"
    out.mkdir(parents=True)
    files = {
        "all-packages.txt": "pm list packages",
        "system-packages.txt": "pm list packages -s",
        "disabled-before.txt": "pm list packages -d",
        "package-paths.txt": "pm list packages -f",
        "meminfo.txt": "dumpsys meminfo",
        "props.txt": "getprop",
    }
    for filename, command in files.items():
        (out / filename).write_text(shell(command, check=False) + "\n")
    print(f"Baseline saved to {out}")
    print("Keep this folder: it is your record of what was installed and already disabled.")


def cmd_check(args):
    path = resolve_list(args.batch)
    rules = never_touch_rules()
    installed, disabled = package_set(), package_set("-d")
    print(f"{path.name}:")
    for package in read_list(path):
        if is_protected(package, rules):
            status = "PROTECTED (never-touch list, will be skipped)"
        elif package not in installed:
            status = "not on this TV (will be skipped)"
        elif package in disabled:
            status = "already disabled"
        else:
            status = "enabled -> would be disabled"
        print(f"  {package:<45} {status}")


def cmd_apply(args):
    rules = never_touch_rules()
    if args.package:
        candidates, label = args.package, "custom"
    else:
        if not args.batch:
            die("give a batch (batch1..batch4) or --package <name>")
        path = resolve_list(args.batch)
        candidates, label = read_list(path), args.batch
        if args.batch in ONE_AT_A_TIME:
            if not args.only:
                die(f"{args.batch} is applied one package at a time: add --only <package>")
            if args.only not in candidates:
                die(f"{args.only} is not in {path.name}")
            candidates = [args.only]

    installed, disabled = package_set(), package_set("-d")

    if LAUNCHER_PAIR & set(candidates):
        if PROJECTIVY not in installed:
            die("Projectivy Launcher is not installed. Install it and turn on its override first (docs/setup-checklist.md, step 2).")
        if not LAUNCHER_PAIR <= set(candidates):
            die("launcherx and setupwraith must be disabled together (use batch4).")

    todo = []
    for package in candidates:
        if is_protected(package, rules):
            print(f"  skip {package}: on the never-touch list")
        elif package not in installed:
            print(f"  skip {package}: not on this TV")
        elif package in disabled:
            print(f"  skip {package}: already disabled")
        else:
            todo.append(package)

    if not todo:
        print("Nothing to do.")
        return
    print(f"\nAbout to disable ({label}):")
    for package in todo:
        print(f"  {package}")
    if not args.yes and input("Continue? [y/N] ").strip().lower() != "y":
        print("Cancelled.")
        return

    for package in todo:
        out = shell(f"pm disable-user --user 0 {package}", check=False)
        if "disabled" in out:
            log_change("disable", package)
            print(f"  disabled {package}")
        else:
            print(f"  FAILED {package}: {out}")
    print("Undo any of these with: python3 tvdebloat.py restore <package>   (or --all)")
    if args.reboot:
        reboot_after_delay()
    else:
        print(f"Wait about {REBOOT_DELAY}s, then reboot the TV (python3 tvdebloat.py reboot) and test it.")


def cmd_restore(args):
    if args.all:
        targets = list(reversed(disabled_by_tool()))
    elif args.packages:
        targets = args.packages
    else:
        die("give package names or --all")
    if not targets:
        print("This tool has no disabled packages on record.")
        return
    for package in targets:
        out = shell(f"pm enable --user 0 {package}", check=False)
        if "enabled" in out:
            log_change("enable", package)
            print(f"  enabled {package}")
        else:
            print(f"  FAILED {package}: {out}")
    if args.reboot:
        reboot_after_delay()


def cmd_status(args):
    mine = disabled_by_tool()
    disabled = package_set("-d")
    print("Disabled by this tool:")
    for package in mine:
        note = "" if package in disabled else "   <- ENABLED AGAIN (run: rearm)"
        print(f"  {package}{note}")
    if not mine:
        print("  (none)")
    others = sorted(disabled - set(mine))
    if others:
        print("\nOther disabled packages (factory-disabled or done by hand; leave them unless you know why):")
        for package in others:
            print(f"  {package}")


def cmd_rearm(args):
    disabled = package_set("-d")
    back = [p for p in disabled_by_tool() if p not in disabled]
    if not back:
        print("Everything this tool disabled is still disabled.")
        return
    for package in back:
        out = shell(f"pm disable-user --user 0 {package}", check=False)
        print(f"  {'re-disabled' if 'disabled' in out else 'FAILED'} {package}")


def cmd_tweaks(args):
    value = "0.5" if args.action == "apply" else "1"
    for key in ANIMATION_KEYS:
        shell(f"settings put global {key} {value}")
    print(f"Animation scales set to {value}x.")
    if args.action == "apply" and args.trim_cache:
        shell("pm trim-caches 32G", check=False)
        print("App caches cleared (apps rebuild them as needed).")


def cmd_reboot(args):
    reboot_after_delay()


def main():
    global serial
    if shutil.which("adb") is None:
        die("adb not found. Install Google's Android SDK Platform-Tools and add it to your PATH.")

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-s", "--serial", help="device to use when several are connected (e.g. 192.168.1.50:5555)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("connect", help="connect to the TV over the network")
    p.add_argument("address", help="TV IP address, optionally with :port (default 5555)")
    p.set_defaults(func=cmd_connect)

    sub.add_parser("info", help="show model, Android version, memory").set_defaults(func=cmd_info)
    sub.add_parser("baseline", help="save package lists and memory use before changing anything").set_defaults(func=cmd_baseline)

    p = sub.add_parser("check", help="show what a batch would do on this TV, without changing anything")
    p.add_argument("batch", help="batch1..batch4 or a path to a package list")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("apply", help="disable the packages in a batch")
    p.add_argument("batch", nargs="?", help="batch1..batch4 or a path to a package list")
    p.add_argument("--only", help="the single package to apply from a one-at-a-time batch (batch3)")
    p.add_argument("--package", action="append", help="disable a specific package instead of a batch (repeatable)")
    p.add_argument("--yes", action="store_true", help="don't ask for confirmation")
    p.add_argument("--reboot", action="store_true", help="wait 15s, then reboot the TV")
    p.set_defaults(func=cmd_apply)

    p = sub.add_parser("restore", help="re-enable packages this tool disabled")
    p.add_argument("packages", nargs="*")
    p.add_argument("--all", action="store_true", help="re-enable everything this tool disabled")
    p.add_argument("--reboot", action="store_true", help="wait 15s, then reboot the TV")
    p.set_defaults(func=cmd_restore)

    sub.add_parser("status", help="list what is disabled and flag anything that came back").set_defaults(func=cmd_status)
    sub.add_parser("rearm", help="re-disable packages that an update or reboot turned back on").set_defaults(func=cmd_rearm)

    p = sub.add_parser("tweaks", help="animation scales (apply = 0.5x, revert = 1x)")
    p.add_argument("action", choices=["apply", "revert"])
    p.add_argument("--trim-cache", action="store_true", help="also clear all app caches")
    p.set_defaults(func=cmd_tweaks)

    sub.add_parser("reboot", help="wait 15s, then reboot the TV").set_defaults(func=cmd_reboot)

    args = parser.parse_args()
    serial = args.serial
    args.func(args)


if __name__ == "__main__":
    main()
