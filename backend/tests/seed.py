import os
from pathlib import Path
from edgar import set_identity, set_local_storage_path, use_local_storage
from edgar import Company

IDENTITY_FIRST = os.getenv("IDENTITY_FIRST")
IDENTITY_LAST = os.getenv("IDENTITY_LAST")
IDENTITY_EMAIL = os.getenv("IDENTITY_EMAIL")

set_identity(f"{IDENTITY_FIRST} {IDENTITY_LAST} {IDENTITY_EMAIL}")

script_dir = Path(__file__).resolve().parent
download_dir = script_dir / "fixtures"
download_dir.mkdir(parents=True, exist_ok=True)

print(f"Target Directory: {download_dir}")

set_local_storage_path(str(download_dir))
use_local_storage(True)

tickers = ["AAPL", "COST", "TMUS"]

def seed_tenk(): 
    for ticker in tickers: 
        company = Company(ticker)
        tenk_filings = company.get_filings(form="10-K")
        recent_tenk_filings = tenk_filings.head(5)
        for filing in recent_tenk_filings: 
            filename = f"{filing.company}_{filing.form}_{filing.filing_date}.md"
            filename = filename.replace(" ", "_").replace("/", "-")
            
            file_path = download_dir / filename
            
            content = filing.markdown()
            with open(file_path, "w", encoding="UTF-8") as f: 
                f.write(content)
            print(f"Saved {filename} ({len(content)} characters)")
            
if __name__ == "__main__": 
    seed_tenk()