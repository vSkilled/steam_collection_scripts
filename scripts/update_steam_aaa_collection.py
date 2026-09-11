#!/usr/bin/env python3
"""
Steam "AAA" Collection Manager & Automator
==========================================
A reusable tool to safely manage and automate adding major blockbuster / AAA
games to the custom "AAA" collection in your local Steam library.

Operates against an extensive master catalog of blockbuster PC titles and
matches against the user's owned Steam library games.

Usage:
  python3 scripts/update_steam_aaa_collection.py --status
  python3 scripts/update_steam_aaa_collection.py --dry-run
  python3 scripts/update_steam_aaa_collection.py --apply
  python3 scripts/update_steam_aaa_collection.py --all-catalog
  python3 scripts/update_steam_aaa_collection.py --add 1593500
  python3 scripts/update_steam_aaa_collection.py --add "God of War"
  python3 scripts/update_steam_aaa_collection.py --scan
  python3 scripts/update_steam_aaa_collection.py --restore
"""

import argparse
import glob
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time
from typing import Dict, List, Optional, Set, Tuple

# Comprehensive Master Catalog of Major Blockbuster / AAA Steam Games
# Last Updated: September 11, 2026
MASTER_AAA_CATALOG: List[Tuple[int, str]] = [
    # --- PlayStation PC Flagships ---
    (1593500, "God of War"),
    (2322010, "God of War Ragnarök"),
    (1817070, "Marvel’s Spider-Man Remastered"),
    (1817190, "Marvel’s Spider-Man: Miles Morales"),
    (1151640, "Horizon Zero Dawn™ Complete Edition"),
    (2420110, "Horizon Forbidden West™ Complete Edition"),
    (2215430, "Ghost of Tsushima DIRECTOR'S CUT"),
    (1888930, "The Last of Us™ Part I"),
    (1259420, "Days Gone"),
    (1649240, "Returnal™"),
    (1895880, "Ratchet & Clank: Rift Apart"),
    (1659420, "UNCHARTED™: Legacy of Thieves Collection"),
    (2172010, "Until Dawn™"),
    (553850, "HELLDIVERS™ 2"),

    # --- Rockstar Games ---
    (271590, "Grand Theft Auto V Legacy"),
    (3240220, "Grand Theft Auto V Enhanced"),
    (12210, "Grand Theft Auto IV: The Complete Edition"),
    (1174180, "Red Dead Redemption 2"),
    (2668510, "Red Dead Redemption"),
    (204100, "Max Payne 3"),
    (110800, "L.A. Noire"),

    # --- FromSoftware & Soulslikes ---
    (1245620, "ELDEN RING"),
    (2778580, "ELDEN RING Shadow of the Erdtree"),
    (374320, "DARK SOULS™ III"),
    (570940, "DARK SOULS™: REMASTERED"),
    (335300, "DARK SOULS™ II: Scholar of the First Sin"),
    (814380, "Sekiro™: Shadows Die Twice - GOTY Edition"),
    (1888160, "ARMORED CORE™ VI FIRES OF RUBICON™"),
    (1627720, "Lies of P"),
    (1501750, "Lords of the Fallen"),
    (1282100, "REMNANT II®"),
    (617290, "Remnant: From the Ashes"),
    (2358720, "Black Myth: Wukong"),

    # --- CD Projekt Red ---
    (292030, "The Witcher 3: Wild Hunt - Complete Edition"),
    (20920, "The Witcher 2: Assassins of Kings Enhanced Edition"),
    (20900, "The Witcher: Enhanced Edition Director's Cut"),
    (1091500, "Cyberpunk 2077"),

    # --- Bethesda, id Software & Arkane ---
    (489830, "The Elder Scrolls V: Skyrim Special Edition"),
    (306130, "The Elder Scrolls Online"),
    (22330, "The Elder Scrolls IV: Oblivion® Game of the Year Edition Deluxe"),
    (1716740, "Starfield"),
    (377160, "Fallout 4"),
    (1151340, "Fallout 76"),
    (22380, "Fallout: New Vegas"),
    (22370, "Fallout 3: Game of the Year Edition"),
    (379720, "DOOM"),
    (782330, "DOOM Eternal"),
    (201810, "Wolfenstein: The New Order"),
    (350080, "Wolfenstein: The Old Blood"),
    (612880, "Wolfenstein II: The New Colossus"),
    (205100, "Dishonored"),
    (403640, "Dishonored 2"),
    (614570, "Dishonored®: Death of the Outsider™"),
    (480490, "Prey"),
    (1252330, "DEATHLOOP"),
    (1475810, "Ghostwire: Tokyo"),
    (268050, "The Evil Within"),
    (601430, "The Evil Within 2"),

    # --- Capcom ---
    (582010, "Monster Hunter: World"),
    (1446780, "MONSTER HUNTER RISE"),
    (2246340, "Monster Hunter Wilds"),
    (367500, "Dragon's Dogma: Dark Arisen"),
    (2054970, "Dragon's Dogma 2"),
    (883710, "Resident Evil 2"),
    (952060, "Resident Evil 3"),
    (2050650, "Resident Evil 4"),
    (21690, "Resident Evil 5"),
    (221040, "Resident Evil 6"),
    (418370, "Resident Evil 7 Biohazard"),
    (1196590, "Resident Evil Village"),
    (287290, "Resident Evil Revelations 2"),
    (601150, "Devil May Cry 5"),
    (1364780, "Street Fighter™ 6"),

    # --- Square Enix & JRPGs ---
    (1462040, "FINAL FANTASY VII REMAKE INTERGRADE"),
    (2515020, "FINAL FANTASY XVI"),
    (637650, "FINAL FANTASY XV WINDOWS EDITION"),
    (359870, "FINAL FANTASY X/X-2 HD Remaster"),
    (595520, "FINAL FANTASY XII THE ZODIAC AGE"),
    (1295510, "DRAGON QUEST XI S: Echoes of an Elusive Age – Definitive Edition"),
    (524220, "NieR:Automata™"),
    (1113560, "NieR Replicant™ ver.1.22474487139..."),
    (740130, "Tales of ARISE"),
    (337000, "Deus Ex: Mankind Divided™"),
    (238010, "Deus Ex: Human Revolution - Director's Cut"),
    (391220, "Rise of the Tomb Raider"),
    (750920, "Shadow of the Tomb Raider: Definitive Edition"),
    (203160, "Tomb Raider (2013)"),
    (225540, "Just Cause 3"),
    (517630, "Just Cause 4 Reloaded"),
    (202170, "Sleeping Dogs: Definitive Edition"),

    # --- Ubisoft Blockbusters ---
    (2208920, "Assassin's Creed Valhalla"),
    (812140, "Assassin's Creed® Odyssey"),
    (582160, "Assassin's Creed Origins"),
    (3035570, "Assassin's Creed Mirage"),
    (368500, "Assassin's Creed® Syndicate"),
    (289650, "Assassin's Creed® Unity"),
    (242050, "Assassin's Creed IV Black Flag"),
    (311560, "Assassin's Creed Rogue"),
    (208480, "Assassin's Creed® III"),
    (201870, "Assassin's Creed Revelations"),
    (2369390, "Far Cry 6"),
    (552520, "Far Cry® 5"),
    (939960, "Far Cry New Dawn"),
    (298110, "Far Cry 4"),
    (371660, "Far Cry Primal"),
    (220240, "Far Cry® 3"),
    (365590, "Tom Clancy's The Division"),
    (2221490, "Tom Clancy's The Division 2"),
    (460930, "Tom Clancy's Ghost Recon® Wildlands"),
    (2231380, "Tom Clancy's Ghost Recon® Breakpoint"),
    (359550, "Tom Clancy's Rainbow Six Siege"),
    (447040, "Watch_Dogs 2"),
    (2239550, "Watch Dogs®: Legion"),
    (243470, "Watch_Dogs"),
    (2221920, "Immortals Fenyx Rising"),
    (2840770, "Avatar: Frontiers of Pandora™"),
    (2842040, "Star Wars Outlaws"),

    # --- EA, BioWare, Respawn & DICE ---
    (1172380, "STAR WARS Jedi: Fallen Order™"),
    (1774580, "STAR WARS Jedi: Survivor™"),
    (1517290, "Battlefield™ 2042"),
    (1238840, "Battlefield™ 1"),
    (1238810, "Battlefield™ V"),
    (1238860, "Battlefield 4™"),
    (24960, "Battlefield: Bad Company™ 2"),
    (1328670, "Mass Effect™ Legendary Edition"),
    (1238000, "Mass Effect™: Andromeda Deluxe Edition"),
    (1222690, "Dragon Age™ Inquisition"),
    (1845910, "Dragon Age™: The Veilguard"),
    (1693980, "Dead Space (2023 Remake)"),
    (17470, "Dead Space (2008)"),
    (47780, "Dead Space 2"),
    (1237950, "Titanfall® 2"),
    (1222670, "The Sims™ 4"),
    (1262580, "Need for Speed™ Heat"),
    (1846380, "Need for Speed™ Unbound"),

    # --- Warner Bros & DC ---
    (990080, "Hogwarts Legacy"),
    (208650, "Batman™: Arkham Knight"),
    (200260, "Batman: Arkham City GOTY"),
    (35140, "Batman: Arkham Asylum GOTY Edition"),
    (209000, "Batman™: Arkham Origins"),
    (1496790, "Gotham Knights"),
    (241930, "Middle-earth™: Shadow of Mordor™"),
    (356190, "Middle-earth™: Shadow of War™"),
    (234140, "Mad Max"),
    (1971870, "Mortal Kombat 1"),
    (976310, "Mortal Kombat 11"),
    (307780, "Mortal Kombat X"),
    (237110, "Mortal Kombat Komplete Edition"),
    (924970, "Back 4 Blood"),

    # --- 2K, Firaxis & Gearbox ---
    (397540, "Borderlands 3"),
    (49520, "Borderlands 2"),
    (261640, "Borderlands: The Pre-Sequel"),
    (1286680, "Tiny Tina's Wonderlands"),
    (289070, "Sid Meier's Civilization VI"),
    (8930, "Sid Meier's Civilization V"),
    (268500, "XCOM 2"),
    (200510, "XCOM: Enemy Unknown"),
    (368260, "Marvel's Midnight Suns"),
    (409710, "BioShock™ Remastered"),
    (409720, "BioShock™ 2 Remastered"),
    (8870, "BioShock Infinite"),
    (1030840, "Mafia: Definitive Edition"),
    (1030830, "Mafia II: Definitive Edition"),
    (360430, "Mafia III: Definitive Edition"),

    # --- Xbox Game Studios & Microsoft ---
    (976730, "Halo: The Master Chief Collection"),
    (1240440, "Halo Infinite"),
    (1551360, "Forza Horizon 5"),
    (1293830, "Forza Horizon 4"),
    (2440510, "Forza Motorsport"),
    (1097840, "Gears 5"),
    (1184050, "Gears Tactics"),
    (414340, "Hellblade: Senua's Sacrifice"),
    (2461850, "Senua’s Saga: Hellblade II"),
    (1172620, "Sea of Thieves: 2026 Edition"),
    (495420, "State of Decay 2"),
    (2457220, "Avowed"),

    # --- Sega, Atlus & Ryu Ga Gotoku ---
    (638970, "Yakuza 0"),
    (834530, "Yakuza Kiwami"),
    (927380, "Yakuza Kiwami 2"),
    (1235140, "Yakuza: Like a Dragon"),
    (2072450, "Like a Dragon: Infinite Wealth"),
    (1687950, "Persona 5 Royal"),
    (2161700, "Persona 3 Reload"),
    (1113000, "Persona 4 Golden"),
    (1875830, "Shin Megami Tensei V: Vengeance"),
    (2679460, "Metaphor: ReFantazio"),
    (364360, "Total War: WARHAMMER"),
    (594570, "Total War: WARHAMMER II"),
    (1142710, "Total War: WARHAMMER III"),
    (779340, "Total War: THREE KINGDOMS"),
    (214490, "Alien: Isolation"),

    # --- Larian Studios ---
    (1086940, "Baldur's Gate 3"),
    (435150, "Divinity: Original Sin 2"),
    (373420, "Divinity: Original Sin Enhanced Edition"),

    # --- Blizzard, Activision & Valve ---
    (2344520, "Diablo® IV"),
    (202970, "Call of Duty: Black Ops II"),
    (209170, "Call of Duty: Ghosts - Multiplayer"),
    (730, "Counter-Strike 2"),
    (220, "Half-Life 2"),

    # --- Other Major Blockbusters & Releases ---
    (2183900, "Warhammer 40,000: Space Marine 2"),
    (1850570, "DEATH STRANDING DIRECTOR'S CUT"),
    (1643320, "S.T.A.L.K.E.R. 2: Heart of Chornobyl"),
    (379430, "Kingdom Come: Deliverance"),
    (1771300, "Kingdom Come: Deliverance II"),
    (752590, "A Plague Tale: Innocence"),
    (1182900, "A Plague Tale: Requiem"),
    (239140, "Dying Light"),
    (534380, "Dying Light 2 Stay Human"),
    (1544020, "The Callisto Protocol"),
    (870780, "Control Ultimate Edition"),
    (275850, "No Man's Sky"),
    (1085660, "Destiny 2"),
    (1063730, "New World: Aeternum"),
    (2429640, "Throne and Liberty"),
    (1599340, "Lost Ark"),
    (582660, "Black Desert"),
    (2694490, "Path of Exile 2"),
    (1659040, "HITMAN World of Assassination"),
    (863550, "HITMAN™ 2"),
    (236870, "HITMAN™"),
    (203140, "Hitman: Absolution"),
    (813780, "Age of Empires II: Definitive Edition"),
    (933110, "Age of Empires III: Definitive Edition"),
    (255710, "Cities: Skylines"),
    (949230, "Cities: Skylines II"),
    (648350, "Jurassic World Evolution"),
    (1244460, "Jurassic World Evolution 2"),
    (703080, "Planet Zoo"),
    (493340, "Planet Coaster"),
    (281990, "Stellaris"),
    (2399830, "ARK: Survival Ascended"),
    (346110, "ARK: Survival Evolved"),
    (1623730, "Palworld"),
    (2456740, "inZOI"),
    (3564740, "Where Winds Meet"),
    (3321460, "Crimson Desert Enhanced"),
]

