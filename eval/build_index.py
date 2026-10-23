# eval/build_index.py
"""CLI: build the index that eval/dataset.json expects, in a folder of its own (never in the index of the app).

Put the four documents of the evaluation set in eval/documents/ (the evaluation section of the README says which; the
folder is not tracked by git) and run:
    python -m eval.build_index [--docs-dir eval/documents] [--db data/eval_index]
    VECTOR_DB_PATH=data/eval_index python -m eval.evaluate      # then evaluate against it
"""

import argparse
import os

# Must be set before any ML library is imported.
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = str(min(4, os.cpu_count() or 1))

# One file per `doc` value of eval/dataset.json, named after it
DOCUMENTS = [
    "hands-on-llms.pdf",
    "ml-co-ban.pdf",
    "photosynthesis-wikipedia.txt",
    "bien-doi-khi-hau-wikipedia.txt",
]


def main():
    parser = argparse.ArgumentParser(description="Build the index used by the evaluation set.")
    parser.add_argument("--docs-dir", default="eval/documents", help="Folder with the four documents.")
    parser.add_argument("--db", default="data/eval_index", help="Folder to create the index in (must not exist yet).")
    args = parser.parse_args()

    paths = [os.path.join(args.docs_dir, name) for name in DOCUMENTS]
    missing = [p for p in paths if not os.path.isfile(p)]
    if missing:
        raise SystemExit(
            "Missing documents (the evaluation section of the README says where to get them):\n" + "\n".join(missing)
        )
    # The index of the app must never be rebuilt or mixed with the evaluation documents by accident
    app_indexes = {os.path.realpath("data/vector_db"), os.path.realpath("vector_db")}
    if os.path.realpath(args.db) in app_indexes or (os.path.isdir(args.db) and os.listdir(args.db)):
        raise SystemExit(f"{args.db} already exists or is the index of the app. Choose a new folder with --db.")

    os.environ["VECTOR_DB_PATH"] = args.db  # src.config reads it when it is imported
    from src.rag_pipeline import RAGPipeline

    pipeline = RAGPipeline()
    for path in paths:
        splits = pipeline.load_and_split_file(path)
        pipeline.embed_and_store_documents(splits)
        print(f"Indexed {os.path.basename(path)}: {len(splits)} chunks")
    print(f"Done: {pipeline.vector_store._collection.count()} chunks in {args.db}")


if __name__ == "__main__":
    main()
