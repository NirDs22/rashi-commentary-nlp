"""
Iterate over source files and make data table of statistics
"""

import os
import pandas as pd
from collections import defaultdict
from typing import List, Dict, Any, Tuple
import string

# List of Hebrew stopwords
hebrew_stopwords = set([
    'של', 'על', 'עם', 'את', 'זה', 'היא', 'הוא', 'הם', 'הן', 'אני', 'אתה', 'את', 'אנחנו', 'הוא', 'היא', 'הם', 'הן', 
    'מה', 'מי', 'זה', 'זאת', 'אלה', 'אלו', 'כן', 'לא', 'אם', 'או', 'אבל', 'כי', 'כאשר', 'אשר', 'אף', 'כל', 'רק', 
    'כמו', 'למה', 'לכן', 'למרות', 'אחרי', 'לפני', 'בין', 'תחת', 'מאחורי', 'מעל', 'מתחת', 'מול', 'ליד', 'אצל', 
    'ב', 'ל', 'מ', 'כ', 'ש', 'ו', 'ה', 'י', 'ת', '-', '–'
])
# Statistic data table columns
COLUMNS = [
    'file',
    'num_pages',
    #'num_refs',
    #'common_words',
    'avg_comment_words',
    'avg_comment_char',
    'avg_comment_char_per_word',
    'max_comment_len_words',
    'min_comment_len_words',
    'loazi_words_count',
    'avg_comments_wLoazi',
    'unique_words_count',
    'total_words_count',
    'unique_words_usage_rate',
    'comment_complexity',
    'masechet']
stt_df = pd.DataFrame(columns=COLUMNS)
comment_lengths_df = pd.DataFrame(columns=['masechet', 'length'])
word_count = defaultdict(int)

# Dictionary for Talmud masechet to Rashi or other
talmud_dict = {
    "megila": "rashi",
    "sanhendrin": "rashi",
    "brachot": "rashi",
    "psahim": "rashi",
    "beitza": "rashi",
    "sukka": "rashi",
    "nazir": "other",
    "horayot": "unknown",
    "shabat": "rashi",
    "taanit": "unknown",
    "hagiga": "rashi",
    "eruvin": "rashi",
    "nedarim": "other",
    "moed": "mixed",
    "pasahimRashbam": "other",
    "meila": "unknown",
    "yoma": "rashi",
    "kiddushin": "rashi",
    "zevahim": "rashi",
    "babaMetsia" : "rashi",
    "babaKama": "rashi",
    "gittin" : "rashi"
}

def make_timestamp() -> str:
    " Make a timestamp for the output file "
    from datetime import datetime
    now = datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")

# preprocess file
def preprocess_file(peirush: pd.DataFrame) -> pd.DataFrame:
    " Preprocess a file for analysis "
    # remove empty rows
    peirush = peirush.dropna()
    # replace all the "–" with "-" from 
    peirush.iloc[:,0] = peirush.iloc[:,0].replace("–", "-")
    # Remove parentheses and content within them
    # add a "#" to mark the removed content for future reference
    peirush.iloc[:,0] = peirush.iloc[:,0].str.replace(r"\(.*\)", "#", regex=True)

    return peirush

def aramit_preference_rate(text: List[str]) -> float:
    "Calculate the rate of Aramaic words usage in relation to Hebrew words"
    heb_arm = {
        'שלא': 'דלא',
        'גם': 'נמי',
        'שאמר': 'דאמר',
        'תאמר' : 'תימא',
        'שם': 'התם',
        'מה': 'מאי',
        'לו': 'ליה',
        'שנינו': 'תנן'
    }
    rates = []
    for heb_word, arm_word in heb_arm.items():
        heb_count = text.count(heb_word)
        arm_count = text.count(arm_word)
        if heb_count > 0:
            rates.append(arm_count / heb_count)
        else: rates.append(1.0)

    # Words ending with "א" are Aramaic
    aramaic_count = sum(1 for word in text if word.endswith('א'))
    # Words ending with "ה" are Hebrew
    hebrew_count = sum(1 for word in text if word.endswith('ה'))
    if hebrew_count > 0:
        rates.append(aramaic_count / hebrew_count)

    return sum(rates) / len(rates) if rates else 0.0

