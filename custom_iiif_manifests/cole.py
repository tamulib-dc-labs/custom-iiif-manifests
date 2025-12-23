from iiif_prezi3 import Manifest, config, KeyValueString, Canvas, AnnotationPage, AnnotationPageRefExtended, AnnotationPageRef
import requests
from pydantic import json


class FromthePageCollection:
    def __init__(self, collection):
        self.collection = collection
        self.all_details = self.get()
        self.manifests = self.find()

    def get(self):
        response = requests.get(self.collection)
        return response.json()

    def find(self):
        all = []
        for manifest in self.all_details.get('manifests', []):
            all.append(
                {
                    "ftp": manifest['@id'],
                    "original": manifest['metadata'][0]['value'],
                }
            )
        return all

class ColeManifest:
    def __init__(self, item):
        self.item = item
        self.original_manifest = item.get('original')
        self.item_id = self.original_manifest.split('/')[-1]
        self.base = f"https://tamulib-dc-labs.github.io/custom-iiif-manifests/manifests/cole-htr/{self.original_manifest.split('/')[-1]}"
        self.ftp = self.get_data(item.get('ftp'))

    @staticmethod
    def get_data(data):
        r = requests.get(data)
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception(f"Error Cole Manifest: {data}")

    def create_manifest(self):
        metadata = self.get_metadata()
        manifest = Manifest(
            id=f"{self.base}.json",
            label=self.ftp.get("label"),
            metadata=metadata,
        )
        manifest = self.make_canvases(manifest)
        return manifest

    def get_metadata(self):
        all_metadata = []
        for item in self.ftp.get("metadata", []):
            all_metadata.append(
                KeyValueString(
                    label=item["label"],
                    value=item["value"],
                )
            )
        return all_metadata

    def make_canvases(self, manifest):
        i = 0
        for item in self.ftp['sequences'][0]['canvases']:
            canvas = manifest.make_canvas_from_iiif(
                id=item["@id"],
                url=item['images'][0]['@id'],
                anno_page_id=f"{self.base}/canvas/{i}/anno-page/{i}",
                anno_id=f"{self.base}/canvas/{i}/anno-page/{i}/annotation/{i}",
            )
            if 'otherContent'  in item:
                ref_extended = AnnotationPageRefExtended(
                    id=item['otherContent'][0]['@id'],
                    label="Transcription",
                    type="AnnotationPage",
                )
                canvas.annotations = [AnnotationPageRef(__root__=ref_extended)]
            i+=1
        return manifest



if __name__ == "__main__":
    collection = "https://fromthepage.com/iiif/collection/handwritten-materials-from-j-r-cole"
    ftp_collection = FromthePageCollection(collection).find()
    for item in ftp_collection:
        manifest = ColeManifest(item)
        manifest_data = manifest.create_manifest()
        manifest_json = manifest_data.json(indent=4)
        with open(f"manifests/cole-htr/{manifest.item_id}.json", "w") as f:
            f.write(manifest_json)
