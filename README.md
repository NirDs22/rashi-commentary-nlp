# Stylometric Analysis of Rashi's Talmudic Commentary

This repository contains code and analysis for a stylometric (computational stylistics) study of Rashi's commentary on the Talmud.  
The project aims to identify stylistic patterns, linguistic features, and possible authorship attribution in different volumes (Masehtot/מסכתות).

---

## Project Overview

- **Goal:** Use NLP and statistical methods to analyze, profile, and distinguish authentic Rashi commentary from disputed or alternative segments.
- **Motivation:** Parts of Rashi's commentary are historically debated. Can computational methods help highlight unique stylistic markers?

---

## Code Structure

- `src/make_format.py`  
  Preprocess and format raw Excel commentaries (cleaning, splitting, basic feature extraction).
- `src/project_make_data12.py`  
  Main pipeline: computes summary statistics (comment length, vocabulary richness, Aramaic/Hebrew ratio, complexity, etc.) for each tractate.
- `src/words_stss.py`  
  Counts and compares word frequencies by group/tag ("rashi", "other"), exports summary tables.

- `data/`  
  Example Hebrew commentary files (Excel format; see Data Usage notice).
- `notebooks/`  
  Jupyter notebooks for exploratory analysis, visualization, and summary of findings.
- `results/`  
  Output graphs and summary tables.

---

## Methodology

1. **Data cleaning & formatting**  
   (removal of special characters, split into “dibur hamatchil” and comment, page tracking)
2. **Feature extraction**  
   (comment length, unique words, average word length, Aramaic/Hebrew markers, complexity, etc.)
3. **Statistical comparison**  
   (by tractate and group: "rashi", "other", "unknown")
4. **Word frequency & clustering analysis**  
   (identify common words, stylistic outliers, potential authorship markers)

---

## Results & Insights

- Visualizations of stylistic similarity/distance between tractates
- Top distinguishing features for “rashi” vs. “other” commentaries
- Tables and graphs summarizing key findings

---

##  Data Usage

Data files downloaded from www.sefaria.org.il/texts/Talmud (open source).  

---

## Credits

- Project developed as part of M.Sc. studies, Bar Ilan University

---

> *Feedback is welcome!*
