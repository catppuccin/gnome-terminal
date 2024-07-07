#!/usr/bin/env python3
import json
import argparse
from urllib.request import urlopen
from subprocess import check_output as run
from typing import Union

arg_parser = argparse.ArgumentParser(prog='Catppuccin Theme - Gnome-Terminal Installation',
                                     description='Installs the catppuccin theme for gnome-terminal')
arg_parser.add_argument('-l', '--local', action='store')
args = arg_parser.parse_args()

if args.local is None:
    try:
        palette_repo = "https://raw.githubusercontent.com/catppuccin/palette"
        commit_sha = "407fb8c7f0ddee55bd10999c9b7e78f8fec256c5"
        res = urlopen(f"{palette_repo}/{commit_sha}/palette.json").read().decode("utf-8")
        palette = json.loads(res)
    except Exception as e:
        print(f"Error fetching the palette: {e}")
        exit(1)
else:
    try:
        with open(args.local) as local_palette:
            palette = json.load(local_palette)
    except Exception as e:
        print(f"Error fetching the palette: {e}")
        exit(1)

gsettings_path_base = "org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/"
gsettings_schema = "org.gnome.Terminal.ProfilesList"
# hardcoded uuids for each flavour
uuids = {
    "mocha": "95894cfd-82f7-430d-af6e-84d168bc34f5",
    "macchiato": "5083e06b-024e-46be-9cd2-892b814f1fc8",
    "frappe": "71a9971e-e829-43a9-9b2f-4565c855d664",
    "latte": "de8a9081-8352-4ce4-9519-5de655ad9361",
}


def gsettings_get(key: str):
    return json.loads(
        run(["gsettings", "get", gsettings_schema, key]).decode("utf-8").replace("'", '"')
    )


def gsettings_set(key: str, value: Union[dict, list, str, bool], path: str = "") -> None:
    if type(value) in [dict, list]:
        value = json.dumps(value).replace('"', "'")
    elif type(value) == str:
        value = f"'{value}'"
    elif type(value) == bool:
        value = str(value).lower()

    if path:
        print(f"Setting {path}/ {key} to {value}")
        run(["gsettings", "set", f"{gsettings_path_base}:{path}/", f"{key}", f"{value}"])
    else:
        print(f"Setting {key} to {value}")
        run(["gsettings", "set", f"{gsettings_schema}", f"{key}", f"{value}"])


# handle the case where there are no profiles
try:
    profiles = gsettings_get("list")
except:
    profiles = []

for flavour, colours in palette.items():
    uuid = uuids[flavour]
    gsettings_set("visible-name", f"Catppuccin {flavour.capitalize()}", f"{uuid}")
    gsettings_set("background-color", colours["base"]["hex"], f"{uuid}")
    gsettings_set("foreground-color", colours["text"]["hex"], f"{uuid}")
    gsettings_set("highlight-colors-set", True, f"{uuid}")
    gsettings_set("highlight-background-color", colours["rosewater"]["hex"], f"{uuid}")
    gsettings_set("highlight-foreground-color", colours["surface2"]["hex"], f"{uuid}")
    gsettings_set("cursor-colors-set", True, f"{uuid}")
    gsettings_set("cursor-background-color", colours["rosewater"]["hex"], f"{uuid}")
    gsettings_set("cursor-foreground-color", colours["base"]["hex"], f"{uuid}")

    isLatte = flavour == "latte"
    colors = [
        isLatte and colours["subtext1"] or colours["surface1"],
        colours["red"],
        colours["green"],
        colours["yellow"],
        colours["blue"],
        colours["pink"],
        colours["teal"],
        isLatte and colours["surface2"] or colours["subtext1"],
        isLatte and colours["subtext0"] or colours["surface2"],
        colours["red"],
        colours["green"],
        colours["yellow"],
        colours["blue"],
        colours["pink"],
        colours["teal"],
        isLatte and colours["surface1"] or colours["subtext0"],
    ]
    gsettings_set("use-theme-colors", False, f"{uuid}")
    # get only the hex key from each entry in colors
    gsettings_set("palette", [color["hex"] for color in colors], f"{uuid}")

    if uuid not in profiles:
        profiles.append(uuid)

gsettings_set("list", profiles)
print("All profiles installed.")
