#!/usr/bin/env python3
import sys

current_file = None
current_count = 0

for line in sys.stdin:
    file, count = line.strip().split("\t", 1)
    try:
        count = int(count)
    except ValueError:
        continue

    if current_file == file:
        current_count += count
    else:
        if current_file:
            print(f"\"{current_file}\": {current_count}")
        current_file = file
        current_count = count

# last file
if current_file is not None:
    print(f"\"{current_file}\": {current_count}")