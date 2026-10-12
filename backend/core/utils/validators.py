def clean_and_dedupe_strings(v: list[str]) -> list[str]:
    seen = set() 
    cleaned_list = []
    
    for item in v: 
        stripped = item.strip()
        
        if stripped and stripped not in seen: 
            seen.add(stripped)
            cleaned_list.append(stripped)
            
    return cleaned_list