# Alias for backward compatibility
DEFAULT_AAA_CATALOG = MASTER_AAA_CATALOG


def find_steam_root() -> str:
    """Locate the Steam base installation path on Linux."""
    candidates = [
        os.path.expanduser("~/.local/share/Steam"),
        os.path.expanduser("~/.steam/steam"),
        os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam"),
    ]
    for path in candidates:
        if os.path.isdir(path) and os.path.isdir(os.path.join(path, "userdata")):
            return path
    raise FileNotFoundError("Could not find Steam installation directory.")


def find_steam_userdata_dir(steam_root: str, user_id: Optional[str] = None) -> str:
    """Find the specific user's userdata directory."""
    userdata_base = os.path.join(steam_root, "userdata")
    if not os.path.isdir(userdata_base):
        raise FileNotFoundError(f"Userdata directory not found at {userdata_base}")

    if user_id:
        user_dir = os.path.join(userdata_base, user_id)
        if os.path.isdir(user_dir):
            return user_dir
        raise FileNotFoundError(f"Specified Steam user ID {user_id} not found in {userdata_base}")

    # 1. Try checking loginusers.vdf for the active / most recent user
    loginusers_path = os.path.join(steam_root, "config", "loginusers.vdf")
    if os.path.isfile(loginusers_path):
        try:
            with open(loginusers_path, "r", errors="ignore") as f:
                content = f.read()
            user_blocks = re.findall(r'"(\d{17})"\s*\{([^}]+)\}', content)
            best_id = None
            best_score = -1
            for steam64, block in user_blocks:
                score = 0
                if "FalseBit" in block:
                    score += 1000
                if '"MostRecent"\t\t"1"' in block or '"MostRecent" "1"' in block:
                    score += 500
                if '"AutoLogin"\t\t"1"' in block or '"AutoLogin" "1"' in block:
                    score += 300
                ts_m = re.search(r'"Timestamp"\s*"(\d+)"', block)
                if ts_m:
                    score += int(ts_m.group(1)) / 1e10
                if score > best_score:
                    best_score = score
                    steam3 = int(steam64) - 76561197960265728
                    best_id = str(steam3)
            if best_id and os.path.isdir(os.path.join(userdata_base, best_id)):
                return os.path.join(userdata_base, best_id)
        except Exception:
            pass

    # 2. Check which directory contains the AAA collection
    for d in os.listdir(userdata_base):
        if d == "0":
            continue
        candidate = os.path.join(userdata_base, d)
        ns1 = os.path.join(candidate, "config", "cloudstorage", "cloud-storage-namespace-1.json")
        if os.path.isfile(ns1):
            try:
                with open(ns1, "r", encoding="utf-8") as f:
                    if "AAA" in f.read():
                        return candidate
            except Exception:
                pass

    # 3. Fallback: non-zero directory with most recent cloudstorage modification
    subdirs = [
        d for d in os.listdir(userdata_base)
        if d != "0" and os.path.isdir(os.path.join(userdata_base, d))
    ]
    if not subdirs:
        raise FileNotFoundError(f"No user accounts found in {userdata_base}")

    def get_user_activity(d: str) -> float:
        cs = os.path.join(userdata_base, d, "config", "cloudstorage")
        if os.path.exists(cs):
            return os.path.getmtime(cs)
        return os.path.getmtime(os.path.join(userdata_base, d))

    subdirs.sort(key=get_user_activity, reverse=True)
    return os.path.join(userdata_base, subdirs[0])


