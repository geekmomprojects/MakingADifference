# Updates toy code written for version 1 of this library so it uses the
# version 2 names.
#
# Run this on your computer (not on the Pico), for example:
#
#     python tools/update_to_v2.py G:\code.py
#     python tools/update_to_v2.py my_toy.py another_toy.py
#
# Add --dry-run to see what would change without changing anything:
#
#     python tools/update_to_v2.py --dry-run G:\code.py
#
# Before changing a file, the script saves a copy of the original next to it
# (for example code.py.v1.bak). Every changed line is printed.
#
# Code that still uses the old names will work with version 2 anyway; it just
# prints a note for each old name. This script makes those notes go away.

import re
import sys

# (pattern to find, replacement). The patterns only match names used after a
# "." (like trigger.current_action), so your own variable names are not touched.
RENAMES = [
    (r"\.start_action\(",             ".start("),
    (r"\.stop_action\(",              ".stop("),
    (r"\.do_action\(",                ".update("),
    (r"\.current_action\b",           ".current_group"),
    (r"\.action_index\b",             ".group_index"),
    (r"\.set_random_action\(",        ".set_random_group("),
    (r"\.set_current_action\(",       ".set_current_group("),
    (r"\.get_current_action_data\(",  ".get_current_group_data("),
    (r"\bbutton_actions\s*=",         "action_groups="),
    (r"\bdef\s+action\(\s*self\s*\)", "def on_update(self)"),   # in your own Action child classes
]


def update_file(path, dry_run):
    with open(path, newline="") as f:
        original = f.read()

    line_ending = "\r\n" if "\r\n" in original else "\n"
    lines = original.split(line_ending)
    changed = 0

    for i, line in enumerate(lines):
        new_line = line
        for pattern, replacement in RENAMES:
            new_line = re.sub(pattern, replacement, new_line)
        if new_line != line:
            changed += 1
            print("  line", i + 1)
            print("    old:", line.strip())
            print("    new:", new_line.strip())
            lines[i] = new_line

    if changed == 0:
        print("  nothing to change")
        return

    if dry_run:
        print(" ", changed, "line(s) would change (dry run, file not changed)")
        return

    with open(path + ".v1.bak", "w", newline="") as f:
        f.write(original)
    with open(path, "w", newline="") as f:
        f.write(line_ending.join(lines))
    print(" ", changed, "line(s) changed. Original saved as", path + ".v1.bak")


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    files = [a for a in args if a != "--dry-run"]
    if not files:
        print("Usage: python update_to_v2.py [--dry-run] file.py [more files...]")
        sys.exit(1)
    for path in files:
        print(path)
        update_file(path, dry_run)


main()
