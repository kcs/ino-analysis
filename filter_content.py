#!/usr/bin/env python3

import json
import sys

rows = []
repos = set()
dupes = 0

with open("ino_content.json", "r") as f:
    for line in f:
        if line:
            try:
                row = json.loads(line.strip('\0'))
            except:
                print("JSON error")
                print(line)
                c = line[0]
                print(ord(c))
                sys.exit(1)
            s = (row['repo'],row['ref'],row['path'])
            if s in repos:
                dupes += 1
            else:
                repos.add(s)
                with open("ino_content2.json", "a") as f:
                    f.write(json.dumps(row, ensure_ascii=False, indent=None) + "\n")

print(f"{dupes} duplicates found")