def is_steam_running() -> bool:
    """Check if the Steam client is currently running."""
    try:
        output = subprocess.check_output(["pgrep", "-a", "steam"], stderr=subprocess.DEVNULL)
        lines = [line.strip() for line in output.decode("utf-8").splitlines() if line.strip()]
        running = [l for l in lines if "update_steam_aaa_collection" not in l and "pgrep" not in l]
        return len(running) > 0
    except subprocess.CalledProcessError:
        return False


def parse_appinfo_names(steam_root: str) -> Dict[int, str]:
    """Parse Steam's binary appcache/appinfo.vdf to map AppID -> Game Name."""
    appinfo_path = os.path.join(steam_root, "appcache", "appinfo.vdf")
    if not os.path.isfile(appinfo_path):
        return {}

    with open(appinfo_path, "rb") as f:
        buf = f.read()

    if len(buf) < 16:
        return {}

    magic, universe, str_offset = struct.unpack("<IIQ", buf[:16])
    if str_offset >= len(buf):
        return {}

    pos = str_offset
    num_strings = struct.unpack("<I", buf[pos:pos+4])[0]
    pos += 4
    strings = []
    for _ in range(num_strings):
        end = buf.find(b"\x00", pos)
        if end == -1:
            break
        strings.append(buf[pos:end].decode("utf-8", errors="ignore"))
        pos = end + 1

    try:
        name_idx = strings.index("name")
    except ValueError:
        name_idx = 4
    name_token = struct.pack("<I", name_idx)

    names: Dict[int, str] = {}
    pos = 16
    while pos < str_offset:
        if pos + 8 > str_offset:
            break
        appid, size = struct.unpack("<II", buf[pos:pos+8])
        if appid == 0:
            break
        rec_data = buf[pos+8 : pos+8+size]
        name_pos = rec_data.find(b"\x01" + name_token)
        if name_pos != -1:
            end = rec_data.find(b"\x00", name_pos + 5)
            if end != -1:
                game_name = rec_data[name_pos+5:end].decode("utf-8", errors="ignore")
                names[appid] = game_name
        pos += 8 + size

    return names


