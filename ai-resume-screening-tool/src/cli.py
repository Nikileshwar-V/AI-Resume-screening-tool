import argparse
import csv
from pathlib import Path
from .resume_screen import rank_resumes

def main():
    parser = argparse.ArgumentParser(description='AI Resume Screening Tool (CLI)')
    parser.add_argument('--jd', required=True, help='Path to Job Description file (.txt/.pdf/.docx)')
    parser.add_argument('--resumes', required=True, help='Folder containing resumes')
    parser.add_argument('--out', default='results.csv', help='Output CSV path')
    parser.add_argument('--skills', default=str(Path(__file__).parent / 'skills.yaml'), help='Path to skills.yaml')
    args = parser.parse_args()

    results = rank_resumes(args.jd, args.resumes, args.skills)

    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['resume_path', 'similarity_score', 'skills_score', 'final_score', 'skills_matched'])
        for r in results:
            writer.writerow([r.resume_path, f'{r.similarity_score:.4f}', f'{r.skills_score:.4f}', f'{r.final_score:.4f}', ', '.join(r.skills_matched)])

    print(f'Wrote: {args.out}')
    for i, r in enumerate(results, 1):
        print(f"{i:2d}. {Path(r.resume_path).name:40s}  final={r.final_score:.4f}  sim={r.similarity_score:.4f}  skills={r.skills_score:.4f}")

if __name__ == '__main__':
    main()
