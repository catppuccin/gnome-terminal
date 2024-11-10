#!/usr/bin/env python3
import json
import argparse
from subprocess import check_output as run

arg_parser = argparse.ArgumentParser(
    prog="Catppuccin Theme - Gnome-Terminal Uninstallation",
    description="Uninstalls the Catppuccin theme for gnome-terminal",
)
args = arg_parser.parse_args()

gsettings_path_base = (
    "org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/"
)
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
        run(["gsettings", "get", gsettings_schema, key])
        .decode("utf-8")
        .replace("'", '"')
    )


# filter out non-Catppuccin profiles
try:
    profiles = gsettings_get("list")
except:
    profiles = []
other_profiles = []

for uuid in profiles:
    if uuid not in uuids.values():
        other_profiles.append(uuid)
        continue

    print(f"Removing {uuid}")

    run(["gsettings", "reset-recursively", f"{gsettings_path_base}:{uuid}/"])

# reset the profiles list
run(["gsettings", "set", f"{gsettings_schema}", "list", f"{other_profiles}"])

print("Catppuccin profiles uninstalled.")
