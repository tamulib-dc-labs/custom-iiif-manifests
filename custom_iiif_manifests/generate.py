from iiif_prezi3 import Collection
from csv import DictReader
import requests
from pydantic import json

collection = Collection(
    id="https://tamulib-dc-labs.github.io/custom-iiif-manifests/collections/cole-text-only.json",
    label="Handwritten Materials from J.R. Cole",
    type="Collection",
)
with open("cole.csv", "r") as f:
    reader = DictReader(f)
    for row in reader:
        r = requests.get(row["Manifest"])
        json_doc = r.json()
        title = json_doc["label"]
        collection.make_manifest(
            id=row["Manifest"],
            type="Manifest",
            label=title
        )

json_string = collection.json(indent=4)

with open("collections/cole-text-only.json", "w") as f:
    f.write(json_string)
