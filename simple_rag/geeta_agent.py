from dotenv import load_dotenv
import os

import chromadb
from google import genai
from google.genai import types

EMBEDDING_MODEL_NAME = "gemini-embedding-001"

retrieve_similar_geeta_verses_function = {
    "name": "retrieve_similar_geeta_verses",
    "description": "Retrieves 10 similar verses to `query` from a vector database containing geeta verses.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Query string to retrieve relevant geeta verses from vector database"
            },
        },
        "required": ["query"],
    },
}

SYSTEM_PROMPT = """You are a helpful agent. 
You may call a tool named `retrieve_similar_geeta_verses` whenever the user 
asks for teachings from the Bhagavad Geeta.

The tool `retrieve_similar_geeta_verses` needs a `query` string which you should provide.
This `query` string will be used to semantically search for related or similar verses.
Thus, ensure that you construct the `query` string in a way that gets you the information
needed to answer the user's query.

After receiving tool output, use it to answer the user's question.
Answer only in english and in less than 100 words.
"""

def retrieve_similar_geeta_verses(query, gemini_client, db_collection, top_k=10):
    """Retrieves `top_k` similar verses to `query` from `db_collection`."""

    query_emb = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL_NAME,
        contents=[query],
    )
    results = db_collection.query(
        query_embeddings=[emb.values for emb in query_emb.embeddings],
        n_results=top_k,
        include=["documents"]    
    )
    return results["documents"][0]

def call_llm(messages, gemini_client, tool_config):
    """Sends messages to LLM."""
    resp = gemini_client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=messages,
        config=tool_config,
    )
    return resp

def run_agent():
    """Run the agent."""
    load_dotenv()
    gemini_client = genai.Client()
    tools = types.Tool(function_declarations=[retrieve_similar_geeta_verses_function])
    tool_config = types.GenerateContentConfig(tools=[tools])

    db_client = chromadb.HttpClient(host="localhost", port=8000)
    collection = db_client.get_collection(
        name=os.getenv("CHROMADB_COLLECTION_NAME"),
    )

    messages = [
        types.Content(
            role="user", parts=[types.Part(text=SYSTEM_PROMPT)]
        )
    ]

    print("Hi, How can I help you?\n")
    while True:
        user_query = input("User: ")

        if user_query.lower() in {"exit", "quit", "bye"}:
            print("👋 Bye!")
            break

        messages.append(
            types.Content(
                role="user", parts=[types.Part(text=user_query)]
            )
        )

        llm_response = call_llm(messages, gemini_client, tool_config)

        if llm_response.candidates[0].content.parts[0].function_call:
            tool_call = llm_response.candidates[0].content.parts[0].function_call
            db_query_str = tool_call.args["query"]
            similar_verses = retrieve_similar_geeta_verses(
                db_query_str, gemini_client, collection
            )

            messages.append(
                types.Content(
                    role="model", parts=[types.Part(text=user_query)]
                )
            )
            function_response_part = types.Part.from_function_response(
                name=tool_call.name,
                response={"result": "\n".join(similar_verses)},
            )

            messages.append(
                types.Content(
                    role="user", parts=[function_response_part]
                )
            )

            llm_response = call_llm(messages, gemini_client, tool_config)
            messages.pop()

        print(f"LLM's response: {llm_response.text}")
        print("\n\n")
        messages.append(
            types.Content(
                role="model", parts=[types.Part(text=llm_response.text)]
            )
        )

if __name__ == "__main__":
    run_agent()

    





    



