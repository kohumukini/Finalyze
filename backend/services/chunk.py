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

BLOCK_SPLIT = re.compile(r"\n\s*\n")
APPLE_FOOTER = re.compile(r"Apple Inc\\?\. \| \d{4} Form 10\\?-K \| \d+")
IMAGES = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
TOC = re.compile(r"<u>Table of Contents</u>")
HEADER = re.compile(r"#{1,6}[ \t]+(.*)")
REAL_HEADER = re.compile(r"(PART [IXV]+|Item \d+[A-C]?)\b")
CONTINUE = re.compile(r"[ a-z,.;:)\]®™”’\\]") # To denote that the sentence hasn't ended
ESCAPED = re.compile(r"\\([^\w\s])") # For the escaped characters 
BULLET = re.compile(r"(\*\*)?\s*([■•])\s*(?(1)\*\*)\s*") # glyph; closing ** only if it was opened
BULLET_GLYPHS = {
    "■": "- ",
    "•": "    - "
}

def drop_noise(blocks: list[str]) -> list[str]: 
    valid_blocks = []
    for i, block in enumerate(blocks): 
        text = block.strip()
        previous = blocks[i - 1].strip() if i else ""
        nxt = blocks[i + 1].strip() if i + 1 < len(blocks) else ""
        
        # If our text is a footer or an image, skip it
        if TOC.fullmatch(text) or IMAGES.fullmatch(text) or APPLE_FOOTER.fullmatch(text): 
            continue
        if re.fullmatch(r"\d{1,3}$", text) and TOC.fullmatch(nxt) and previous.endswith("."): 
            continue
        
        valid_blocks.append(block)
    return valid_blocks

def _is_open(text: str) -> bool: 
    return text.endswith((" ", "“")) 

def fix_lists(blocks: list[str]) -> list[str]:
    valid_blocks = []
    skip = False
    for i, block in enumerate(blocks):
        if skip: # already merged into the previous bullet
            skip = False
            continue
        text = block.strip()
        nxt = blocks[i + 1].strip() if i + 1 < len(blocks) else ""

        bullet = BULLET.match(text)
        if not bullet:
            valid_blocks.append(block)
            continue

        label = text[bullet.end():]
        if not label: # bare glyph: its label is the next block
            match = HEADER.fullmatch(nxt)
            label = f"**{match.group(1).strip()}**" if match else nxt
            skip = True

        valid_blocks.append(BULLET_GLYPHS[bullet.group(2)] + label)

    return valid_blocks

def fix_tables(blocks: list[str]) -> list[str]: 
    out = []
    
    for block in blocks: 
        if not block.startswith("|"): 
            out.append(block)
            continue
        
        rows = [[cell.strip() for cell in line.split("|")[1:-1]] for line in block.splitlines()]
        header = rows[0]
        
        if header[0]: 
            out.append(block)
            continue
        
        starts = [0] + [i for i in range(1, len(header)) if header[i]]
        ends = starts[1:] + [len(header)]
        groups = list(zip(starts, ends))
        
        new_lines = []
        for row in rows: 
            if all(cell == "---" for cell in row): 
                new_row = ["---"] * len(groups)
            else: 
                new_row = ["".join(row[start:end]) for start,end in groups]
            
            new_lines.append("| " + " | ".join(new_row) + " |")
        out.append("\n".join(new_lines))
        
    return out

def demote_headers(blocks: list[str]) -> list[str]: 
    kept = []
    for i, block in enumerate(blocks): 
        m = HEADER.fullmatch(block)
        if not m: 
            kept.append(block)
            continue
        text = m.group(1).strip()
        previous = blocks[i - 1] if i else ""
        nxt = blocks[i + 1] if i + 1 < len(blocks) else ""
        
        if REAL_HEADER.match(text) and not _is_open(previous) and not CONTINUE.match(nxt): 
            kept.append(block)
        elif _is_open(previous): 
            kept.append(f"**{text}**" + (" " if nxt[:1].isalnum() else ""))
        else: 
            kept.append(text)
    return kept

def join_blocks(blocks: list[str]) -> list[str]: 
    out = []
    for block in blocks: 
        previous = out[-1] if out else ""
        is_plain = previous and not previous.startswith(("#", "|"))
        is_item = block.lstrip().startswith("- ")
        if is_plain and not is_item and (_is_open(previous) or _is_open(block) or CONTINUE.match(block)): 
            glue = "" if previous.endswith((" ", "“")) or CONTINUE.match(block) else " "
            out[-1] = previous + glue + block
        else: 
            out.append(block)
    return out

def clean_markdown(text: str) -> str:
    blocks = re.split(BLOCK_SPLIT, text.strip("\n"))
    blocks = join_blocks(demote_headers(fix_tables(fix_lists(drop_noise(blocks)))))
    text = blocks[0] if blocks else ""
    for previous, block in zip(blocks, blocks[1:]):
        tight = previous.lstrip().startswith("- ") and block.lstrip().startswith("- ")
        text += ("\n" if tight else "\n\n") + block
    text = ESCAPED.sub(r"\1", text).replace("\xa0", " ")
    text = re.sub(r"(?<=\w) ' (?=s\b)", "'", text)
    return re.sub(r"(?<=[^\s|]) {2,}", " ", text).strip()