import pytest

from backend.services.chunk import clean_markdown

def test_footer_line_removal_apple(): 
    result = clean_markdown("Apple Inc\. | 2024 Form 10\-K | 55")
    assert result == ""
    
def test_double_space_collapse(): 
    result = clean_markdown("Some content  between other content")
    assert result == "Some content between other content"
    
def test_unescaped_punctuation(): 
    result = clean_markdown(r"Someone \. something \. somewhere\-")
    assert result == "Someone . something . somewhere-"
    
def test_image_drop(): 
    result = clean_markdown("![aapl-20210925_g1.jpg](https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925_g1.jpg)")
    assert result == ""
