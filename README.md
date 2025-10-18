# README.md

## python-project-arxiv

A small, interactive command-line application to search scientific articles on **arXiv** by topic, author, or title/abstract, then save a tidy JSON file with the results. The project targets Python **3.11+** and depends on the `arxiv` library.

---

## Table of contents

- [Features](#features)  
- [Quick start](#quick-start)  
  - [Using `git` and `uv`](#using-git-and-uv)  
  - [Alternative with `pip`](#alternative-with-pip)  
- [How to use](#how-to-use)  
- [Output format](#output-format)  
- [Project structure](#project-structure)  
- [Classes overview](#classes-overview)  
- [Troubleshooting](#troubleshooting)  
- [License](#license)

---

## Features

- Interactive prompts to choose **search type** (topic / author / title+abstract), **sorting**, **order**, and **max results** (1–10).  
- Uses arXiv’s official API via the `arxiv` Python package with a resilient client (pagination, delay between requests, and retries).  
- Saves neatly formatted results to `articles.json` (authors, title, dates, journal ref if any, permalink, and a trimmed abstract).  

---

## Quick start

### Using `git` and `uv`

> Requirements: [Python 3.11+ installed](https://www.python.org/), [uv](https://docs.astral.sh/uv/) installed (`pipx install uv` or `pip install uv`).

```bash
# 1) Clone the repository
git clone https://github.com/ilclaudio/python-project-arxiv.git
cd python-project-arxiv

# 2) Create a virtual environment and install dependencies from pyproject.toml
uv sync

# 3) Run the app
uv run python search_articles.py
```

Why `uv sync`? It reads `pyproject.toml` (which declares `requires-python = ">=3.11"` and the dependency on `arxiv`) and installs everything into a local virtual environment for you.

**Notes**
- If you prefer to activate the environment explicitly: `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows) after `uv sync`, then run `python search_articles.py`.
- You can also use `uv run search_articles.py` (uv infers `python`).

### Alternative with `pip`

```bash
git clone https://github.com/ilclaudio/python-project-arxiv.git
cd python-project-arxiv

python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -U pip
pip install -e .
python search_articles.py
```

The `-e .` reads `pyproject.toml` and installs the `arxiv` dependency.

---

## How to use

Run the program; it will guide you through a few prompts:

1) **Search type**
```
1 - By topic
2 - By author
3 - By title/abstract
```

2) **Search text** (non-empty, max 100 chars).

3) **Sorting**
```
1 - Relevance
2 - Last updated
3 - Publication date
```
4) **Order**
```
1 - Ascending
2 - Descending
```

5) **Max results** (1–10).

The app will query arXiv and, if results are found, write them to `articles.json`, then print the absolute file path so you can open it right away.

---

## Output format

Saved as `articles.json` in pretty-printed UTF-8 JSON. Each item contains:

```json
[
  {
    "id": 1,
    "authors": ["First Author", "Second Author"],
    "title": "Paper title",
    "publication_date": "YYYY-MM-DD",
    "journal": "N/A or Journal Ref",
    "link": "https://arxiv.org/abs/XXXX.XXXXX",
    "abstract": "First ~300 characters of the abstract..."
  }
]
```

Fields and truncation rules are applied exactly as above.

---

## Project structure

```
python-project-arxiv/
├─ pyproject.toml        # Project metadata and dependencies (Python 3.11+, arxiv>=2.2.0)
├─ search_articles.py    # CLI application entry point (run this)
└─ README.md             # You are here
```

The environment and dependency definitions live in `pyproject.toml`.

---

## Classes overview

All classes live in `search_articles.py`.

- **`UserInterface`**  
  Handles all user interaction: prints menus, validates inputs (e.g., non-empty text ≤ 100 chars; numeric ranges), and shows where results are saved. Provides helper methods such as `get_search_type`, `get_search_query`, `get_sort_by`, `get_sort_order`, `get_max_results`, and an orchestrator `collect_all_inputs()`.

- **`ArxivSearcher`**  
  Wraps the `arxiv` client with sensible defaults (`page_size=100`, `delay_seconds=3.0`, `num_retries=5`) and exposes:  
  - `build_query(...)` translating the chosen search type into arXiv query syntax (`all:`, `au:`, `ti:` / `abs:`),  
  - `get_sort_criterion(...)` and `get_sort_order(...)` mapping menu choices to `arxiv.SortCriterion` and `arxiv.SortOrder`,  
  - `search(...)` that performs the request with a small retry loop and exponential backoff (5s, 10s, 15s) on transient errors.

- **`ResultManager`**  
  Converts raw `arxiv.Result` objects into a friendly list of dictionaries and writes them to `articles.json`. It normalizes authors, formats dates (`YYYY-MM-DD`), keeps a journal reference when present, and truncates abstracts to ~300 characters. Methods: `format_results(results)` and `save_to_file(data, filename="articles.json")`.

- **`main()`**  
  Wires everything together: collects inputs → executes the search → formats & saves → prints the saved file path; with graceful handling of keyboard interrupts and generic errors.

---

## Troubleshooting

- **No results found**  
  Try different keywords, switch sorting, or increase the result count (up to 10).

- **Temporary arXiv errors / timeouts**  
  The app already retries with backoff. If it ultimately fails, wait a bit and run again, or reduce the number of results.

- **ImportError for `arxiv`**  
  Ensure you installed dependencies with `uv sync` (recommended) or `pip install -e .`, and that you’re using the project’s virtual environment. `arxiv>=2.2.0` is declared in `pyproject.toml`.

---

## License

Add a license file (e.g., MIT) if you plan to distribute the project. (Not specified in the current repository.)

---

**Happy searching!**
