# Repository build rules

- Compile this thesis only with TeX Live 2026, not MiKTeX.
- Use `C:\texlive\2026\bin\windows\latexmk.exe -xelatex -outdir=build JNUThesis.tex` from the repository root.
- Never invoke `xelatex`, `pdflatex`, or `bibtex` directly in the repository root.
- Keep all generated LaTeX files, including the PDF, under `build/`.
- Do not install missing MiKTeX packages for this project; first verify the TeX Live command and build path.
