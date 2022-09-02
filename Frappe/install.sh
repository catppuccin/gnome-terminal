#!/usr/bin/env sh

LOG_INFO="$(date +"%H:%M:%S") \e[0;34mINFO\e[0m"
LOG_ERROR="$(date +"%H:%M:%S") \e[1;31mERROR\e[0m"
LOG_WARNING="$(date +"%H:%M:%S") \e[0;33mWARNING\e[0m"
LOG_SUCCESS="$(date +"%H:%M:%S") \e[0;32mSUCCESS\e[0m"

profile="$1"
dconfdir="/org/gnome/terminal/legacy/profiles:"

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

create_default_profile() {
    profile_id="$(uuidgen)"
    dconf write $dconfdir/default "'$profile_id'"
    dconf write $dconfdir/list "['$profile_id']"
    dconf write $dconfdir/:$profile_id/visible-name "'Default'"
}

get_uuid() {
    name="$1"
    for uuid in $(dconf list "$dconfdir/"); do
        if [ "$(dconf read "$dconfdir/$uuid"visible-name)" = "'$name'" ]; then
            echo "$uuid"
        fi
    done

    echo ""
}

alert "Checking profiles..."

uuid="$(get_uuid "$profile")"
if [ -z "$uuid" ] && [ -z "$(dconf list "$dconfdir/")" ]; then
    alert -w "No profile was found. Creating 'Default' profile..."
    create_default_profile
    profile="Default"
    uuid="$(get_uuid "$profile")"
elif [ -z "$uuid" ]; then
    alert -e "Profile '${profile}' does not exist"
    alert "Use one of the following profiles or create a new one:"
    for prf in $(dconf list "$dconfdir/"); do
        dconf read "$dconfdir/$prf"visible-name
    done
    exit 1
fi

alert -s "Profile found!"
alert "Are you sure you want to overwrite the selected profile (${profile})? (YES to continue)"

read confirmation
if [ "$(echo $confirmation | tr '[:lower:]' '[:upper:]')" != YES ]; then
    echo "Confirmation failed - ABORTING!"
    exit 1
fi

printf "\n"
alert -w "Proceeding..."
alert -w "Applying settings..."

profile_path="$dconfdir/$uuid"

# Make sure the profile is set to not use GTK theme colors
dconf write "$profile_path"use-theme-colors "false"

# Set foreground and background color
dconf write "$profile_path"foreground-color "'#D7DAE0'"
dconf write "$profile_path"background-color "'#303446'"

# Set bold color to be same as foreground color
# (I'm not really sure where this color appears)
dconf write "$profile_path"bold-color-same-as-fg "true"

# Set cursor color
dconf write "$profile_path"cursor-colors-set "true"
dconf write "$profile_path"cursor-foreground-color "'#303446'"
dconf write "$profile_path"cursor-background-color "'#f2d5cf'"

# Set highlight color (highlight colors are reverse
# of foreground and background by default)
dconf write "$profile_path"highlight-colors-set "false"

alert -w "Applying color palette..."

# Set the color palette
dconf write "$profile_path"palette "$(cat $PWD/palette)"

printf "\n"

alert -s "You are all set! Now, restart your terminal :)"
