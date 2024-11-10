#!/usr/bin/env python3
import argparse
import json
from subprocess import CalledProcessError, check_output as run
from typing import Union
from urllib.request import urlopen

arg_parser = argparse.ArgumentParser(
    prog="Catppuccin Theme - Gnome-Terminal Installation",
    description="Installs the Catppuccin theme for gnome-terminal",
)
arg_parser.add_argument("-l", "--local", action="store")
args = arg_parser.parse_args()

if args.local is None:
    try:
        url = "https://raw.githubusercontent.com/catppuccin/palette/refs/tags/v1.7.1/palette.json"
        res = urlopen(url).read().decode("utf-8")
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

gsettings_path_base = (
    "org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/"
)
gsettings_schema = "org.gnome.Terminal.ProfilesList"
# hardcoded uuids for each flavor
uuids = {
    "mocha": "95894cfd-82f7-430d-af6e-84d168bc34f5",
    "macchiato": "5083e06b-024e-46be-9cd2-892b814f1fc8",
    "frappe": "71a9971e-e829-43a9-9b2f-4565c855d664",
    "latte": "de8a9081-8352-4ce4-9519-5de655ad9361",
}


def gsettings_get(key: str):
    return json.loads(
        run(["gsettings", "get", gsettings_schema, key])
        .decode("utf-8")
        .replace("'", '"')
    )


def gsettings_set(
    key: str, value: Union[dict, list, str, bool], path: str = ""
) -> None:
    if type(value) in [dict, list]:
        value = json.dumps(value).replace('"', "'")
    elif type(value) is str:
        value = f"'{value}'"
    elif type(value) is bool:
        value = str(value).lower()

    if path:
        print(f"Setting {path}/ {key} to {value}")
        run(
            ["gsettings", "set", f"{gsettings_path_base}:{path}/", f"{key}", f"{value}"]
        )
    else:
        print(f"Setting {key} to {value}")
        run(["gsettings", "set", f"{gsettings_schema}", f"{key}", f"{value}"])


# handle the case where there are no profiles
try:
    profiles = gsettings_get("list")
except CalledProcessError:
    profiles = []

del palette["version"]
for flavor, color_obj in palette.items():
    uuid = uuids[flavor]
    colors = color_obj["colors"]
    ansi_colors = color_obj["ansiColors"]
    all_ansi_colors = [
        ansi_colors["black"]["normal"],
        ansi_colors["red"]["normal"],
        ansi_colors["green"]["normal"],
        ansi_colors["yellow"]["normal"],
        ansi_colors["blue"]["normal"],
        ansi_colors["magenta"]["normal"],
        ansi_colors["cyan"]["normal"],
        ansi_colors["white"]["normal"],
        ansi_colors["black"]["bright"],
        ansi_colors["red"]["bright"],
        ansi_colors["green"]["bright"],
        ansi_colors["yellow"]["bright"],
        ansi_colors["blue"]["bright"],
        ansi_colors["magenta"]["bright"],
        ansi_colors["cyan"]["bright"],
        ansi_colors["white"]["bright"],
    ]

    gsettings_set("visible-name", f"Catppuccin {flavor.capitalize()}", uuid)
    gsettings_set("background-color", colors["base"]["hex"], uuid)
    gsettings_set("foreground-color", colors["text"]["hex"], uuid)
    gsettings_set("highlight-colors-set", True, uuid)
    gsettings_set("highlight-background-color", colors["rosewater"]["hex"], uuid)
    gsettings_set("highlight-foreground-color", colors["surface2"]["hex"], uuid)
    gsettings_set("cursor-colors-set", True, uuid)
    gsettings_set("cursor-background-color", colors["rosewater"]["hex"], uuid)
    gsettings_set("cursor-foreground-color", colors["base"]["hex"], uuid)
    gsettings_set("use-theme-colors", False, uuid)
    gsettings_set("bold-is-bright", True, uuid)
    gsettings_set("palette", [color["hex"] for color in all_ansi_colors], uuid)

    if uuid not in profiles:
        profiles.append(uuid)

gsettings_set("list", profiles)
print("All profiles installed.")
