#!/usr/bin/env python3
"""deskRemote rebrand script (RustDesk fork).

Run from the repository ROOT (after `git submodule update --init`):
    python deskremote/rebrand.py

Idempotent: running twice is harmless. Exits with code 1 if an expected
text is not found (so CI fails loudly instead of building a half-renamed app).
RustDesk copyright notices and LICENCE are intentionally NOT touched (AGPL-3.0).
"""
import json, os, re, sys

# Windows CI consoles use cp1252 and crash on Korean text -> force UTF-8 output
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))
EN, KO = cfg["app_name_en"], cfg["app_name_ko"]
failed = []


def path(p):
    return os.path.join(ROOT, *p.split("/"))


def edit(rel, pairs, regex=False, required=True):
    fp = path(rel)
    if not os.path.exists(fp):
        failed.append(f"missing file: {rel}")
        return
    s = open(fp, encoding="utf-8").read()
    for old, new in pairs:
        if regex:
            s2, n = re.subn(old, new, s)
        else:
            n = s.count(old)
            s2 = s.replace(old, new)
        if n == 0 and new not in s and required:
            failed.append(f"pattern not found in {rel}: {old[:60]}")
        s = s2
    open(fp, "w", encoding="utf-8", newline="").write(s)
    print("patched", rel)


# 1) App name (default value) + optional server settings: hbb_common is a submodule
edit("libs/hbb_common/src/config.rs",
     [('RwLock::new("RustDesk".to_owned())', f'RwLock::new("{EN}".to_owned())')])
# Server settings: environment variables (GitHub Secrets) win over config.json.
# NEVER commit real values to a public repository.
host = os.environ.get("DESKREMOTE_SERVER_HOST", "").strip() or cfg.get("server_host", "").strip()
key = os.environ.get("DESKREMOTE_SERVER_KEY", "").strip() or cfg.get("server_key", "").strip()
if host or key:
    if not (host and key):
        failed.append("server host and key must be set together")
    elif not re.fullmatch(r"[A-Za-z0-9.\-]+(:[0-9]{1,5})?", host):
        failed.append("server host has invalid characters")
    elif not re.fullmatch(r"[A-Za-z0-9+/]{30,60}={0,2}", key):
        failed.append("server key has invalid format")
    else:
        edit("libs/hbb_common/src/config.rs",
             [(r'RENDEZVOUS_SERVERS: &\[&str\] = &\[[^\]]*\];',
               f'RENDEZVOUS_SERVERS: &[&str] = &["{host}"];'),
              (r'RS_PUB_KEY: &str = "[^"]*";',
               f'RS_PUB_KEY: &str = "{key}";')], regex=True)
        print("custom server applied (values hidden)")
else:
    print("WARNING: no server configured -> client will use RustDesk public servers (test only).")

# 2) Windows file properties
edit("Cargo.toml", [
    ('ProductName = "RustDesk"', f'ProductName = "{EN}"'),
    ('FileDescription = "RustDesk Remote Desktop"', f'FileDescription = "{cfg["description"]}"'),
    ('name = "RustDesk"\nidentifier = "com.carriez.rustdesk"',
     f'name = "{EN}"\nidentifier = "{cfg["bundle_identifier"]}"'),
])
edit("flutter/windows/runner/Runner.rc", [
    ('"FileDescription", "RustDesk Remote Desktop"', f'"FileDescription", "{cfg["description"]}"'),
    ('"ProductName", "RustDesk"', f'"ProductName", "{EN}"'),
])

# 2b) Installer fix: the build output is rustdesk.exe, but the installer launches
#     "<app name>.exe". Add the missing rename step to the install flow (the update
#     flow already has it).
edit("src/platform/windows.rs", [
    ("{copy_exe}\nreg add {subkey} /f\nreg add {subkey} /f /v DisplayIcon",
     "{copy_exe}\n{rename_exe}\nreg add {subkey} /f\nreg add {subkey} /f /v DisplayIcon"),
    ("        copy_exe = copy_exe_cmd(&src_exe, &exe, &path)?,\n        import_config = get_import_config(&exe),",
     "        copy_exe = copy_exe_cmd(&src_exe, &exe, &path)?,\n        rename_exe = rename_exe_cmd(&src_exe, &path)?,\n        import_config = get_import_config(&exe),"),
])

# 3) UI strings (Korean / English)
for rel, name in (("src/lang/ko.rs", KO), ("src/lang/en.rs", EN)):
    fp = path(rel)
    s = open(fp, encoding="utf-8").read()
    open(fp, "w", encoding="utf-8", newline="").write(s.replace("RustDesk", name))
    print("patched", rel)

# 4) Icons
try:
    from PIL import Image
    src = Image.open(os.path.join(HERE, "icon_1024.png")).convert("RGBA")
    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    for rel in ("res/icon.ico", "res/tray-icon.ico", "flutter/windows/runner/resources/app_icon.ico"):
        src.save(path(rel), sizes=ico_sizes)
    for rel, px in (("res/32x32.png", 32), ("res/64x64.png", 64), ("res/128x128.png", 128),
                    ("res/128x128@2x.png", 256), ("res/icon.png", 512), ("res/mac-icon.png", 512)):
        src.resize((px, px), Image.LANCZOS).save(path(rel))
    print("icons replaced")
except Exception as e:  # pillow missing etc.
    failed.append(f"icon step failed: {e}")

if failed:
    print("\nREBRAND FAILED:")
    for f in failed:
        print(" -", f)
    sys.exit(1)
print("\nREBRAND OK ->", EN, "/", KO)
