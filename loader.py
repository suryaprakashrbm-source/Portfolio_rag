from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
import uuid

transformer=HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
    )



with open("./data/Portfolio_doc.txt",'r',encoding="latin-1") as file:
    context=file.read()

def dynamic_chunker(text, target_size=600, overlap=100):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    chunks = []
    current_chunk = []
    current_len = 0
    for line in lines:
        current_chunk.append(line)
        current_len += len(line) + 1
        if current_len >= target_size:
            # Add prefix so every chunk retains portfolio context
            chunk_text = f"[Suryaprakash B - Portfolio]\n" + "\n".join(current_chunk)
            chunks.append(chunk_text)
            
            # Keep overlap for context continuity
            while current_chunk and current_len > overlap:
                removed = current_chunk.pop(0)
                current_len -= len(removed) + 1
    if current_chunk:
        chunks.append(f"[Suryaprakash B - Portfolio]\n" + "\n".join(current_chunk))
    return chunks

chunks = dynamic_chunker(context)
emb_chunks=transformer.embed_documents(chunks)

client=chromadb.PersistentClient("C:/Users/krith/Desktop/surya/Projects/portfolio-rag/data/vectordb")
client.delete_collection("my_profile")
collection=client.get_or_create_collection("my_profile")

collection.add(
    ids=[str(uuid.uuid4()) for i in range(len(chunks))],
    documents=chunks,
    embeddings=emb_chunks,
    metadatas=[{"topic": "rag"} for _ in range(len(chunks))]
)
print(len(chunks))
print(len(emb_chunks))
print(len(emb_chunks[0]))