def get_owned_game_ids(user_dir: str) -> Set[int]:
    """Read owned/played app IDs from localconfig.vdf."""
    localconfig_path = os.path.join(user_dir, "config", "localconfig.vdf")
    if not os.path.isfile(localconfig_path):
        return set()

    with open(localconfig_path, "r", errors="ignore") as f:
        lines = f.readlines()

    in_apps = False
    depth = 0
    app_ids = set()
    for line in lines:
        if '"apps"' in line and not in_apps:
            in_apps = True
            depth = line.count("\t")
            continue
        if in_apps:
            cur_depth = line.count("\t")
            if line.strip() == "{":
                continue
            if line.strip() == "}":
                if cur_depth <= depth:
                    break
            if cur_depth == depth + 1 and line.strip().startswith('"'):
                name = line.strip().split('"')[1]
                if name.isdigit():
                    app_ids.add(int(name))

    return app_ids


def create_backup(cloudstorage_dir: str) -> str:
    """Create a timestamped backup of the cloudstorage directory."""
    backup_dir = os.path.join(cloudstorage_dir, "backups", f"backup_{int(time.time())}")
    os.makedirs(backup_dir, exist_ok=True)
    for fname in os.listdir(cloudstorage_dir):
        full_path = os.path.join(cloudstorage_dir, fname)
        if os.path.isfile(full_path):
            shutil.copy2(full_path, backup_dir)
    return backup_dir


