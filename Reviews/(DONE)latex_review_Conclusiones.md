Este informe presenta los resultados de la revisión formal, ortotipográfica y estilística del archivo [Conclusiones.tex](file:///home/pauver/repos/pauverblom/TFM/TeX/Cap%C3%ADtulos/Conclusiones.tex).

---

### 1. Formato y Sintaxis LaTeX

*   **Error de compilación por sintaxis matemática fuera de entorno matemático (Línea 176):**
    *   **Texto actual:** `los valores de (n_{pg}, l) a cada pico.`
    *   **Explicación:** Se utiliza el guion bajo (`_`) propio de los subíndices de LaTeX fuera del modo matemático, lo que provocará un error de compilación (`Missing $ inserted`). Debe envolverse en modo matemático y formatear adecuadamente el subíndice de texto.
    *   **Propuesta de corrección:** `los valores de $(n_{\text{pg}}, l)$ a cada pico.`
*   **Variables y números cuánticos en modo texto (Línea 149):**
    *   **Texto actual:** `sus números cuánticos n,l,m) resulta`
    *   **Explicación:** Las variables y números cuánticos deben representarse siempre en modo matemático (cursiva) para cumplir con el estándar académico.
    *   **Propuesta de corrección:** `sus números cuánticos $n, l, m$) resulta`
*   **Formato de subíndices de texto en modo matemático (Líneas 35, 41, 75 y 77):**
    *   **Texto actual:** `T_{int}`
    *   **Explicación:** La abreviatura "int" (de integración) no es una variable matemática, sino una etiqueta textual. En modo matemático, las letras se formatean individualmente con espaciado de variables ($i \times n \times t$). Debe usarse `\text{int}` o `\mathrm{int}` para que se renderice en fuente romana y vertical.
    *   **Propuesta de corrección:** Cambiar `T_{int}` por `T_{\text{int}}` (o `T_{\mathrm{int}}`) en todas sus apariciones.
*   **Representación de modos espectrales en texto plano (Líneas 23, 138, 151 y 153):**
    *   **Texto actual:** `modos g`, `modos p`
    *   **Explicación:** En astrosismología, las clases de modos de oscilación ($g$ para gravedad y $p$ para presión) deben denotarse con su variable matemática correspondiente en cursiva.
    *   **Propuesta de corrección:** Reemplazar por `modos $g$` y `modos $p$`.
*   **Uso de comandos matemáticos en títulos de sección (Línea 143):**
    *   **Texto actual:** `\section{Identificación de Modos en las $\boldsymbol{\delta}$ Scuti}`
    *   **Explicación:** Introducir comandos matemáticos complejos como `\boldsymbol{\delta}` en títulos de secciones puede generar advertencias o fallos si se utiliza el paquete `hyperref` para generar los marcadores del PDF. Se recomienda usar `\texorpdfstring` para proveer una alternativa en texto plano.
    *   **Propuesta de corrección:** `\section{Identificación de Modos en las \texorpdfstring{$\boldsymbol{\delta}$}{\textdelta} Scuti}`
*   **Comandos `\protect` redundantes en leyendas (Líneas 69, 106 y 129):**
    *   **Texto actual:** `$T_{\protect\min}$`, `|\Delta(\nu)|_{\protect\max}`, `|\Delta(\Delta\nu)|_{\protect\max}`, `|\Delta(\delta\nu_{02})|_{\protect\max}`
    *   **Explicación:** En versiones modernas de LaTeX, los operadores matemáticos estándar como `\min` y `\max` son robustos y no requieren protección mediante `\protect` dentro de los argumentos de `\caption`. Además, en la línea 69, `|\Delta(\nu)|` debería escribirse de forma más consistente con el resto del texto como `|\Delta\nu|` (o `|\Delta\nu_{\text{ind}}|` si se refiere a diferencias de frecuencias individuales).
    *   **Propuesta de corrección:** Reemplazar por `$T_{\min}$` y `|\Delta\nu|_{\max}`.
*   **Espacios duros ausentes antes de referencias cruzadas (Líneas 9 y 17):**
    *   **Texto actual:** `Figura \ref{fig:evolution_graphs}` (Línea 9) y `Figura \ref{fig:global_hr_diagram}` (Línea 17).
    *   **Explicación:** Se debe utilizar un espacio de no ruptura (`~`) en lugar de un espacio simple antes de `\ref` para evitar huérfanos (que el número de la figura aparezca al inicio de una línea nueva). En la línea 153 se usa correctamente (`Figura~\ref{fig:prop_bss}`).
    *   **Propuesta de corrección:** Reemplazar por `Figura~\ref{fig:evolution_graphs}` y `Figura~\ref{fig:global_hr_diagram}`.
*   **Espaciado inconsistente en modo matemático (Línea 79):**
    *   **Texto actual:** `$\Delta \nu$ o $\delta\nu_{02}$`
    *   **Explicación:** Se observa un espacio en `\Delta \nu` que no existe en el resto del manuscrito (`\Delta\nu`). Se recomienda unificar la sintaxis.
    *   **Propuesta de corrección:** Cambiar a `$\Delta\nu$`.

---

### 2. Ortografía, Gramática y Redacción en Español

*   **Uso del punto decimal en lugar de la coma decimal (Consistente en todo el documento):**
    *   **Líneas afectadas:** 9, 17, 21, 23, 27, 29, 60–66, 97–103, 120–126 y 168.
    *   **Explicación:** El manuscrito utiliza consistentemente el punto decimal en español (p. ej., `2.0`, `1.0`, `909.3`, `1.82136`, `69.7\%`, `0.1\%`, `2.491`, `88.5`, `0.4`, `0.8\%`, `2.75`, `3.21`, `0.08`, `1.2`, `3.25`). Según la normativa académica del español y la costumbre en las publicaciones técnicas en este idioma, el separador decimal recomendado es la coma (p. ej., `2,0`, `909,3`, `1,82136`). Se debe revisar si este criterio es uniforme con el resto de los capítulos de la tesis.
    *   **Propuesta de corrección:** Sustituir los puntos decimales por comas en todos los valores numéricos y tablas.
*   **Coma incorrecta entre sujeto y predicado (Línea 153):**
    *   **Texto actual:** `Este fenómeno (visible en la Figura~\ref{fig:prop_bss}), genera un espectro difícil de interpretar.`
    *   **Explicación:** La coma colocada inmediatamente después del paréntesis de cierre separa de forma incorrecta el sujeto de la oración ("Este fenómeno") de su verbo principal ("genera").
    *   **Propuesta de corrección:** Eliminar la coma: `Este fenómeno (visible en la Figura~\ref{fig:prop_bss}) genera un espectro difícil de interpretar.`
*   **Coma omitida tras adverbio introductorio (Línea 17):**
    *   **Texto actual:** `Además se ha observado`
    *   **Explicación:** En español, cuando un conector discursivo o adverbio como "Además" inicia una oración, debe ir seguido de coma.
    *   **Propuesta de corrección:** `Además, se ha observado`
*   **Comas incorrectas antes de la conjunción copulativa "y" (Líneas 11 y 15):**
    *   **Texto actual:**
        *   `...de oscilación, y poder determinar...` (Línea 11)
        *   `...dicho espectro de frecuencias, y se han empleado...` (Línea 15)
    *   **Explicación:** La coma delante de la conjunción "y" es incorrecta cuando une elementos que forman parte de la misma serie predicativa o comparten el mismo sujeto lógico sin ambigüedad.
    *   **Propuesta de corrección:** Eliminar la coma en ambos casos.
*   **Uso incorrecto del gerundio de posterioridad (Línea 136):**
    *   **Texto actual:** `...a menudo presentando ruido de fondo alto...`
    *   **Explicación:** El gerundio "presentando" indica una consecuencia o acción posterior al verbo principal "cumplen", lo cual es un uso incorrecto del gerundio en español. Debe redactarse como una oración de relativo o coordinada.
    *   **Propuesta de corrección:** `...las cuales a menudo presentan un nivel elevado de ruido de fondo...`
*   **Anglicismo terminológico (Línea 170):**
    *   **Texto actual:** `división de los modos en multiplets debido`
    *   **Explicación:** "Multiplets" es un término en inglés. En la literatura astrofísica en español se utiliza la palabra adaptada "multipletes".
    *   **Propuesta de corrección:** Reemplazar por `división de los modos en multipletes debido`.
*   **Redundancias y repeticiones de vocabulario:**
    *   **Línea 3:** `En este trabajo se ha llevado a cabo un trabajo...` -> Repetición inmediata de la palabra "trabajo". *Propuesta:* `En este estudio se ha desarrollado un marco teórico y computacional...`
    *   **Línea 11:** `...con el fin de emplearlas para comparar...` -> El verbo "emplearlas" es redundante con "empleado" al inicio de la frase. *Propuesta:* `...con el fin de comparar...`
    *   **Línea 15:** `...no ha sido necesario calcular dicho espectro de frecuencias, y se han empleado directamente estas frecuencias.` -> Repetición de la palabra "frecuencias". *Propuesta:* `...no ha sido necesario calcular dicho espectro, utilizándose directamente los valores obtenidos por GYRE.`
    *   **Línea 138:** `...requiere de una muy alta resolución...` -> El verbo "requerir" es transitivo en este contexto; el uso de la preposición "de" es superfluo. *Propuesta:* `...requiere una resolución muy alta...`
    *   **Línea 141:** `...que es el hecho de que, a día de hoy, no existe...` -> Expresión muy prolija y uso de la locución coloquial "a día de hoy". *Propuesta:* `...consistente en que, en la actualidad, no existe...`
    *   **Línea 159:** `...limpiar el espectro de frecuencias de frecuencias espurias...` -> Cacofonía por repetición de "frecuencias". *Propuesta:* `...limpiar el espectro de señales espurias...`
    *   **Línea 168:** `...de que el método propuesto pueda ser capaz de distinguir...` -> Redundancia semántica ("pueda ser capaz"). *Propuesta:* `...de que el método propuesto permita distinguir...`
*   **Presencia de texto provisional (Keyboard Smash / Placeholder) (Línea 11):**
    *   **Texto actual:** `Además, se ha empleado el repositorio \texttt{wsssss} para simular...`
    *   **Explicación:** El nombre del repositorio `wsssss` parece un marcador de posición de teclado provisional y carece de sentido científico. Se debe sustituir por el nombre real del repositorio o código utilizado.

---

### 3. Citas y Referencias Cruzadas

*   **Cita no resuelta (Placeholder) (Línea 136):**
    *   **Texto actual:** `\citep{CITAR}`
    *   **Explicación:** Se ha dejado la clave genérica `CITAR`. Esto provocará una advertencia de BibTeX/biber y se mostrará como un signo de interrogación `[?]` en el documento final. Debe sustituirse por la clave bibliográfica del trabajo correspondiente al criterio de Rayleigh.
*   **Clave de cita con formato de DOI (Líneas 145, 151, 159, 161 y 170):**
    *   **Texto actual:** `\citep{..., 10.3389/fspas.2022.952296}`
    *   **Explicación:** Aunque técnicamente compila en algunos entornos, usar el número DOI como clave de citación en el archivo `.bib` no es una buena práctica y puede dar problemas de lectura con ciertos caracteres (como los puntos y barras). Se aconseja modificar la clave en el archivo bibliográfico por una estándar (p. ej., `Fspas2022`).
*   **Posible errata en clave de cita (Línea 151):**
    *   **Texto actual:** `\citep{Handler_2009,Gatuam_2026}`
    *   **Explicación:** La clave `Gatuam_2026` parece contener una errata en el nombre del autor principal, que probablemente sea "Gautam" (un apellido de uso común en esta área de investigación). Se recomienda verificar el archivo `.bib`.

---

### 4. Control de Estilo Impersonal

*   **Evaluación:** Se ha realizado un escaneo completo y minucioso de todo el texto del capítulo en busca de pronombres personales de primera persona del plural (`nosotros`, `nos`, `nuestro`, `nuestros`, `nuestra`, `nuestras`) y de formas verbales conjugadas en primera persona del plural (`hemos`, `observamos`, `esperamos`, `concluimos`, `calculamos`, `analizamos`, `obtenemos`, `simulamos`, etc.).
*   **Resultado:** **0 ocurrencias detectadas.**
*   **Valoración:** El capítulo cumple estrictamente con el requisito de estilo académico impersonal y pasiva refleja (`se ha simulado`, `se han comparado`, `se observa`, `se estimará`, `se obtienen`, etc.). No se requiere ninguna reescritura por este concepto.
