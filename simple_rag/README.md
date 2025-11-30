Python version needed: 3.11.9

Steps the execute the code:
1. Install the requirements: `pip install -r requirements.txt`
2. Run a chroma server: `chroma run --path ./vector_db`
3. Create a `.env` file containing the following environment variables: `CHROMADB_COLLECTION_NAME`, `GEMINI_API_KEY`
4. First index the documents: `python indexing.py` if you want to use a sentence transformer embedding model locally or `python indexing_gemini.py`if you want to use an embedding model from google AI studio
5. Run the chat app: `python run_llm.py` if you embedded the documents using the sentence transformer model in step 4 or `python run_llm_gemini.py`if you used an embedding model from google in step 4