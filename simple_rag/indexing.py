import os
import json
from dotenv import load_dotenv

import chromadb
from sentence_transformers import SentenceTransformer

BATCH_SIZE = 10
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def main():
    load_dotenv()

    print("Connecting to Chroma")
    db_client = chromadb.HttpClient(host="localhost", port=8000)

    print(f"Loading {EMBEDDING_MODEL_NAME} model")
    emb_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print("Reading Geeta verses")
    with open("geeta/commentary.json", "rb") as fhandle:
        verses = json.load(fhandle)
    
    verses = [verse for verse in verses if verse["author_id"] == 2]
    verses_text = [verse["description"] for verse in verses]
    print(f"Number of verses: {len(verses)}")
    
    print("Embedding Geeta verses")
    embeddings = []
    for b_idx in range(0, len(verses), BATCH_SIZE):
        verses_text_batch = verses_text[b_idx: b_idx+BATCH_SIZE]

        batch_embeddings = emb_model.encode(verses_text_batch)
        embeddings.extend(batch_embeddings)
        print(f"Embedded {len(embeddings)} verses")

    print("Setting up document collection")
    collection = db_client.get_or_create_collection(
        name=os.getenv("CHROMADB_COLLECTION_NAME"),
    )

    print("Adding each verse as a chunk to Chroma")
    collection.add(
        ids=[f"verse_{verse['verse_id']}" for verse in verses],
        documents=verses_text,
        embeddings=embeddings,
    )

    print("All verses succesfully uploaded to Chroma")
    

if __name__ == "__main__":
    main()