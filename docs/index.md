# domdb docs 

This is the documentation for domdb, a tool for citing Danish judicial verdicts in LaTeX.

## Features
- Download verdicts
- Convert to BibTeX
- Convert to EVID structure

## Help
<pre>
<font color="#C01C28"><b>❯</b></font> <font color="#12488B">domdb</font>
<b>Usage: domdb </b><font color="#A2734C"><b>...</b></font><b> </b><font color="#2D2D2D"><b> (--json, -h, --help)</b></font>
<font color="#D0CFCC"><b>Description: Tools for citing Danish judicial verdicts using BibTeX.</b></font>
<font color="#228594"><b>domdb</b></font>                    <font color="#B4B4B4"><b>Tools for citing Danish judicial verdicts using BibTeX.</b></font>
<font color="#2D2D2D">├── </font><font color="#A2734C">--directory, -d</font>      <font color="#A2734C"><i>Directory to save JSON case files</i></font><font color="#8B8A88"><b> (default: ~/domdatabasen/cases)</b></font>
<font color="#2D2D2D">├── </font><font color="#2AA1B3">download</font>             <font color="#B4B4B4"><b>Download verdicts from domsdatabasen.dk.</b></font>
<font color="#2D2D2D">└── </font><font color="#26A269"><b>output</b></font>               <font color="#B4B4B4"><b>Commands for outputting data.</b></font>
<font color="#2D2D2D">    ├── </font><font color="#2AA1B3">bib</font>              <font color="#B4B4B4"><b>Convert JSON case files to BibTeX format.</b></font>
<font color="#2D2D2D">    │   ├── </font><font color="#A2734C">--number, -n</font> <font color="#A2734C"><i>Maximum number of verdicts to process</i></font><font color="#8B8A88"><b> (default: -1)</b></font>
<font color="#2D2D2D">    │   └── </font><font color="#A2734C">--output, -o</font> <font color="#A2734C"><i>Output BibTeX file path</i></font><font color="#8B8A88"><b> (default: resources/cases.bib)</b></font>
<font color="#2D2D2D">    └── </font><font color="#2AA1B3">j2e</font>              <font color="#B4B4B4"><b>Convert JSON case files to EVID directory structure.</b></font>
<font color="#2D2D2D">        ├── </font><font color="#A2734C">--number, -n</font> <font color="#A2734C"><i>Maximum number of cases to process</i></font><font color="#8B8A88"><b> (default: -1)</b></font>
<font color="#2D2D2D">        └── </font><font color="#A2734C">--output, -o</font> <font color="#A2734C"><i>Output directory for EVID structure</i></font><font color="#8B8A88"><b> (default: evid)</b></font>
</pre>