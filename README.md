# N26 PDF Converter

The purpose of this repository is to offer a simple and easy way to convert a N26 PDF monthly statement file into a CSV file.  
It provides a simple command line interface to **process** the PDF file into a CSV file.
It also allow to generate a **journal** file, which contains a summary of past account transactions, with the related categories. Once generated, it can be used during the **process** of converting the PDF file into a CSV file, to override the provided/missing categories.

## Requirements

- Python 3.10 or higher
- Poetry

## Installation

1. Clone the repository
2. Install the dependencies

```bash
poetry install
```

3. Run the application

```bash
poetry run python pdf_converter/main.py --help
```

## Usage

### Generate a journal file

```bash
poetry run python pdf_converter/main.py journal pdf_statement_1.csv ... pdf_statement_n.csv journal.feather
```

### Process a PDF file

```bash
poetry run python pdf_converter/main.py process pdf_statement_1.pdf --journal_filepath journal.feather
```
