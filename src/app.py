import os
import tempfile
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename

from .resume_screen import rank_resumes
from pathlib import Path

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AI Resume Screening Tool</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light p-4">

<div class="container">
  <h2 class="mb-4 text-center">🚀 AI Resume Screening Tool</h2>

  <form method="POST" enctype="multipart/form-data" class="card p-3 shadow-sm">
    <div class="mb-3">
      <label class="form-label fw-bold">Job Description (JD):</label>
      <input type="file" name="jd" class="form-control" required>
    </div>

    <div class="mb-3">
      <label class="form-label fw-bold">Resumes (Multiple):</label>
      <input type="file" name="resumes" multiple class="form-control" required>
    </div>

    <button type="submit" class="btn btn-primary">Rank Resumes</button>
  </form>

  {% if results %}
  <h4 class="mt-5">📊 Results</h4>
  <table class="table table-striped table-hover table-bordered mt-3">
    <thead class="table-dark">
      <tr>
        <th>#</th>
        <th>Filename</th>
        <th>Final Score</th>
        <th>Similarity</th>
        <th>Skills Match</th>
        <th>Matched Skills</th>
      </tr>
    </thead>
    <tbody>
      {% for r in results %}
      <tr>
        <td>{{ loop.index }}</td>
        <td>{{ r.resume_path }}</td>
        <td>{{ '%.4f'|format(r.final_score) }}</td>
        <td>{{ '%.4f'|format(r.similarity_score) }}</td>
        <td>{{ '%.4f'|format(r.skills_score) }}</td>
        <td>{{ ', '.join(r.skills_matched) }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% endif %}
</div>
</body>
</html>
"""

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    results = None
    if request.method == 'POST':
        with tempfile.TemporaryDirectory() as tmpdir:
            jd_file = request.files['jd']
            jd_path = os.path.join(tmpdir, secure_filename(jd_file.filename))
            jd_file.save(jd_path)

            resumes_dir = os.path.join(tmpdir, 'resumes')
            os.makedirs(resumes_dir, exist_ok=True)
            for f in request.files.getlist('resumes'):
                p = os.path.join(resumes_dir, secure_filename(f.filename))
                f.save(p)

            skills_yaml = str(Path(__file__).parent / 'skills.yaml')
            results = rank_resumes(jd_path, resumes_dir, skills_yaml)
    return render_template_string(TEMPLATE, results=results)
