import re
import pytest
from pathlib import Path

from backend.services.chunk import clean_markdown, ESCAPED, IMAGES, APPLE_FOOTER

FILES = sorted(Path(__file__).parent.glob("fixtures/*.md"))

@pytest.mark.skipif(not FILES, reason = "run seed.py first")
@pytest.mark.parametrize("path", FILES, ids = lambda p: p.stem)
def test_full_filing(path): 
    raw = path.read_text(encoding="utf-8")
    out = clean_markdown(raw)
    
    assert "<u>Table of Contents</u>" not in out
    assert "![" not in out
    assert not re.search(r"\\[^\w\s]", out)
    assert clean_markdown(out) == out                       # stable

    # what a correct cleaner should keep: raw minus images, minus escapes
    fair = ESCAPED.sub(r"\1", APPLE_FOOTER.sub("", IMAGES.sub("", raw))).replace("\xa0", " ")
    numbers = lambda s: set(re.findall(r"\d[\d,.]*\d", s))
    assert not numbers(fair) - numbers(out), "lost"
    assert not numbers(out) - numbers(fair), "gained (cells glued together)"