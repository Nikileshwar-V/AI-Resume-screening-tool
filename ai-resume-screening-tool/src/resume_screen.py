import os
import io
from typing import List, Dict, Tuple
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import yaml
import numpy as np

from .text_utils import normalize_text, tokenize

# Weights (tune as needed)
SIMILARITY_WEIGHT = 0.7
SKILLS_WEIGHT     = 0.3

SUPPORTED_EXTS = {'.txt', '.pdf', '.docx'}

def load_text_from_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == '.txt':
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif ext == '.pdf':
        from pdfminer.high_level import extract_text
        return extract_text(path)
    elif ext == '.docx':
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def load_skills(skills_yaml_path: str) -> Dict[str, List[str]]:
    with open(skills_yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    # lower-case everything for robust matching
    for k, v in data.items():
        data[k] = [s.lower() for s in v]
    return data

def find_files(folder: str) -> List[str]:
    files = []
    for root, _, names in os.walk(folder):
        for n in names:
            if os.path.splitext(n)[1].lower() in SUPPORTED_EXTS:
                files.append(os.path.join(root, n))
    return sorted(files)

def compute_similarity(jd_text: str, resume_texts: List[str]) -> np.ndarray:
    corpus = [jd_text] + resume_texts
    try:
        vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1, max_df=1.0)
        X = vectorizer.fit_transform(corpus)
        sims = cosine_similarity(X[0:1], X[1:]).flatten()
    except ValueError:
        # fallback if corpus is too small
        vectorizer = TfidfVectorizer(ngram_range=(1,1))
        X = vectorizer.fit_transform(corpus)
        sims = cosine_similarity(X[0:1], X[1:]).flatten()
    return sims

def skills_from_text(text: str, skills_map: Dict[str, List[str]]) -> Tuple[List[str], float]:
    text_l = text.lower()
    present = []
    for category, skills in skills_map.items():
        for s in skills:
            # exact token containment (rough but effective)
            if f" {s} " in f" {text_l} ":
                present.append(s)
    present = sorted(set(present))
    # Simple skill score: sqrt of coverage ratio to reduce bias
    total_unique = len(set(sum(skills_map.values(), [])))
    score = (len(set(present)) / max(total_unique, 1)) ** 0.5
    return present, float(score)

from dataclasses import dataclass
@dataclass
class ResumeResult:
    resume_path: str
    similarity_score: float
    skills_matched: list
    skills_score: float
    final_score: float

def rank_resumes(jd_path: str, resumes_folder: str, skills_yaml_path: str):
    # Load JD
    jd_raw = load_text_from_file(jd_path)
    jd = normalize_text(jd_raw)

    # Load resumes
    files = find_files(resumes_folder)
    texts = [normalize_text(load_text_from_file(p)) for p in files]

    # Similarity
    sims = compute_similarity(jd, texts)

    # Skills
    skills_map = load_skills(skills_yaml_path)
    skill_hits, skill_scores = [], []
    for t in texts:
        present, score = skills_from_text(t, skills_map)
        skill_hits.append(present)
        skill_scores.append(score)

    # Final score
    results = []
    for i, path in enumerate(files):
        sim = float(sims[i])
        ss  = float(skill_scores[i])
        final = SIMILARITY_WEIGHT * sim + SKILLS_WEIGHT * ss
        results.append(ResumeResult(
            resume_path=path,
            similarity_score=sim,
            skills_matched=skill_hits[i],
            skills_score=ss,
            final_score=final
        ))

    results.sort(key=lambda r: r.final_score, reverse=True)
    return results
