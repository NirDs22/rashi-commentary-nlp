#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 09:48:18 2024

@author: nird
"""

import pandas as pd

path = input("Enter File Path:\n-> ")

peirush = pd.read_excel(path)
peirush = peirush.dropna()

# replace all the "–" with "-"
peirush.iloc[:,0] = peirush.iloc[:,0].str.replace('–', '-')

# save references count
ref_avg_peirush = peirush.iloc[:,0].str.count('\(').sum() / peirush.shape[0]

# Remove parentheses and content within them
peirush.iloc[:,0] = peirush.iloc[:,0].str.replace(r"\(.*\)", "", regex=True)

def format_df(df):
    formatted_df = pd.DataFrame(columns=['dibur', 'comment', 'page'])
    now_page = ''

    for i,content in df.iterrows():
        print(df.columns[0],"|",now_page,"|",content.iloc[0])
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

peirush = format_df(peirush)

# Remove punctuations
import string

translator = str.maketrans('', '', string.punctuation)
peirush['dibur'] = peirush['dibur'].str.translate(translator)
peirush['comment'] = peirush['comment'].str.translate(translator)

# commen length by characters
peirush['comment_len'] = peirush['comment'].str.len()

#   avg per page
peirush_avg_comm_char = peirush.groupby(['page'])['comment_len'].mean()

# comment length by words
peirush['comment_len_words'] = peirush['comment'].str.split().str.len()

#   avg per page
peirush_avg_comm_char = peirush.groupby(['page'])['comment_len_words'].mean()

print(peirush.comment_len.describe())

# comparison of common comment words
from collections import Counter

peirush_words = peirush.comment.str.cat(sep=' ').split()

peirush_words_count = Counter(peirush_words)

peirush_common = peirush_words_count.most_common(10)

peirush_common_words = [word[0] for word in peirush_common]
peirush_common_counts = [word[1] for word in peirush_common]

print(peirush_common)
