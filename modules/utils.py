# modules/utils.py
import re

def split_text(text, max_chars=2000):
    """split text into sections under max_chars"""
    # check if response exceeds character limit
    if len(text) <= max_chars:
        return [text]
    
    sections = []
    remaining_text = text
    
    while remaining_text:
        if len(remaining_text) <= max_chars:
            sections.append(remaining_text)
            break
            
        # try to find natural breaking point (paragraph or sentence)
        # first look for paragraph breaks
        split_index = remaining_text[:max_chars].rfind('\n\n')
        
        # if no paragraph break, look for sentence break
        if split_index == -1 or split_index < max_chars * 0.5:
            # look for last sentence break
            for punct in ['. ', '! ', '? ']:
                last_punct = remaining_text[:max_chars].rfind(punct)
                if last_punct > 0 and (split_index == -1 or last_punct > split_index):
                    split_index = last_punct + 1  # include punctuation
            
        # if no good breaking point found, just split at max_chars
        if split_index == -1 or split_index < max_chars * 0.5:
            split_index = max_chars
        
        # add section and update remaining text
        sections.append(remaining_text[:split_index].strip())
        remaining_text = remaining_text[split_index:].strip()
        
    return sections

def is_url(text):
    """check if input is url and return boolean"""
    url_pattern = re.compile(
        r'^(https?:\/\/)?'          # optional http or https
        r'(www\.)?'                 # optional www
        r'([a-zA-Z0-9\-]+\.)+'      # domain name
        r'[a-zA-Z]{2,}'             # domain suffix
        r'(\/\S*)?$'                # optional trailing path
    )
    return bool(url_pattern.match(text))