# Repository build rules

- Compile this thesis only with TeX Live 2026, not MiKTeX.
- Use `C:\texlive\2026\bin\windows\latexmk.exe -xelatex -outdir=build JNUThesis.tex` from the repository root.
- Never invoke `xelatex`, `pdflatex`, or `bibtex` directly in the repository root.
- Keep all generated LaTeX files, including the PDF, under `build/`.
- Do not install missing MiKTeX packages for this project; first verify the TeX Live command and build path.

# Thesis writing rules

- Use direct, evidence-based academic statements. Avoid defensive wording, self-justifying disclaimers, anticipatory rebuttals, and phrases framed around what the thesis does not claim; state the applicable conditions, parameter sources, observations, and conclusions positively.
