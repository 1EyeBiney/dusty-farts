import json
import glob

for f in sorted(glob.glob("data/shownotes/*.json")):
    d = json.load(open(f, encoding="utf-8"))
    slug = f.split("/")[-1].replace(".json", "").replace("\\", "")
    print("===", slug, "===")
    for v in d["voices"]:
        print(" ", v)
