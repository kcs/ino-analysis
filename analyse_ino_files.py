#!/usr/bin/env python3

import json

with open("ino_content.json", "r") as f:
    json_rows = [json.loads(line) for line in f]


includes = {}
functions = {}

repos = {}

for row in json_rows:
    for i in row['includes']:
        if i in includes:
            includes[i] += 1
        else:
            includes[i] = 1
    for k,v in row['functions'].items():
        if k in functions:
            functions[k] += v
        else:
            functions[k] = v
    if row['repo'] not in repos:
        repos[row['repo']] = [set(row['includes']), set(row['functions'].keys())]
    else:
        repos[row['repo']][0].update(row['includes'])
        repos[row['repo']][1].update(row['functions'].keys())    


with open("includes.lst", "w") as f:
    for k,v in sorted(includes.items(), key=lambda x: (-x[1], x[0])):
        f.write(f"{k}: {v}\n")

with open("functions.lst", "w") as f:
    for k,v in sorted(functions.items(), key=lambda x: (-x[1], x[0])):
        f.write(f"{k}: {v}\n")

repo_includes = {}
repo_functions = {}

for repo in repos.values():
    for i in repo[0]:
        if i in repo_includes:
            repo_includes[i] += 1
        else:
            repo_includes[i] = 1
    for f in repo[1]:
        if f in repo_functions:
            repo_functions[f] += 1
        else:
            repo_functions[f] = 1

with open("repo_includes.lst", "w") as f:
    for k,v in sorted(repo_includes.items(), key=lambda x: (-x[1], x[0])):
        f.write(f"{k}: {v}\n")

with open("repo_functions.lst", "w") as f:
    for k,v in sorted(repo_functions.items(), key=lambda x: (-x[1], x[0])):
        f.write(f"{k}: {v}\n")

print(f"Total repos: {len(repos)}")
print(f"Total files: {len(json_rows)}")
