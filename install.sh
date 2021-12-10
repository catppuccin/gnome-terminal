#!/bin/sh

# This is a simplified version of the install script used by dracula theme
# It does not work for for Gnome Terminal version < 3.8

profile="${1:-"Default"}"

dconfdir="/org/gnome/terminal/legacy/profiles:/"

get_uuid()
{
	name="$1"
	for uuid in $(dconf list "$dconfdir")
	do
		if [ "$(dconf read "$dconfdir$uuid"visible-name)" = "'$name'" ]
		then
			echo "$uuid"
		fi
	done

	echo ""
}

uuid="$(get_uuid "$profile")"
if [ -z "$uuid" ]
then
	echo "Profile: '$profile' does not exist -- ABORTING!"
	exit 1
fi

cat <<- EOF
Note that running this script will overwrite
the colors in the selected profile ("$profile").
There currently isn't a uninstall option.

Are you sure you want overwrite the selected profile ("$profile")?
("YES" to continue)
EOF

read confirmation
if [ "$(echo $confirmation | tr '[:lower:]' '[:upper:]')" != YES ]
then
   echo "ERROR: Confirmation failed -- ABORTING!"
   exit 1
fi
cat <<- EOF
-- Confirmation received --
--  Applying Catppuccin --
EOF

profile_path="$dconfdir$uuid"

# Make sure the profile is set to not use GTK theme colors
dconf write "$profile_path"use-theme-colors "false"

# Set foreground and background color
dconf write "$profile_path"foreground-color "'#D7DAE0'"
dconf write "$profile_path"background-color "'#1E1E29'"

# Set bold color to be same as foreground color
# (I'm not really sure where this color appears)
dconf write "$profile_path"bold-color-same-as-fg "true"

# Set cursor color
dconf write "$profile_path"cursor-colors-set "true"
dconf write "$profile_path"cursor-foreground-color "'#1E1E29'"
dconf write "$profile_path"cursor-background-color "'#B3E1A3'"

# Set highlight color (highlight colors are reverse
# of foreground and background by default)
dconf write "$profile_path"highlight-colors-set "false"

# Set the color palette
dconf write "$profile_path"palette "$(cat $PWD/palette)"

echo "Catppuccin successfully set!"
