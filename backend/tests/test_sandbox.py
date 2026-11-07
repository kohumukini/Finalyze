from backend.services.embed import embed_chunks

from scipy.spatial.distance import pdist, squareform
    
texts = [
    """
    **Gross Margin**

    |  | 2025 |  |  | 2024 |  |  | 2023 |  |  |
    | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
    | Net sales | $ | 269,912 |  | $ | 249,625 |  | $ | 237,710 |  |
    | Less merchandise costs | 239,886 |  |  | 222,358 |  |  | 212,586 |  |  |
    | Gross margin | $ | 30,026 |  | $ | 27,267 |  | $ | 25,124 |  |
    | Gross margin percentage | 11.12 |  | % | 10.92 |  | % | 10.57 |  | % |
    """, 
    """**Gross Margin**

    |  | 2025 | 2024 | 2023 |
    | --- | --- | --- | --- |
    | Net sales | $269,912 | $249,625 | $237,710 |
    | Less merchandise costs | 239,886 | 222,358 | 212,586 |
    | Gross margin | $30,026 | $27,267 | $25,124 |
    | Gross margin percentage | 11.12% | 10.92% | 10.57% |
    """, 
]

def test_embeds(): 
    embeddings = embed_chunks(texts)
    pairwise_distance = pdist(embeddings, metric="cosine")
    print(squareform(pairwise_distance))

test_embeds()