def restore_backup(cloudstorage_dir: str) -> bool:
    """Restore from the most recent backup."""
    backups_parent = os.path.join(cloudstorage_dir, "backups")
    if not os.path.isdir(backups_parent):
        print("[-] No backups found.")
        return False

    entries = [
        os.path.join(backups_parent, d)
        for d in os.listdir(backups_parent)
        if os.path.isdir(os.path.join(backups_parent, d))
    ]
    if not entries:
        print("[-] No backup directories found.")
        return False

    entries.sort(key=os.path.getmtime, reverse=True)
    latest_backup = entries[0]
    print(f"[*] Restoring from {latest_backup}...")
    for fname in os.listdir(latest_backup):
        src = os.path.join(latest_backup, fname)
        dst = os.path.join(cloudstorage_dir, fname)
        shutil.copy2(src, dst)
    print("[+] Restore completed successfully.")
    return True


def load_cloud_storage(cloudstorage_dir: str):
    """Load namespace 1 and related files."""
    ns1_path = os.path.join(cloudstorage_dir, "cloud-storage-namespace-1.json")
    if not os.path.isfile(ns1_path):
        raise FileNotFoundError(f"Namespace 1 file not found at {ns1_path}")

    with open(ns1_path, "r", encoding="utf-8") as f:
        ns1_data = json.load(f)

    return ns1_data


