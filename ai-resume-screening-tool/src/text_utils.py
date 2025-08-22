import re
import string
from typing import List

import nltk
from nltk.corpus import stopwords

# Ensure NLTK data is available (user must run downloader once in README)
STOPWORDS = set(stopwords.words('english'))

def normalize_text(text: str) -> str:
    text = text or ""
    # Lowercase
    text = text.lower()
    # Replace emails, urls, phones with tokens
    text = re.sub(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", " _email_ ", text)
    text = re.sub(r"http[s]?://\S+", " _url_ ", text)
    text = re.sub(r"\+?\d[\d\-()\s]{6,}\d", " _phone_ ", text)
    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text: str) -> List[str]:
    # Simple whitespace tokenizer
    return [w for w in text.split() if w and w not in STOPWORDS]

def jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)
