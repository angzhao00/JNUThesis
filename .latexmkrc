# Keep every generated LaTeX artifact out of the repository root.
$out_dir = 'build';

# This thesis is a XeLaTeX project. Engine binaries are resolved from PATH,
# so this config works on any machine whose PATH provides TeX Live 2026
# (including TinyTeX). Never use MiKTeX binaries.
$pdf_mode = 5;
