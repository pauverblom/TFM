#!/bin/bash
chapters=(
  "Conclusiones.tex"
  "Creando Blue Stragglers.tex"
  "Evolución de la Blue Straggler.tex"
  "Hidrodinámica y Oscilaciones Estelares.tex"
  "Introducción.tex"
)

for chapter in "${chapters[@]}"; do
  echo "Spawning agent for $chapter..."
  agy --dangerously-skip-permissions --print "You are an expert LaTeX editor. Your task is to process /home/pauver/repos/pauverblom/TFM/TeX/Capítulos/$chapter. Read the file, identify any scientific claim, fact, or specific finding that typically requires a reference but currently lacks one, and insert the LaTeX placeholder \citep{CITAR} immediately after those claims. Do not add \citep{CITAR} to every sentence; only to scientific claims needing citations according to best practices. Use your file editing tools to apply the changes and save the file." > "agent_${chapter%.tex}.log" 2>&1 &
done

echo "Agents deployed! Waiting for them to finish..."
wait
echo "All agents completed!"
