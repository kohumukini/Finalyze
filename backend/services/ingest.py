import os

from .chunk import chunk_doc


def load_documents(): 
    documents = []
    for filename in sorted(os.listdir("./docs")):
        if filename.endswith(".txt"): 
            filepath = os.path.join("./docs", filename)
            with open(filepath, "r", encoding = "utf-8") as f: 
                text = f.read()
            documents.append({
                "filename": filename, 
                "text": text
            })
            
    print(f"Loaded {len(documents)} document(s)")
    return documents

def load_chunks(): 
    docs = load_documents()
    
    chunked_docs = []
    
    for doc in docs: 
        chunked_docs.append({
            "filename": doc["filename"],
            "content": chunk_doc(doc["text"])
        })
    return chunked_docs

load_chunks()