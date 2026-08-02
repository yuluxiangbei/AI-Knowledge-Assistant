from pypdf import PdfReader
from pathlib import Path

def parse_document(file_path) -> str:
  p = Path(file_path)
  extension: str = p.suffix.lower()
  text: str = ""
  if extension == ".pdf":
    reader = PdfReader(p)
    for page in reader.pages:
      text += (page.extract_text() or "")+"\n"
  elif extension in [".txt",".md"]:
    text += p.read_text(encoding="utf-8",errors="ignore")
  return text
  