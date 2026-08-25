# Keep every generated LaTeX artifact out of the repository root.
$out_dir = 'build';

# This thesis is a XeLaTeX project. Use the verified TeX Live installation,
# never the separately installed MiKTeX binaries.
$pdf_mode = 5;
$xelatex = 'C:/texlive/2026/bin/windows/xelatex.exe %O %S';
$bibtex = 'C:/texlive/2026/bin/windows/bibtex.exe %O %B';
