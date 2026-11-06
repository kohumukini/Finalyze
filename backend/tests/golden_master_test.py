import pytest

from pathlib import Path

from backend.services.chunk import clean_markdown

CASES_DIR = Path(__file__).resolve().parent / "cases"

input_files = sorted(CASES_DIR.glob("*.in.md"))

assert input_files, f"No .in.md cases found in {CASES_DIR}"


@pytest.mark.parametrize("input_path", input_files, ids=lambda p: p.name.removesuffix(".in.md"))
def test_markdown_golden_master(input_path: Path):
    output_path = input_path.with_name(input_path.name.replace(".in.md", ".out.md"))

    actual = clean_markdown(input_path.read_text(encoding="utf-8"))
    expected = output_path.read_text(encoding="utf-8")

    assert actual.strip() == expected.strip()
