# Repository build rules

- Compile this thesis only with TeX Live 2026 (including TinyTeX), not MiKTeX; the TeX Live bin directory must be first on PATH.
- Use `latexmk -xelatex -synctex=1 -outdir=build JNUThesis.tex` from the repository root.
- Never invoke `xelatex`, `pdflatex`, or `bibtex` directly in the repository root.
- Keep all generated LaTeX files, including the PDF, under `build/`.
- Do not install missing MiKTeX packages for this project; first verify that the commands on PATH resolve to TeX Live 2026.

# Thesis writing rules

- Use direct, evidence-based academic statements. Avoid defensive wording, self-justifying disclaimers, anticipatory rebuttals, and phrases framed around what the thesis does not claim; state the applicable conditions, parameter sources, observations, and conclusions positively.
