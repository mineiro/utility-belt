#!/bin/bash

set -euo pipefail

if [ "$#" -ne 2 ]; then
	echo "Usage: $0 <package-lock.json> <output-dir>" >&2
	exit 1
fi

lockfile=$1
output_dir=$2

command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm is required" >&2; exit 1; }

[ -f "$lockfile" ] || { echo "Lockfile not found: $lockfile" >&2; exit 1; }

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

rm -rf "$output_dir"
mkdir -p "$output_dir"
mkdir -p "$tmpdir/home"

export HOME="$tmpdir/home"
export npm_config_cache="$output_dir"
export npm_config_audit=false
export npm_config_fund=false
export npm_config_update_notifier=false

jq -r '.. | objects | .resolved? // empty' "$lockfile" \
	| sed '/^$/d' \
	| sort -u \
	| while IFS= read -r url; do
		case "$url" in
			http://*|https://*)
				npm cache add "$url" >/dev/null
				;;
		esac
	done
