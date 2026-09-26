from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

transformer = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

DB_PATH = Path(__file__).resolve().parent / "data" / "vectordb"

client = chromadb.PersistentClient(
    path=str(DB_PATH)
)

collection= client.get_or_create_collection("my_profile")


def get_relevant_context(query):

    query_embedding=[transformer.embed_query(query)]
    result =collection.query(
    query_embeddings=query_embedding,
    n_results=2
    )
    retrival=result["documents"][0]
    context="\n\n".join(retrival)
    return context
