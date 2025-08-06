#!/bin/bash

# Default values
t_warn="${T_WARN:-50}"
t_crit="${T_CRIT:-80}"
cpu_usage=-1
threads=1
decimals="${DECIMALS:-0}"
label="${LABEL:-}"
color_normal="#FFFFFF"
color_warn="#FFBBBB"
color_crit="#FF0000"
icon_color="${PRIMARY_COLOR}"
color="$color_normal"
spacer=""


# Get CPU usage from mpstat
mpstat_output=$(mpstat 1 1)
threads=$(echo "$mpstat_output" | awk '/[0-9]+ CPU/ {print $(NF-1) $NF}' | sed 's/[^0-9]*//g')
cpu_usage=$(echo "$mpstat_output" | awk -v t="$threads" '/^Average:/ {print int((100 - $NF)*t)}')

[[ -z $cpu_usage ]] && echo "Can't find CPU information" && exit 1

t_crit=$(bc -l <<< "$t_crit * $threads")
t_warn=$(bc -l <<< "$t_warn * $threads")

if [[ 10 -le $cpu_usage && $cpu_usage -lt 100 ]]; then
    spacer=" "
elif [[ 0 -le $cpu_usage && $cpu_usage -lt 10 ]]; then
    spacer="  "
fi


if [[ cpu_usage -ge t_crit ]]; then
    color="$color_crit"
	icon_color="$color_crit"
elif [[ cpu_usage -ge t_warn ]]; then
    color="$color_warn"
	icon_color="$color_warn"
fi

# Print short_text, full_text
printf "<span color=\"${color}\">%.${decimals}f%%${spacer}</span>\n" "$cpu_usage"

exit 0
