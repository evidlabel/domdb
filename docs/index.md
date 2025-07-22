# domdb

Tools for citing Danish judicial verdicts in LaTeX and typst.

## Overview

`domdb` is a Python package that helps researchers and legal professionals work with Danish judicial verdicts by:

- Downloading verdicts from domsdatabasen.dk
- Converting verdict data to BibTeX format for LaTeX documents

## Quick Start

After installation (see [Installation](installation.md)):

```bash
domdb get
domdb bib
```

See [Installation](installation.md) and [Usage](usage.md) for detailed instructions.

## Citing verdicts 
### [typst](https://typst.app/) example
```bash
wget https://raw.githubusercontent.com/evidlabel/domdb/master/resources/cases.bib  -O cases.bib
echo "Citing all verdicts:
#bibliography(\"cases.bib\",full:true)" > all.typ
typst compile all.typ
```
Produces a pdf with all verdicts currently in `domstoldatabasen`:
<iframe src="assets/all.pdf" width="100%" height="500px"></iframe>

### Latex example

```bash
wget https://raw.githubusercontent.com/evidlabel/domdb/master/resources/cases.bib  -O cases.bib
echo '\documentclass{article}
\usepackage[backend=biber]{biblatex}
\usepackage{hyperref}
\addbibresource{cases.bib}
\begin{document}
\noindent Citing two verdicts: \cite{bs101312023shr,bs101482018hel}
\printbibliography
\end{document}' > all.tex
lualatex all.tex
biber all
lualatex all.tex
lualatex all.tex
```

<iframe src="assets/ltx.pdf" width="100%" height="500px"></iframe>
