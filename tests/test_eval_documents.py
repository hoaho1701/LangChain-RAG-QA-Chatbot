import json
import os

from eval.build_index import DOCUMENTS


def test_every_document_of_the_dataset_has_a_file_named_after_it():
    with open("eval/dataset.json", encoding="utf-8") as f:
        docs = {case["doc"] for case in json.load(f)}

    assert docs == {os.path.splitext(name)[0] for name in DOCUMENTS}
