#!/usr/bin/env python3

import requests
from google.cloud import bigquery
from datetime import datetime
import json

client = bigquery.Client()

query = """
    SELECT repo_name  as repo, ref, path
    FROM `bigquery-public-data.github_repos.files`
    WHERE RIGHT(path, 4) = '.ino'
"""

def get_ino_file(repo, ref, path):
    url = "https://raw.githubusercontent.com/" + repo + '/' + ref.split('/')[-1] + '/' + path
    print(f"{url}", end='')
    r = requests.get(url)
    if r.status_code != 200:
        print(f" returned {r.status_code}. Ignoring")
        return None
    print(" OK")
    return r.text

if __name__ == "__main__":
    print(f"Script started at {datetime.now()}")

    results = client.query(query)
    json_rows = []

    for row in results:
        json_rows.append(json.dumps(dict(row), ensure_ascii=False,indent=None))
    
    print(f"Total rows: {len(json_rows)}")
    with open("ino.json", "w") as f:
        f.write("\n".join(json_rows))

    print(f"Script ended at {datetime.now()}")
