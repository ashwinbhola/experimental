from dotenv import load_dotenv
import os

import chromadb
from sentence_transformers import SentenceTransformer
from google import genai

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

PROMPT_TEMPLATE = """Use the context provided to answer 
the user's question below. Use only the following 
pieces of context to answer the question. Don't make up any new information:

context: {context}

question: {query}

answer: """

def retrieve_similar_documents(query, emb_model, db_collection, top_k=10):
    """Retrieves `top_k` similar docs to query from db_collection."""

    query_emb = emb_model.encode([query])
    results = db_collection.query(
        query_embeddings=query_emb,
        n_results=top_k,
        include=["documents"]    
    )
    return results["documents"][0]


def create_prompt(query, similar_documents):
    """Returns a prompt with user query augmented with `similar_documents`."""
    context = "\n".join(similar_documents)
    prompt = PROMPT_TEMPLATE.format(context=context, query=query)
    return prompt


def generate_response(query, emb_model, db_collection, llm_client):
    """Generates a response from the LLM for the `query`."""

    similar_docs = retrieve_similar_documents(query, emb_model, db_collection)
    prompt = create_prompt(query, similar_docs)

    response = llm_client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=prompt
    )
    return response.text

def run_bot():
    load_dotenv()
    llm_client = genai.Client()
    emb_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    db_client = chromadb.HttpClient(host="localhost", port=8000)
    collection = db_client.get_collection(
        name=os.getenv("CHROMADB_COLLECTION_NAME"),
    )

    while True:
        input_query = input('Ask me a question: ')

        if input_query.lower() in {"exit", "quit"}:
            print("👋 Bye!")
            break

        resp = generate_response(input_query, emb_model, collection, llm_client)
        print(f"LLM's response: {resp}")
        print("\n\n")

if __name__ == "__main__":
    run_bot()