#!/usr/bin/env python3

from neo4j import GraphDatabase
import requests
from bs4 import BeautifulSoup

uri = 'neo4j://kb.virtualflybrain.org'
auth = ('neo4j', 'vfb')


def get_wlz_size(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')
        pre = soup.find('pre')
        if not pre:
            return -1
        for line in pre.get_text().split('\n'):
            if 'volume.wlz' in line and '../' not in line:
                parts = line.split()
                try:
                    return int(parts[-1])
                except Exception:
                    pass
        return -1
    except Exception:
        return -1


def main():
    with GraphDatabase.driver(uri, auth=auth) as driver:
        with driver.session() as session:
            res = session.run(
                """MATCH (n:Individual)-[r:in_register_with]->(tc:Template {short_form:'VFBc_00101567'})
                   RETURN distinct r.folder[0] as folder LIMIT 200"""
            )
            folders = [r['folder'] for r in res]

    print(f"Sampled {len(folders)} folders")
    sizes = []
    for url in folders:
        sizes.append(get_wlz_size(url))

    from collections import Counter
    cnt = Counter(sizes)
    for size, count in sorted(cnt.items())[:10]:
        print(size, count)
    print('...')
    print('Min size', min([s for s in sizes if s > 0]))
    print('Max size', max(sizes))


if __name__ == '__main__':
    main()
