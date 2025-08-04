"""
Recipe Importer Module
Supports importing recipes from URLs, free-form text, or PDFs.
"""

import re
from typing import Optional, Dict, List, Union
from recipe_scrapers import scrape_me  
from datetime import datetime


class RecipeImporter:
    def __init__(self):
        pass

    def import_from_url(self, url: str) -> Optional[Dict[str, Union[str, List[str]]]]:
        """
        Uses recipe-scrapers to extract structured data from a recipe URL.
        """
        try:
            scraper = scrape_me(url)
            return {
                "title": scraper.title(),
                "ingredients": scraper.ingredients(),
                "instructions": scraper.instructions().split("\n"),
                "total_time": scraper.total_time(),
                "yields": scraper.yields(),
                "source_url": url,
                "imported_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error scraping recipe: {e}")
            return None

    def import_from_text(self, text: str) -> Optional[Dict[str, Union[str, List[str]]]]:
        """
        Parses plain text recipes into structured form using basic heuristics.
        """
        try:
            lines = text.strip().splitlines()
            title = lines[0].strip()

            # Heuristics to find ingredients and instructions
            ingredients = []
            instructions = []
            mode = None

            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                if re.search(r"(?i)^ingredients", line):
                    mode = "ingredients"
                    continue
                elif re.search(r"(?i)^instructions|steps|method", line):
                    mode = "instructions"
                    continue
                elif mode == "ingredients":
                    ingredients.append(line)
                elif mode == "instructions":
                    instructions.append(line)

            return {
                "title": title,
                "ingredients": ingredients,
                "instructions": instructions,
                "source": "text_input",
                "imported_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error parsing text recipe: {e}")
            return None

    def import_from_pdf(self, pdf_path: str) -> str:
        """
        Placeholder: Extracts raw text from a PDF (can be improved with OCR or NLP).
        Requires `PyMuPDF` or `pdfplumber`.
        """
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            text = "\n".join([page.get_text() for page in doc])
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