def find_collection_entry(ns1_data: list, target_name: str = "AAA") -> Tuple[Optional[str], Optional[dict]]:
    """Find the specific user collection by its display name."""
    for item in ns1_data:
        key = item[0]
        meta = item[1]
        if key.startswith("user-collections."):
            val_str = meta.get("value", "")
            try:
                val_data = json.loads(val_str)
                if val_data.get("name") == target_name:
                    return key, meta
            except Exception:
                pass
    return None, None


def show_status(user_dir: str, steam_root: str):
    """Print the current state of the AAA collection."""
    cs_dir = os.path.join(user_dir, "config", "cloudstorage")
    ns1_data = load_cloud_storage(cs_dir)
    key, meta = find_collection_entry(ns1_data, "AAA")
    if not meta:
        print("[-] 'AAA' collection not found.")
        return

    val = json.loads(meta["value"])
    added_ids = val.get("added", [])
    name_map = parse_appinfo_names(steam_root)

    print(f"\n=======================================================")
    print(f" STEAM 'AAA' COLLECTION STATUS (ID: {val.get('id')})")
    print(f" Total Games Currently in Collection: {len(added_ids)}")
    print(f"=======================================================")
    for aid in added_ids:
        title = name_map.get(aid, f"AppID {aid}")
        print(f"  [{aid:>8}] {title}")
    print(f"=======================================================\n")


