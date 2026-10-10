import re
from ..core.config import MAX_CHUNK_SIZE, OVERLAP_SIZE


# Chunker
# Args - Text
# Return - List of text chunks with sentence-aware overlap

def _backtrack_to_word_boundary(text, start, min_start):
    while start > min_start and start < len(text) and not re.match(r"\s", text[start - 1]):
        start -= 1
    return start


def chunk_doc(text):
    chunks = []
    start = 0

    sentence_pattern = r'[.!?]["\']?(?=\s|$)'

    while start < len(text):
        if len(text) - start <= MAX_CHUNK_SIZE:
            chunks.append(text[start:].strip())
            break

        end = start + MAX_CHUNK_SIZE
        chunk = text[start:end]
        sentence_ends = list(re.finditer(sentence_pattern, chunk))

        if sentence_ends:
            split_index = start + sentence_ends[-1].end()
            overlap_start = start + sentence_ends[-2].end() if len(sentence_ends) >= 2 else split_index
            overlap_length = split_index - overlap_start

            if overlap_length > OVERLAP_SIZE:
                desired_start = split_index - OVERLAP_SIZE
                desired_start = max(desired_start, overlap_start)
                overlap_start = _backtrack_to_word_boundary(text, desired_start, overlap_start)

            chunks.append(text[start:split_index].strip())
            start = overlap_start
        else:
            chunks.append(text[start:end].strip())
            start = end

    return chunks

