# Background

Inspired by https://github.com/ntulpule/Schwab-1099B-Parser/blob/master/convert-schwab-1099pdf-txt.py

# Prerequisites

Needs `pdftotext` from `poppler-utils`. On Ubuntu:

```
sudo apt-get install poppler-utils
```

# Help

Run `python3 main.py --help`:

```
$ python3 main.py --help
usage: main.py [-h] [-i I] [-o O]

optional arguments:
  -h, --help  show this help message and exit
  -i I        Input PDF
  -o O        Output CSV
```

# Usage

Write to `out.csv`

```
python3 main.py -i My_1099B.pdf -o out.csv
```

Write to standard out:

```
python3 main.py -i My_1099B.pdf
```

# Testing

```
python3 tests.py

python3 integration_tests.py path/to/test/pdfs
```
