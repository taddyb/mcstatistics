import re
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

COLUMNS = [
    'Item Name',
    'Serving Size',
    'Calories',
    'Calories From Fat',
    'Total Fat (g)',
    '% Daily Value*',
    'Saturated Fat (g)',
    '% Daily Value**',
    'Trans Fat (g)',
    'Cholesterol (mg)',
    '% Daily Value*',
    'Sodium (mg)',
    '% Daily Value*',
    'Carbohydrates (g)',
    '% Daily Value*',
    'Dietary Fiber (g)',
    '% Daily Value*',
    'Sugars (g)',
    'Protein (g)',
    'Vitamin A',
    'Vitamin C',
    'Calcium',
    'Iron'
]

OZ_PATTERN = r'(\s*[^\s]+\s+oz)'
LONG_STR_PATTERN = r'\([^)]*\)\s*'

__all__ = ['read_menu']

def read_menu(pdf_path: Path | str, output_path: Path | str | None = None) -> pd.DataFrame:
    """A function to read a complex mcdonalds nutrition pdf and return a pandas dataframe

    Parameters
    ----------
    pdf_path : Path | str
        The path to the PDF
    output_path : Path | str | None
        The path to save the output CSV

    Returns
    -------
    pd.DataFrame | None
        The pandas dataframe if no output path is provided
    """
    reader = PdfReader(pdf_path)
    df_list = []
    data = []
    for idx, page in enumerate(reader.pages):
        if idx < 8:
            text = page.extract_text()
            menu = text.split('\nIron')[1]
            if "Note: " in menu:
                menu = menu.split("Note: ")[0]
            if ' \nBurgers & Sandwiches\n' in menu:
                menu = menu.split(' \nBurgers & Sandwiches\n')[1]

            menu_text = menu.split('\n')
            line = []
            tmp_str = ""

            for item in menu_text:
                if bool(re.search(LONG_STR_PATTERN, item)):
                    try:
                        result = item.split(') ')[1].split(' ')

                        _parts = re.split(OZ_PATTERN, tmp_str)
                        parts = [part for part in _parts if part.strip()]  # Clean empty strings
                        tmp_str = ""
                        for part in parts:
                            line.append(part)

                        for _result in result:
                            line.append(_result)

                        # creating a new data row
                        data.append(line)
                        line = []
                    except IndexError:
                        # Most likely a case where the item is not formatted correctly
                        tmp_str += f"{item} "
                else:
                    tmp_str += f"{item} "

            df = pd.DataFrame(data, columns=COLUMNS)
            data = []
            df_list.append(df)
    master_menu = pd.concat(df_list)
    if output_path:
        master_menu.to_csv(output_path, index=False)
    return master_menu