def comment_complexity(text: List[str]) -> Tuple[float, float]:
    "Calculate the average word length and the average sentence length"
    linking_words = [ "דא",  "דהא", "הואיל", "היכי", "הכא", "התם", "השתא", "עד", "אי", "אלא", "ואי", "ואי נמי", "ואם", "ואם תמצא לומר", "ואם תמצא לומר", "אלא",  "אי נמי", 
                     "ואי תימא",
                     "אפילו", "ועוד", "דכוותה", "כגון", "הכי", "הכי נמי", "אי נמי", "ולאו", "ולא", "מאי", "למה",
                       "אמאי", "בעי", "איבעיא", "לעולם", "אדרבה", "מיהו", "משום", "כיון", "כל שכן", "ואם", "ויש"]
    # count linking words in text
    text_complexity = 0
    for comment in text:
        if len(comment) == 0: continue
        text_complexity += sum(1 for word in comment if word in linking_words) / len(comment)

    return text_complexity / len(text) if len(text)>0 else 0.0

def format_df(df: pd.DataFrame) -> pd.DataFrame:
    " Format the data frame to perush and dibur"
    formatted_df = pd.DataFrame(columns=['dibur', 'comment', 'page'])
    now_page = ''

    for _,content in df.iterrows():
        print(f"\r{df.columns[0]} | {now_page} | {content.iloc[0]}", end='', flush=True)
        if content.iloc[0].startswith("Daf"):
            now_page = content.iloc[0].split(' ')[1]

        elif not content.iloc[0].startswith("Line"):
            dibur_rows = content.iloc[0].split(': ')
            for dibur_row in dibur_rows:
                split_content = dibur_row.split('-',1)
                if len(split_content) == 1:
                    split_content.insert(0, None)

                dibur, comment = split_content
                formatted_df = formatted_df._append({'dibur': dibur,
                                                    'comment': comment,
                                                    'page': now_page},
                                                     ignore_index=True)
    return formatted_df

def common_words_stats(text: List[str]) -> Dict[str, int]:
    " Calculate the common words in the text "
    global word_count
    # Count the occurrences of each word
    for word in text:
        if word not in hebrew_stopwords:
            word_count[word] += 1
    return dict(word_count)

def get_file_stats(file_path: str) -> Dict[str, Any]:
    """Get statistics for a single file."""
    global comment_lengths_df
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            print(f"Reading file: {file_path}")
            new_row = {'file': file_path}

            # Load Excel file into a DataFrame
            subdata = pd.read_excel(file_path)
            subdata = subdata.dropna()  # Remove empty rows

            # Remove parentheses and content within them
            subdata.iloc[:, 0] = subdata.iloc[:, 0].str.replace(r"\(.*\)", "", regex=True)

            # Format the DataFrame
            formatted_df = format_df(subdata)

            # Remove punctuation from text
            translator = str.maketrans('', '', string.punctuation + '-:')
            formatted_df['dibur'] = formatted_df['dibur'].str.translate(translator)
            formatted_df['comment'] = formatted_df['comment'].str.translate(translator)

            # Extract "masechet" from the file name
            new_row['masechet'] = "".join(file_path.split('/')[-1].split('_')[-1]).replace('.xlsx', '')
            tag = talmud_dict.get(new_row['masechet'], 'unknown')

            # Number of pages
            new_row['num_pages'] = formatted_df['page'].nunique()

            # Average comment by words
            comment_lengths_words = formatted_df['comment'].str.split().str.len()
            new_row['avg_comment_words'] = comment_lengths_words.mean()

            # add comment_lengths_words to comment_lengths_df
            comment_lengths_words_df = pd.DataFrame(comment_lengths_words)
            comment_lengths_words_df['masechet'] = new_row['masechet']
            comment_lengths_df = comment_lengths_df._append(comment_lengths_words_df, ignore_index=True)

            # Average comment len by characters
            comment_lengths_chars = formatted_df['comment'].str.len()
            new_row['avg_comment_char'] = comment_lengths_chars.mean()

            # Average characters per word
            avg_chars_per_word = (
                formatted_df['comment'].str.len().sum() /
                formatted_df['comment'].str.split().str.len().sum()
            ) if formatted_df['comment'].str.split().str.len().sum() > 0 else 0
            new_row['avg_comment_char_per_word'] = avg_chars_per_word

            # Average linking words per sentence (text complexity)
            new_row['comment_complexity'] = comment_complexity(formatted_df['comment'].str.split())

            # Minimum comment length in words (ignoring empty comments)
            min_comment_len_words = comment_lengths_words.replace(0, float('inf')).min()
            new_row['min_comment_len_words'] = 0 if min_comment_len_words == float('inf') else min_comment_len_words

            # Maximum comment length in words
            new_row['max_comment_len_words'] = comment_lengths_words.max()

            # Count occurrences of "לע״ז"
            new_row['loazi_words_count'] = formatted_df['comment'].str.contains('בלעז').sum()

            # amount comments
            num_comments = formatted_df['comment'].count()
            # amount comments with "לע״ז"
            num_loazi_comments = formatted_df['comment'].str.contains('בלעז').sum()

            # Average "לע״ז" occurrences per comments
            new_row['avg_comments_wLoazi'] = num_loazi_comments / num_comments

            # Unique word count
            all_words = ' '.join(formatted_df['comment']).split()
            new_row['unique_words_count'] = len(set(all_words))

            # total word count
            new_row['total_words_count'] = len(all_words)

            # unique words usage rate
            new_row['unique_words_usage_rate'] = new_row['unique_words_count'] / new_row['total_words_count']

            # Get aramit preference rate (masechet)
            new_row['aramit_preference_rate'] = aramit_preference_rate(all_words)

            print(f"{file_path} added to data table")
        return new_row

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        raise e
        return {}

