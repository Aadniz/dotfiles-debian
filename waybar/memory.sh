#!/usr/bin/env sh
# Copyright (C) 2014 Julien Bonjean <julien@bonjean.info>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

TYPE="${BLOCK_INSTANCE:-mem}"
PERCENT="${PERCENT:-true}"

LABEL="${LABEL:-}"
ICON_COLOR="${PRIMARY_COLOR}"
HIGH_COLOR="#FF0000"
MED_COLOR="${SECONDARY_COLOR}"
DEFAULT_COLOR="${FOREGROUND_COLOR}"

awk -v type=$TYPE -v high_color=$HIGH_COLOR -v med_color=$MED_COLOR -v default_color=$DEFAULT_COLOR -v icon_color=$ICON_COLOR -v label=$LABEL -v percent=$PERCENT '
/^MemTotal:/ {
	mem_total=$2
}
/^MemFree:/ {
	mem_free=$2
}
/^Buffers:/ {
	mem_free+=$2
}
/^Cached:/ {
	mem_free+=$2
}
/^SwapTotal:/ {
	swap_total=$2
}
/^SwapFree:/ {
	swap_free=$2
}
END {
	color=default_color
	if (type == "swap") {
		free=swap_free/1024/1024
		used=(swap_total-swap_free)/1024/1024
		total=swap_total/1024/1024
	} else {
		free=mem_free/1024/1024
		used=(mem_total-mem_free)/1024/1024
		total=mem_total/1024/1024
	}

	pct=0
	if (total > 0) {
		pct=used/total*100
	}

	if (pct > 90) {
        color=high_color
		icon_color=high_color
    } else if (pct > 70) {
        color=med_color
		icon_color=med_color
    }

	# full text
	if (percent == "true" ) {
		#printf("%.1fG/%.1fG (%.f%%)\n", used, total, pct)
        #printf("%.1fG/%.1fG\n", used, total)
        printf("%.1fG\n", used)
	} else {
		#printf("%.1fG/%.1fG\n", used, total)
	}
	# short text
	#printf("%.f%%\n", pct)

	# color
	#print(color)
}
' /proc/meminfo
