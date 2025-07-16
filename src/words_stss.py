" word stats: creating a word freq. table "
import os
import pandas as pd
from collections import defaultdict
from typing import List, Dict, Any, Tuple
import string
import project_make_data12 as pr_scripts

# Dictionary for Talmud masechet to Rashi or other
talmud_dict = {
    "megila": "rashi",
    "sanhendrin": "rashi",
    "brachot": "rashi",
    "psahim": "rashi",
    "beitza": "rashi",
    "sukka": "rashi",
    "nazir": "other",
    "horayot": "horayot",
    "shabat": "rashi",
    "taanit": "taanit",
    "hagiga": "rashi",
    "eruvin": "rashi",
    "nedarim": "other",
    "pasahimRashbam": "other",
    "meila": "meila",
    "yoma": "rashi",
    "kiddushin": "rashi",
    "zevahim": "rashi",
    "babaMetsia" : "rashi",
    "babaKama": "rashi",
    "gittin" : "rashi"
}

tag_words_dict = {
    'rashi': defaultdict(int),
    'other': defaultdict(int),
    'horayot': defaultdict(int),
    'taanit': defaultdict(int),
    'meila': defaultdict(int)
}

def make_timestamp() -> str:
    """Generate a timestamp string."""
    from datetime import datetime
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def common_words_stats(file_path):
    """Count the frequency of each word in a file."""
    global talmud_dict
    global tag_words_dict
    masechet = "".join(file_path.split('/')[-1].split('_')[-1]).replace('.xlsx', '')
    tag = talmud_dict.get(masechet, 'unknown')

    # Load Excel file into a DataFrame
    subdata = pd.read_excel(file_path)
    subdata = subdata.dropna()  # Remove empty rows

    # Remove parentheses and content within them
    subdata.iloc[:, 0] = subdata.iloc[:, 0].str.replace(r"\(.*\)", "", regex=True)

    # Format the DataFrame
    formatted_df = pr_scripts.format_df(subdata)

    # Remove punctuation from text
    translator = str.maketrans('', '', string.punctuation + '-:')
    formatted_df['comment'] = formatted_df['comment'].str.translate(translator)

    formatted_df = formatted_df['comment']


    # Iterate over rows in the DataFrame
    for text in formatted_df:
        # Split text into words
        words = text.split()

        # Count word frequencies
        for word in words:
            tag_words_dict[tag][word] += 1

    return tag_words_dict[tag], tag

if __name__ == '__main__':
    source_dir = r'data'
    output_file = f'results/words_stss_table_{make_timestamp()}.xlsx'

    # Iterate over files in source directory
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.xlsx'):
                file_path = os.path.join(root, file)
                word_counts, tag = common_words_stats(file_path)
                print(f"Processed {file_path} with tag {tag}")
        
    # Convert tag_words_dict to a regular dictionary for DataFrame creation
    tag_words_dict_regular = {tag: dict(words) for tag, words in tag_words_dict.items()}
    
    # Create a DataFrame from the word counts
    df = pd.DataFrame.from_dict(tag_words_dict_regular, orient='index').fillna(0).astype(int)
    df = df.transpose()
    df.index.name = 'Word'
    df.reset_index(inplace=True)
    df.columns = ['Word'] + list(df.columns[1:])
    df = df.sort_values(by='Word')
    df.to_excel(output_file, index=False)
    print(f"Word counts saved to {output_file}")
