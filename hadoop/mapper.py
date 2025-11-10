#!/usr/bin/env python3
import os
import sys

env = {k.lower(): v for k, v in os.environ.items()}
filename = env.get("mapreduce_map_input_file") or  env.get("map_input_file") or "unknown_file"
filename = os.path.normpath(filename)

for line in sys.stdin:
    line = line.strip()
    if line:
        print(f"{filename}\t1")