#!/bin/bash
# Script to spawn scientific and LaTeX review agents for the TFM chapters

# Ensure Reviews directory exists
mkdir -p /home/pauver/repos/pauverblom/TFM/Reviews

chapters=(
  "Resumen.tex"
  "Introducción.tex"
  "Hidrodinámica y Oscilaciones Estelares.tex"
  "Creando Blue Stragglers.tex"
  "Evolución de la Blue Straggler.tex"
  "Conclusiones.tex"
)

echo "=== STEP 1: Spawning Chapter Review Agents ==="

for chapter in "${chapters[@]}"; do
  chap_name="${chapter%.tex}"
  echo "Spawning agents for $chapter..."
  
  # 1. Scientific Review Agent (Gemini 3.1 Pro (High))
  agy --dangerously-skip-permissions --model "Gemini 3.1 Pro (High)" --print "You are an expert scientific peer reviewer in astrophysics, stellar evolution, and asteroseismology. Conduct an in-depth scientific review of the chapter located at /home/pauver/repos/pauverblom/TFM/TeX/Capítulos/$chapter.
  
  Evaluate:
  1. Scientific correctness: Check if all astrophysical claims, formulas, and arguments are correct.
  2. Mathematical correctness: Verify derivations, equation structures, indices, signs, and consistency.
  3. Physical unit consistency: Ensure units (e.g., M_sun, cycles/day, etc.) are correct and standard in asteroseismology.
  4. Logical coherence and leaps: Identify any assertions that lack explanation or evidence, or contain contradictions.
  5. Scientific writing style: Evaluate bad scientific writing style (e.g., awkward phrasing, lack of academic tone, or lack of clarity).
  
  Do NOT modify the file. Output a detailed, structured Markdown report in Spanish with your findings. Highlight strong points, critical errors, minor inconsistencies, and style recommendations. Do not include introductory or concluding conversational chat; start directly with the markdown content." > "/home/pauver/repos/pauverblom/TFM/Reviews/scientific_review_${chap_name}.md" 2>&1 &
  
  # 2. LaTeX & Style Review Agent (Gemini 3.5 Flash (High))
  agy --dangerously-skip-permissions --model "Gemini 3.5 Flash (High)" --print "You are an expert LaTeX and academic style editor. Conduct a detailed formal and stylistic review of the chapter located at /home/pauver/repos/pauverblom/TFM/TeX/Capítulos/$chapter.
  
  Evaluate:
  1. LaTeX formatting and syntax: Look for syntax errors, improper math mode usage (e.g., using \$\$ for display math instead of \\[ \\], raw/unescaped characters, bad spacing, etc.).
  2. Spelling, grammar, and punctuation in Spanish.
  3. Citations and Cross-referencing: Ensure citations use correct citation commands (\\citep, \\citet, \\autocite, etc.) and cross-references (\\ref, \\label) are consistent.
  4. Style check - IMPERSONAL STYLE (CRITICAL): Strictly identify any occurrences of first-person plural verbs or pronouns (e.g., 'hemos', 'observamos', 'esperamos', 'nuestro', 'nuestras', 'nuestros', 'nosotros'). The entire text must be written in an impersonal, passive academic style (e.g., 'se observa', 'se calcula', 'este estudio', 'las simulaciones'). Provide the line numbers and exact suggestions to rewrite them to impersonal passive.
  
  Do NOT modify the file. Output a detailed Markdown report in Spanish listing your findings as bullet points with clear textual explanations and referencing specific line numbers. Do not include introductory or concluding conversational chat; start directly with the markdown content." > "/home/pauver/repos/pauverblom/TFM/Reviews/latex_review_${chap_name}.md" 2>&1 &
done

echo "Waiting for chapter review agents to complete..."
wait
echo "All chapter review agents completed!"

echo "=== STEP 2: Running Global Coherence Agent ==="
echo "Spawning Global Coherence Agent for all chapters..."

# 3. Global Coherence Agent (Gemini 3.1 Pro (High))
agy --dangerously-skip-permissions --model "Gemini 3.1 Pro (High)" --print "You are an expert scientific editor and coordinator. Read and evaluate sequentially the following TFM chapters together:
- /home/pauver/repos/pauverblom/TFM/TeX/Capítulos/Resumen.tex
- /home/pauver/repos/pauverblom/TFM/TeX/Capítulos/Introducción.tex
- /home/pauver/repos/pauverblom/TFM/TeX/Capítulos/Hidrodinámica y Oscilaciones Estelares.tex
- /home/pauver/repos/pauverblom/TFM/TeX/Capítulos/Creando Blue Stragglers.tex
- /home/pauver/repos/pauverblom/TFM/TeX/Capítulos/Evolución de la Blue Straggler.tex
- /home/pauver/repos/pauverblom/TFM/TeX/Capítulos/Conclusiones.tex

Evaluate:
1. Notation Continuity: Ensure mathematical notation (variables, indices, symbols) is consistent across all chapters (e.g., ensuring stellar mass is not defined as M in one chapter and m in another, or frequencies).
2. Narrative Promise: Check if the Conclusiones chapter directly addresses and answers the research questions, objectives, or hypotheses proposed in the Introducción chapter.
3. Logical transitions between chapters.

Do NOT modify the files. Output a detailed Markdown report in Spanish with your findings. Structure it to highlight notation mismatches and narrative alignment issues. Do not include introductory or concluding conversational chat; start directly with the markdown content." > "/home/pauver/repos/pauverblom/TFM/Reviews/global_coherence_review.md" 2>&1

echo "Global Coherence Agent completed!"
echo "=== Review Process Finished ==="
