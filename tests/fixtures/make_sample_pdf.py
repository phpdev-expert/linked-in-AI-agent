"""Generate a sample LinkedIn-style PDF for tests. Run: python tests/fixtures/make_sample_pdf.py"""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

LINES = [
    "Jane Developer",
    "Senior Backend Engineer at Acme",
    "",
    "Summary",
    "Experienced engineer who builds reliable APIs.",
    "",
    "Experience",
    "Senior Backend Engineer at Acme",
    "Built services handling millions of requests.",
    "",
    "Education",
    "BSc Computer Science, State University",
    "",
    "Skills",
    "Python, FastAPI, PostgreSQL",
]


def main() -> None:
    out = Path(__file__).parent / "sample_profile.pdf"
    c = canvas.Canvas(str(out), pagesize=letter)
    y = 750
    for line in LINES:
        c.drawString(72, y, line)
        y -= 18
    c.save()
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
