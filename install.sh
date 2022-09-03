#!/usr/bin/env bash

LOG_INFO="$(date +"%H:%M:%S") \e[0;34mINFO\e[0m"
LOG_ERROR="$(date +"%H:%M:%S") \e[1;31mERROR\e[0m"
LOG_WARNING="$(date +"%H:%M:%S") \e[0;33mWARNING\e[0m"
LOG_SUCCESS="$(date +"%H:%M:%S") \e[0;32mSUCCESS\e[0m"

dconfdir="/org/gnome/terminal/legacy/profiles:"

read -rp "Which flavour do you want to install? Select [latte|frappe|macchiato|mocha]: " flavour

palette=$(jq ".${flavour}" palette.json)

function getCol() {
    colour=$1
    echo "$palette" | jq ".${colour}.hex"
}

foreground=$(getCol 'text')
background=$(getCol 'base')
selection_bg=$(getCol 'surface2')
selection_fg=$(getCol 'text')
cursor_bg=$(getCol 'crust')
cursor_fg=$(getCol 'rosewater')
isLatte=$([ "$flavour" = 'latte' ])

col0=$($isLatte && getCol "subtext1" || getCol "surface1")
col1=$(getCol "red")
col2=$(getCol "green")
col3=$(getCol "yellow")
col4=$(getCol "blue")
col5=$(getCol "pink")
col6=$(getCol "teal")
col7=$($isLatte && getCol "surface2" || getCol "subtext1")
col8=$($isLatte && getCol "subtext0" || getCol "subtext2")
col9=$(getCol "red")
col10=$(getCol "green")
col11=$(getCol "yellow")
col12=$(getCol "blue")
col13=$(getCol "pink")
col14=$(getCol "teal")
col15=$($isLatte && getCol "surface1" || getCol "subtext0")

echo "$foreground $background $selection_bg $selection_fg $cursor_bg $cursor_fg"
palette="[$col0, $col1, $col2, $col3, $col4, $col5, $col6, $col7, $col8, $col9, $col10, $col11, $col12, $col13, $col14, $col15]"

before="$(dconf list $dconfdir/ | head -n -2 | sed -e "s/^/'/" | sed -e "s/$/',/" | tr '\n' ' ' | sed -e "s/, $//")"
echo $before

alert() {
    todo=$1
    str=$2
    case "$todo" in
    -e | --error)
        printf "${LOG_ERROR} %s\n" "${str}"
        ;;
    -w | --warning)
        printf "${LOG_WARNING} %s\n" "${str}"
        ;;
    -s | --success)
        printf "${LOG_SUCCESS} %s\n" "${str}"
        ;;
    *)
        printf "${LOG_INFO} %s\n" "${1}" # default is LOG_INFO
        ;;
    esac
}

id1="$(uuidgen)"
id2="$(uuidgen)"
id3="$(uuidgen)"
id4="$(uuidgen)"

before="$(dconf list $dconfdir/ | sed -e "s/^/'/" | sed -e "s/$/\',/" | tr '\n' ' ' | sed -e 's/, $//')"
dconf write $dconfdir/list "'[$before, $id1, $id2, $id3, $id4]'"
dconf write "$dconfdir/:${id1}/visible-name" "'Latte'"
dconf write "$dconfdir/:${id2}/visible-name" "'Frappe'"
dconf write "$dconfdir/:${id3}/visible-name" "'Macchiato'"
dconf write "$dconfdir/:${id4}/visible-name" "'Mocha'"

profile_path="$dconfdir/$uuid"

# Make sure the profile is set to not use GTK theme colors
dconf write "$profile_path"use-theme-colors "false"

# Set foreground and background color
dconf write "$profile_path"foreground-color "$foreground"
dconf write "$profile_path"background-color "$background"

# Set bold color to be same as foreground color
# (I'm not really sure where this color appears)
dconf write "$profile_path"bold-color-same-as-fg "true"

# Set cursor color
dconf write "$profile_path"cursor-colors-set "true"
dconf write "$profile_path"cursor-foreground-color "$cursor_fg"
dconf write "$profile_path"cursor-background-color "$cursor_bg"

# Set highlight color (highlight colors are reverse
# of foreground and background by default)
dconf write "$profile_path"highlight-colors-set "false"

alert -w "Applying color palette..."

# Set the color palette
dconf write "$profile_path"palette "$palette"

printf "\n"

alert -s "You are all set! Now, restart your terminal :)"