def update_collection(
    user_dir: str,
    steam_root: str,
    apps_to_add: List[Tuple[int, str]],
    dry_run: bool = False,
    force: bool = False,
    filter_owned: bool = True,
) -> bool:
    """Safely append games to the AAA collection and trigger cloud sync."""
    if is_steam_running():
        if not force and not dry_run:
            print("[!] ERROR: Steam is currently running!")
            print("    Please exit Steam completely before modifying collection files,")
            print("    otherwise Steam will overwrite your changes upon closing.")
            print("    (You can use --force to override, but closing Steam is strongly advised).")
            return False
        elif dry_run:
            print("[!] Note: Steam is running, but this is a DRY RUN so no files will be changed.")

    cs_dir = os.path.join(user_dir, "config", "cloudstorage")
    ns1_path = os.path.join(cs_dir, "cloud-storage-namespace-1.json")
    ns_meta_path = os.path.join(cs_dir, "cloud-storage-namespaces.json")
    modified_path = os.path.join(cs_dir, "cloud-storage-namespace-1.modified.json")

    ns1_data = load_cloud_storage(cs_dir)
    coll_key, coll_meta = find_collection_entry(ns1_data, "AAA")
    if not coll_meta:
        print("[-] Error: 'AAA' collection could not be found in cloud storage.")
        return False

    val = json.loads(coll_meta["value"])
    existing_added = set(val.get("added", []))
    name_map = parse_appinfo_names(steam_root)

    # Filter against owned library games if filter_owned is True
    if filter_owned:
        owned_ids = get_owned_game_ids(user_dir)
        if owned_ids:
            eligible_apps = [app for app in apps_to_add if app[0] in owned_ids]
            print(f"[*] Scanned Master Catalog ({len(apps_to_add)} titles) against owned library ({len(owned_ids)} titles):")
            print(f"[*] Found {len(eligible_apps)} matching blockbuster games owned by this account.")
        else:
            eligible_apps = apps_to_add
    else:
        print(f"[*] Processing entire Master Catalog ({len(apps_to_add)} titles) without library ownership filter.")
        eligible_apps = apps_to_add

    # Filter out games already present in the collection
    new_apps = [app for app in eligible_apps if app[0] not in existing_added]

    print(f"[*] Target Collection: AAA ({coll_key})")
    print(f"[*] Current collection size: {len(existing_added)} games")
    print(f"[*] New games to be added:   {len(new_apps)} games")

    if not new_apps:
        print("\n[+] All eligible blockbuster games are already present in your AAA collection!")
        return True

    print("\n--- Games to be added ---")
    for aid, name in new_apps:
        display_name = name or name_map.get(aid, f"AppID {aid}")
        print(f"  + [{aid:>8}] {display_name}")

    if dry_run:
        print("\n[+] Dry run complete. No files were modified.")
        return True

    # 1. Create safety backup
    bdir = create_backup(cs_dir)
    print(f"\n[+] Created safety backup at: {bdir}")

    # 2. Update collection value
    updated_added = list(val.get("added", []))
    for aid, _ in new_apps:
        updated_added.append(aid)

    val["added"] = updated_added
    coll_meta["value"] = json.dumps(val, separators=(",", ":"))
    coll_meta["timestamp"] = int(time.time())

    # Find highest version number to increment
    max_ver = 2000
    for item in ns1_data:
        ver = item[1].get("version")
        if ver and str(ver).isdigit():
            max_ver = max(max_ver, int(ver))

    new_ver = str(max_ver + 1)
    coll_meta["version"] = new_ver

    # 3. Write updated namespace-1.json
    with open(ns1_path, "w", encoding="utf-8") as f:
        json.dump(ns1_data, f, separators=(",", ":"))
    print(f"[+] Updated {ns1_path} (version {new_ver})")

    # 4. Mark modified key in modified.json
    modified_keys = []
    if os.path.isfile(modified_path):
        try:
            with open(modified_path, "r", encoding="utf-8") as f:
                modified_keys = json.load(f)
        except Exception:
            modified_keys = []

    if coll_key not in modified_keys:
        modified_keys.append(coll_key)

    with open(modified_path, "w", encoding="utf-8") as f:
        json.dump(modified_keys, f, separators=(",", ":"))
    print(f"[+] Marked {coll_key} in {modified_path} for Cloud sync")

    # 5. Update namespaces version map
    if os.path.isfile(ns_meta_path):
        try:
            with open(ns_meta_path, "r", encoding="utf-8") as f:
                ns_meta = json.load(f)
            for entry in ns_meta:
                if entry[0] == 1:
                    entry[1] = new_ver
            with open(ns_meta_path, "w", encoding="utf-8") as f:
                json.dump(ns_meta, f, separators=(",", ":"))
            print(f"[+] Updated {ns_meta_path}")
        except Exception as e:
            print(f"[!] Warning updating namespaces.json: {e}")

    print("\n=======================================================")
    print(f" SUCCESS: Added {len(new_apps)} games to 'AAA' collection!")
    print(f" New Total Games in AAA Collection: {len(updated_added)}")
    print(" You can now launch Steam. It will automatically detect")
    print(" the updated collection and sync it to Steam Cloud.")
    print("=======================================================\n")
    return True


