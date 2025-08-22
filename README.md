# AI Resume Screening Tool

A lightweight, ATS-aware resume ranking tool that scores and ranks resumes against a Job Description (JD) using TF‑IDF cosine similarity + skills matching. 
Includes a **CLI** and a minimal **Flask web app**.

---

## Features
- Parse **.pdf**, **.docx**, and **.txt** resumes
- Clean & normalize text; remove boilerplate
- Compute **TF-IDF + cosine similarity** against JD
- **Skills match boost** (weighted by your skills list in `skills.yaml`)
- Output **ranked CSV** with scores and matched skills
- Minimal **Flask UI** for quick uploads and rankings

---

## Quickstart

```bash
# 1) Create a venv (recommended)
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

# 2) Install requirements
pip install -r requirements.txt

# 3) Download NLTK data (once)
python -m nltk.downloader punkt stopwords

# 4) CLI usage
python -m src.cli --jd data/samples/jd.txt --resumes data/samples/resumes --out results.csv

# 5) Run Flask app (optional)
export FLASK_APP=src.app:app         # Windows (PowerShell): $env:FLASK_APP="src.app:app"
flask run --reload --port 5000
```

Then open http://127.0.0.1:5000/ in your browser.

---

## Project Structure

```
ai-resume-screening-tool/
├─ data/
│  └─ samples/
│     ├─ jd.txt
│     └─ resumes/
│        ├─ sample_resume_1.txt
│        └─ sample_resume_2.txt
├─ src/
│  ├─ cli.py
│  ├─ app.py
│  ├─ resume_screen.py
│  ├─ text_utils.py
│  └─ skills.yaml
├─ requirements.txt
└─ README.md
```

---

## Output

The CLI writes a CSV with:
- `resume_path`
- `similarity_score` (0–1)
- `skills_matched` (comma-separated)
- `skills_score` (0–1)
- `final_score` (0–1) = 0.7 * similarity + 0.3 * skills_score (configurable)

---

## Configuration (optional)

You can adjust weights by editing `src/resume_screen.py` constants:
```python
SIMILARITY_WEIGHT = 0.7
SKILLS_WEIGHT     = 0.3
```

You can also edit `src/skills.yaml` to add/remove skills.

---

## Notes
- This tool is **evaluation support** only; final decisions should involve human review.
- For best results, use clear text resumes (ATS-friendly) and a focused JD.
