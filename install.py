#!/usr/bin/env python3
import json
from urllib.request import urlopen
from subprocess import check_output as run
from typing import Union

try:
    palette_repo = "https://raw.githubusercontent.com/catppuccin/palette"
    commit_sha = "407fb8c7f0ddee55bd10999c9b7e78f8fec256c5"
    res = urlopen(f"{palette_repo}/{commit_sha}/palette.json").read().decode("utf-8")
    palette = json.loads(res)
except Exception as e:
    print(f"Error fetching the palette: {e}")
    exit(1)

dconf_root = "/org/gnome/terminal/legacy/profiles:"
# hardcoded uuids for each flavour
uuids = {
    "mocha": "95894cfd-82f7-430d-af6e-84d168bc34f5",
    "macchiato": "5083e06b-024e-46be-9cd2-892b814f1fc8",
    "frappe": "71a9971e-e829-43a9-9b2f-4565c855d664",
    "latte": "de8a9081-8352-4ce4-9519-5de655ad9361",
}


def dconf_get(path: str):
    return json.loads(
        run(["dconf", "read", f"{dconf_root}/{path}"]).decode("utf-8").replace("'", '"')
    )


def dconf_set(path: str, data: Union[dict, list, str, bool]) -> None:
    if type(data) in [dict, list]:
        data = json.dumps(data).replace('"', "'")
    elif type(data) == str:
        data = f"'{data}'"
    elif type(data) == bool:
        data = str(data).lower()

    print(f"Setting {path} to {data}")

    run(["dconf", "write", f"{dconf_root}/{path}", f"{data}"])


# handle the case where there are no profiles
try:
    profiles = dconf_get("list")
except:
    profiles = []

for flavour, colours in palette.items():
    uuid = uuids[flavour]
    dconf_set(f":{uuid}/visible-name", f"Catppuccin {flavour.capitalize()}")
    dconf_set(f":{uuid}/background-color", colours["base"]["hex"])
    dconf_set(f":{uuid}/foreground-color", colours["text"]["hex"])
    dconf_set(f":{uuid}/highlight-colors-set", True)
    dconf_set(f":{uuid}/highlight-background-color", colours["base"]["hex"])
    dconf_set(f":{uuid}/highlight-foreground-color", colours["surface2"]["hex"])
    dconf_set(f":{uuid}/cursor-colors-set", True)
    dconf_set(f":{uuid}/cursor-background-color", colours["rosewater"]["hex"])
    dconf_set(f":{uuid}/cursor-foreground-color", colours["base"]["hex"])

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
    dconf_set(f":{uuid}/use-theme-colors", False)
    # get only the hex key from each entry in colors
    dconf_set(f":{uuid}/palette", [color["hex"] for color in colors])

    if uuid not in profiles:
        profiles.append(uuid)

dconf_set("list", profiles)
print("All profiles installed.")