def search_library(user_dir: str, steam_root: str, query: Optional[str] = None):
    """Scan library games and display matches."""
    name_map = parse_appinfo_names(steam_root)
    owned_ids = get_owned_game_ids(user_dir)

    print(f"\n[*] Scanning library for user {os.path.basename(user_dir)}...")
    print(f"[*] Found {len(owned_ids)} owned/played titles.")

    results = []
    for aid in owned_ids:
        title = name_map.get(aid)
        if not title:
            continue
        if query:
            if query.lower() in title.lower():
                results.append((aid, title))
        else:
            results.append((aid, title))

    results.sort(key=lambda x: x[1].lower())
    print(f"\nFound {len(results)} matching titles:")
    for aid, title in results[:60]:
        print(f"  [{aid:>8}] {title}")
    if len(results) > 60:
        print(f"  ... and {len(results) - 60} more.")


def main():
    parser = argparse.ArgumentParser(
        description="Steam 'AAA' Collection Manager & Automator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--status", action="store_true", help="Show all games currently in the AAA collection")
    parser.add_argument("--apply", action="store_true", help="Scan owned library against Master Catalog and add all owned blockbusters")
    parser.add_argument("--all-catalog", action="store_true", help="Add ALL games from the Master Catalog without filtering by owned games")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying any files")
    parser.add_argument("--add", nargs="+", help="Add specific game(s) by AppID or Title (e.g. --add 1593500)")
    parser.add_argument("--scan", nargs="?", const="", help="Search owned library games (optional search term)")
    parser.add_argument("--restore", action="store_true", help="Restore cloudstorage from the latest backup")
    parser.add_argument("--user", help="Specify Steam3 User ID (e.g. 22334621)")
    parser.add_argument("--force", action="store_true", help="Force write even if Steam process is detected")

    args = parser.parse_args()

    try:
        steam_root = find_steam_root()
        user_dir = find_steam_userdata_dir(steam_root, args.user)
    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)

    if args.status:
        show_status(user_dir, steam_root)
    elif args.restore:
        cs_dir = os.path.join(user_dir, "config", "cloudstorage")
        restore_backup(cs_dir)
    elif args.scan is not None:
        search_library(user_dir, steam_root, args.scan if args.scan else None)
    elif args.add:
        name_map = parse_appinfo_names(steam_root)
        apps_to_add = []
        for item in args.add:
            if item.isdigit():
                aid = int(item)
                name = name_map.get(aid, f"AppID {aid}")
                apps_to_add.append((aid, name))
            else:
                matched = [(aid, name) for aid, name in name_map.items() if item.lower() in name.lower()]
                if matched:
                    apps_to_add.append(matched[0])
                else:
                    print(f"[-] Could not find game matching '{item}'")
        if apps_to_add:
            update_collection(user_dir, steam_root, apps_to_add, dry_run=args.dry_run, force=args.force, filter_owned=False)
    elif args.all_catalog:
        update_collection(user_dir, steam_root, MASTER_AAA_CATALOG, dry_run=args.dry_run, force=args.force, filter_owned=False)
    elif args.apply or args.dry_run:
        update_collection(user_dir, steam_root, MASTER_AAA_CATALOG, dry_run=args.dry_run, force=args.force, filter_owned=True)
    else:
        show_status(user_dir, steam_root)
        parser.print_help()


if __name__ == "__main__":
    main()
