import io
import pandas as pd
from typing import List, Dict, Any, Tuple


class ExcelParserService:
    """
    Service responsible for parsing, validating, and normalizing participant Excel/CSV data.
    """

    @staticmethod
    def format_name_casing(raw_name: str) -> str:
        """
        Formats participant names:
        - Capitalizes each word (e.g., 'lakshmi somisetty' -> 'Lakshmi Somisetty')
        - Preserves common acronyms in all-caps (e.g., 'vvl' -> 'VVL')
        """
        if not raw_name or pd.isna(raw_name):
            return ""

        words = str(raw_name).strip().split()
        formatted_words = []
        for word in words:
            # Common acronyms / initials
            if word.lower() in ["vvl", "dr", "nri", "sri", "km", "md"]:
                if word.lower() in ["vvl", "nri", "md"]:
                    formatted_words.append(word.upper())
                else:
                    formatted_words.append(word.capitalize())
            else:
                formatted_words.append(word.capitalize())
        return " ".join(formatted_words)

    @staticmethod
    def clean_cell_value(val: Any) -> Any:
        """
        Cleans pandas cell values:
        - Replaces NaN with empty string
        - Converts float numbers that are integers (e.g., 1934214.0) to clean strings ('1934214')
        """
        if pd.isna(val):
            return ""
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        return str(val).strip()

    @classmethod
    def parse_file(cls, file_content: bytes, filename: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Reads raw file bytes (Excel or CSV), cleans all columns, and returns:
        1. columns: list of detected header names
        2. records: list of cleaned row dictionaries
        """
        # Read Excel or CSV directly from in-memory bytes
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            df = pd.read_excel(io.BytesIO(file_content))

        # Clean column headers
        df.columns = [str(c).strip() for c in df.columns]

        # Extract available columns
        columns = list(df.columns)

        records: List[Dict[str, Any]] = []

        for _, row in df.iterrows():
            row_dict: Dict[str, Any] = {}
            for col in columns:
                row_dict[col] = cls.clean_cell_value(row[col])

            # Construct Full_Name intelligently if separate First and Last Name exist
            first_name = row_dict.get("First Name", "")
            last_name = row_dict.get("Last Name", "")
            if first_name or last_name:
                raw_full = f"{first_name} {last_name}".strip()
                row_dict["Full Name"] = cls.format_name_casing(raw_full)
            elif "Name" in row_dict:
                row_dict["Full Name"] = cls.format_name_casing(row_dict["Name"])

            records.append(row_dict)

        # If we added 'Full Name', ensure it's in the columns list for the UI
        if "Full Name" not in columns and any("Full Name" in r for r in records):
            columns.insert(0, "Full Name")

        return columns, records
