import os
import json
import time
from dotenv import load_dotenv

import chromadb
from google import genai

BATCH_SIZE = 10
EMBEDDING_MODEL_NAME = "gemini-embedding-001"

def main():
    load_dotenv()

    print("Connecting to Chroma")
    db_client = chromadb.HttpClient(host="localhost", port=8000)

    print("Connecting to embedding model")
    gemini_client = genai.Client()

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

        while True:
            try:
                batch_embeddings_result = gemini_client.models.embed_content(
                    model=EMBEDDING_MODEL_NAME,
                    contents=verses_text_batch,
                )
                embeddings.extend([emb.values for emb in batch_embeddings_result.embeddings])
                print(f"Embedded {len(embeddings)} verses")
                break
            except:
                print(f"Rate limited. Waiting 60 seconds...")
                time.sleep(60)  # for rate limiting

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
