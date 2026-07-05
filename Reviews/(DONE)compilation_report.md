# Informe de Compilación del TFM

Este informe resume los resultados y advertencias obtenidos tras compilar localmente el proyecto utilizando la receta por defecto de VS Code (`lualatex` ➔ `biber` ➔ `lualatex` x2).

La compilación ha finalizado **correctamente** y ha generado el archivo PDF final: [main.pdf](file:///home/pauver/repos/pauverblom/TFM/TeX/latex-output/main.pdf).

---

## 1. Advertencias de Formato y Estructura

### 🟡 Altura de Cabecera Insuficiente (`\headheight is too small`)
* **Advertencia**: `Package fancyhdr Warning: \headheight is too small (12.0pt): Make it at least 15.21004pt`
* **Detalle**: Esta advertencia ocurre repetidamente durante la generación de páginas. Aunque en el archivo `main.tex` se incluye `\setlength{\headheight}{15.21004pt}`, el paquete `geometry` o `fancyhdr` redefine o evalúa esta variable antes de que tenga efecto en algunas partes de la estructura del documento.
* **Solución**: Añadir el parámetro `headheight=16pt` directamente en las opciones del paquete `geometry` en la línea 27 de [main.tex](file:///home/pauver/repos/pauverblom/TFM/TeX/main.tex):
  ```latex
  \usepackage[lmargin=1in, rmargin=1in, tmargin=1.5in, bmargin=1.3in, headheight=16pt]{geometry}
  ```

### 🟡 Cajas Desbordadas (`Overfull \hbox` / `Overfull \vbox`)
El compilador reporta algunas regiones de texto o figuras que desbordan los márgenes establecidos por unos pocos puntos:
* **Overfull `\hbox` en la bibliografía**:
  * Ocurre en la entrada correspondiente al *Workshop (TASC8/KASC15)* en las líneas finales y en las direcciones URL de las referencias de StackExchange.
  * **Solución**: Se puede corregir ajustando la división silábica o configurando el estilo de ruptura de URLs de `biblatex`.
* **Overfull `\vbox` en la maquetación**:
  * Ocurre al encajar imágenes de gran tamaño en ciertas páginas (como en las páginas de figuras dobles).
  * **Solución**: Disminuir ligeramente la escala (`width`) de las imágenes o usar `\vspace` negativos para ajustar las distancias.

---

## 2. Conclusión de Compilación

El documento compila limpiamente y todas las referencias cruzadas y bibliografía se enlazan de manera robusta.