def get_proximity(stt_df):
    # חישוב ממוצעים של כל תגית
    grouped_means = stt_df[stt_df['tag'] != 'unknown'].groupby("tag").mean(numeric_only=True)
    params = stt_df.drop(columns = ['tag', 'masechet']).columns
    proximity_df = pd.DataFrame(columns=params, index = stt_df[stt_df['tag'] == 'unknown']['masechet'])
    distace_df = pd.DataFrame(columns=params, index = stt_df[stt_df['tag'] == 'unknown']['masechet'])

    for masechet in proximity_df.index:
        for param in params:
            # Check if the parameter is numeric
            if pd.api.types.is_numeric_dtype(stt_df[param]):
                # Calculate the proximity to rashi or other for the masechet
                val = stt_df.loc[stt_df['masechet'] == masechet, param].values[0]
                distance_rashi = abs(val - grouped_means.loc['rashi', param])
                distance_other = abs(val - grouped_means.loc['other', param])
                # Calculate the distance to the average of the other tag
                distace_df.loc[masechet, param] = min(distance_rashi, distance_other)
                # Determine the proximity
                if distance_rashi < distance_other:
                    proximity_df.loc[masechet, param] = 'rashi'
                elif distance_rashi > distance_other:
                    proximity_df.loc[masechet, param] = 'other'
                else:
                    proximity_df.loc[masechet, param] = 'equal'

    return proximity_df, distace_df

if __name__ == '__main__':
    source_dir = r'/Users/nird/Library/CloudStorage/OneDrive-Personal/Uni/שנה ב/מדעי הרוח הדיגיטליים/rashi/sources'
    output_file = f'outputs/data_table_{make_timestamp()}.xlsx'

    # Iterate over files in source directory
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.xlsx'):
                file_path = os.path.join(root, file)
                stt_df = stt_df._append(get_file_stats(file_path), ignore_index=True)
    
    stt_df['masechet'] = stt_df.masechet.str.replace('.xlsx', '')
    stt_df['tag'] = stt_df['masechet'].map(talmud_dict)
    stt_df = stt_df[['tag',
                     'masechet',
                    'avg_comment_words',
                     'avg_comment_char',
                     'avg_comment_char_per_word',
                     'avg_comments_wLoazi',
                     'unique_words_usage_rate',
                     'comment_complexity',
                     'aramit_preference_rate']]


    comment_lengths_df['masechet'] = comment_lengths_df.masechet.str.replace('.xlsx', '')
    comment_lengths_df['tag'] = comment_lengths_df['masechet'].map(talmud_dict)

    proximity_df, distance_df = get_proximity(stt_df)

    with pd.ExcelWriter(output_file, engine='openpyxl', mode='w') as writer:
        comment_lengths_df.to_excel(writer, sheet_name='comment_lengths_df', index=False)
        stt_df.to_excel(writer, sheet_name='data_table', index=False)
        proximity_df.to_excel(writer, sheet_name='proximity_df', index=True)
        distance_df.to_excel(writer, sheet_name='proximity_df', index=True, startrow=proximity_df.shape[0] + 2)
    print('Data table written to', output_file)
        
        
        


