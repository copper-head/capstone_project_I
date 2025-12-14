from backend.constants import AI_CONFIG

from pathlib import Path
from google import genai
from google.genai import types
import os

PROMPT = r"""
You are a LaTeX transcription engine.

Task:
- I will provide multiple images (ordered pages) of notes.
- Produce ONE complete LaTeX document that compiles as-is.

Requirements:
- Output ONLY the LaTeX source (no markdown fences, no commentary).
- Use \documentclass{article} and include a minimal preamble:
  amsmath, amssymb, amsthm, geometry, hyperref.
- Preserve headings/sections as best you can.
- Use display math environments (equation/align) when appropriate.
- If something is unreadable, insert: \textbf{[illegible]}.
- DO NOT EVER PUT IMAGES IN THE LATEX.
"""

def guess_mime(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    raise ValueError(f"Unsupported image type: {ext}")

def generate_latex_from_images(image_files):

    """
    image_files: ordered iterable of file paths (str or Path)
                 ordering defines page order
    returns: LaTeX source (str)
    """

    # Prefer key from constants; fallback to env var for compatibility
    api_key = AI_CONFIG.get("API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing API key. Set AI_API_KEY in .env or GEMINI_API_KEY in environment.")

    client = genai.Client(api_key=api_key)

    parts = [types.Part(text=PROMPT)]

    for file in image_files:

        path = Path(file)
    
        if not path.exists():
            raise FileNotFoundError(path)

        parts.append(
            types.Part(
                inline_data=types.Blob(
                    mime_type=guess_mime(path),
                    data=path.read_bytes(),
                )
            )
        )

    resp = client.models.generate_content(
        model=AI_CONFIG["MODEL_NAME"],
        contents=[types.Content(role="user", parts=parts)],
        config=types.GenerateContentConfig(temperature=0.2),
    )

    return resp.text or ""