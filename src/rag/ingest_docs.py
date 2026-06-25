import os
from rag.vector_store import build_index
# from src.rag.vector_store import build_index

def load_documents():

    docs = []

    folder = "data/career_doc"

    for file in os.listdir(folder):

        with open(os.path.join(folder, file)) as f:
            docs.append(f.read())

    return docs


def ingest():

    docs = load_documents()

    build_index(docs)

    print("Career knowledge indexed")