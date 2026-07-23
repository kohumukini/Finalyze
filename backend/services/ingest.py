import os


def load_documents(): 
    documents = []
    for filename in sorted(os.listdir("../../docs")):
        if filename.endswith(".txt"): 
            filepath = os.join("../../docs", filename)
            with open(filepath, "r", encoding = "utf-8") as f: 
                text = f.read()
            documents.append({
                "filename": filename, 
                "text": text
            })
            
    print(f"Loaded {len(documents)} document(s)")
    return documents

load_documents()

