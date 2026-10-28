import pytest

from ..services.chunk import chunk_finance_docs

def test_footer_line_removal_apple(): 
    result = chunk_finance_docs("Apple Inc\. | 2024 Form 10\-K | 55")
    assert result == ""
    
def test_footer_line_removal_costco(): 
    result = chunk_finance_docs("27")
    assert result == ""
    
def test_footer_line_removal_tmobile(): 
    result = chunk_finance_docs("30")
    assert result == ""
    
def test_copyright_merge(): 
    result = chunk_finance_docs("Some content \n®")
    assert result == "Some content®"
    
def test_double_space_collapse(): 
    result = chunk_finance_docs("Some content  between other content")
    assert result == "Some content between other content"
    
def test_unescaped_punctuation(): 
    result = chunk_finance_docs(r"Someone \. something \. somewhere\-")
    assert result == "Someone . something . somewhere-"
    
def test_image_drop(): 
    result = chunk_finance_docs("![aapl-20210925_g1.jpg](https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925_g1.jpg)")
    assert result == ""
    
def test_split_heading(): 
    result = chunk_finance_docs("Find this in \n ### Item 8 \n\n of this report\\.")
    assert result == "Find this in Item 8 of this report."
    
