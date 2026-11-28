#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PRACTICE_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
REFERENCE_DIR="$PRACTICE_DIR/reference"
CC=\${CC:-cc}
TMP_DIR=$(mktemp -d "\${TMPDIR:-/tmp}/campus-practice-tests.XXXXXX")
trap 'rm -rf "$TMP_DIR"' EXIT HUP INT TERM

compile_and_run() {
    name=$1
    source=$2
    shift 2
    "$CC" -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 \
        "$@" "$REFERENCE_DIR/$source" -o "$TMP_DIR/$name"
    "$TMP_DIR/$name"
}

assert_contains() {
    output=$1
    expected=$2
    if ! printf '%s\n' "$output" | grep -F "$expected" >/dev/null; then
        printf 'Expected output fragment not found: %s\n' "$expected" >&2
        printf '%s\n' "$output" >&2
        exit 1
    fi
}

printf '%s\n' '[A] timetable baseline'
out=$(compile_and_run a_base topic_a_timetable.c)
assert_contains "$out" 'C1      08:00-09:40    A'
assert_contains "$out" 'C1 -> C2: gap=20 min, travel=25 min, shortfall=5 min [INSUFFICIENT]'
assert_contains "$out" 'C4 -> C5: gap=20 min, travel=25 min, shortfall=5 min [INSUFFICIENT]'
assert_contains "$out" 'Insufficient transitions: 2'

printf '%s\n' '[A] A-B movement time changed to 20 minutes'
out=$(compile_and_run a_ab20 topic_a_timetable.c -DAB_MOVE_MINUTES=20)
assert_contains "$out" 'Insufficient transitions: 0'

printf '%s\n' '[A] empty and single-course boundaries'
out=$(compile_and_run a_empty topic_a_timetable.c -DCOURSE_COUNT=0)
assert_contains "$out" 'No courses provided.'
out=$(compile_and_run a_single topic_a_timetable.c -DCOURSE_COUNT=1)
assert_contains "$out" 'Not enough courses to compare transitions.'

printf '%s\n' '[B] baseline BFS path'
out=$(compile_and_run b_base topic_b_bfs.c)
assert_contains "$out" 'Minimum-edge path from 0 to 5: 0 -> 1 -> 4 -> 5'
assert_contains "$out" 'Minimum edge count: 3'

printf '%s\n' '[B] road E3 closed'
out=$(compile_and_run b_close_e3 topic_b_bfs.c -DCLOSE_E3=1)
assert_contains "$out" 'Minimum-edge path from 0 to 5: 0 -> 2 -> 3 -> 5'
assert_contains "$out" 'Minimum edge count: 3'

printf '%s\n' '[B] isolated target and source-equals-target boundaries'
out=$(compile_and_run b_unreachable topic_b_bfs.c -DTARGET_VERTEX=6)
assert_contains "$out" 'No path from 0 to 6.'
out=$(compile_and_run b_same_vertex topic_b_bfs.c -DTARGET_VERTEX=0)
assert_contains "$out" 'Minimum edge count: 0'

printf '%s\n' '[C] FIFO baseline'
out=$(compile_and_run c_base topic_c_fifo.c)
assert_contains "$out" 'R2        1        2      3       5     2'
assert_contains "$out" 'R3        1        4      5       9     4'
assert_contains "$out" 'Average waiting time: 2.17 min'
assert_contains "$out" 'Maximum waiting time: 5 min'

printf '%s\n' '[C] R3 service time changed to 1 minute'
out=$(compile_and_run c_r3_one topic_c_fifo.c -DR3_SERVICE_MINUTES=1)
assert_contains "$out" 'R3        1        1      5       6     4'
assert_contains "$out" 'R4        4        1      6       7     2'
assert_contains "$out" 'Average waiting time: 1.67 min'
assert_contains "$out" 'Maximum waiting time: 4 min'

printf '%s\n' '[C] empty and single-request boundaries'
out=$(compile_and_run c_empty topic_c_fifo.c -DREQUEST_COUNT=0)
assert_contains "$out" 'No requests to simulate.'
out=$(compile_and_run c_single topic_c_fifo.c -DREQUEST_COUNT=1)
assert_contains "$out" 'R4        4        1      4       5     0'
assert_contains "$out" 'Average waiting time: 0.00 min'

printf '%s\n' 'All reference-program tests passed.'