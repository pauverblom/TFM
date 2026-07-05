# Reporte de Revisión Formal y Estilística
Este documento presenta la evaluación y propuestas de mejora para el capítulo de la tesis de maestría (TFM) ubicado en [Hidrodinámica y Oscilaciones Estelares.tex](file:///home/pauver/repos/pauverblom/TFM/TeX/Cap%C3%ADtulos/Hidrodin%C3%A1mica%20y%20Oscilaciones%20Estelares.tex).

---

### 1. Formato y Sintaxis LaTeX

*   **Uso obsoleto de delimitadores para ecuaciones en bloque (`$$` en lugar de `\[ ... \]`):**
    *   **Líneas 87, 120, 217, 237, 245, 252, 256:** Se emplean los símbolos de doble dólar (`$$`) para introducir ecuaciones en bloque (display math).
    *   *Explicación:* En LaTeX2e moderno, el uso de `$$` está desaconsejado ya que altera el espaciado vertical automático de los párrafos y puede causar conflictos con diversos paquetes y clases de documentos. Debe reemplazarse sistemáticamente por la sintaxis estándar `\[ ... \]`.
*   **Fórmulas matemáticas mal delimitadas o con llaves incorrectas:**
    *   **Línea 19:** `$\mathbf{v(\mathbf{r}, t)} = \frac{d \mathbf{r}}{d t}$.`
        *   *Explicación:* El uso de la negrita `\mathbf` envuelve los paréntesis y a la variable temporal $t$, haciendo que estos se rendericen incorrectamente en negrita. Además, es inconsistente con el formato de la línea 6 ($\mathbf{v}(\mathbf{r}, t)$). Debe cambiarse a: `$\mathbf{v}(\mathbf{r}, t) = \frac{d \mathbf{r}}{d t}$.`
    *   **Línea 87:** `p_0({\mathbf{r_0}})`
        *   *Explicación:* Se utilizan llaves `{...}` en lugar de paréntesis `(...)` para denotar la dependencia de la variable espacial, lo cual rompe la consistencia física y sintáctica. Debe cambiarse a `p_0(\mathbf{r}_0)`.
*   **Uso incorrecto de comandos de negrita en letras griegas:**
    *   **Línea 138:** `\mathbf{\delta r}` y `\mathbf{\xi_h}`
        *   *Explicación:* El comando `\mathbf` no tiene efecto sobre caracteres griegos (como `\delta` o `\xi`) en las fuentes matemáticas estándar de LaTeX, lo que puede causar que no se muestren o se muestren en formato normal sin negrita. Para vectorizar letras griegas de manera correcta, debe emplearse el comando `\boldsymbol` de `amsmath`/`amsbsy` (o `\bm` si se usa el paquete `bm`), tal y como se hace en la línea 144 (`\boldsymbol{\xi}_h`).
*   **Variables y expresiones matemáticas en texto plano (fuera de modo matemático):**
    *   **Líneas 219 y 224 (múltiples apariciones):** La función de dispersión `K(r)` y sus relaciones `K(r) > 0`, `K(r) < 0` y `K(r) = 0` se encuentran escritas directamente en texto plano. Deben encerrarse en delimitadores matemáticos: `$K(r)$`, `$K(r) > 0$`, `$K(r) < 0$` y `$K(r) = 0$`.
    *   **Línea 229:** La fracción de hidrógeno `X_H=0.4` y `X_H=0.05` debe ir en modo matemático: `$X_{\text{H}} = 0.4$` y `$X_{\text{H}} = 0.05$`. Asimismo, "eje x" debe corregirse a "eje $x$".
    *   **Línea 239:** "velocidad del sonido c" debe corregirse a "velocidad del sonido $c$".
    *   **Línea 245:** "se identifica de forma natural con K:" debe corregirse a "se identifica de forma natural con $K$:".
*   **Sintaxis incorrecta en el formateo de unidades de frecuencia:**
    *   **Línea 263:** `3038.0\mu$Hz`, `2939.2\mu$Hz`, `3043.2\mu$Hz`, `109.2\mu$Hz`, `102.6\mu$Hz` y `104.1\mu$Hz`.
        *   *Explicación:* El comando de la letra griega `\mu` está colocado fuera del entorno matemático (antes del primer `$`). Esto causa un error crítico de compilación en LaTeX ("*Missing $ inserted*") a menos que se defina explícitamente en modo texto. Además, no se incluye espaciado fino entre el número y la unidad. Se debe corregir a: `3038.0\,\mu\text{Hz}$` o, mejor aún, utilizar el paquete estándar `siunitx` escribiendo `\qty{3038.0}{\micro\hertz}`.
*   **Uso incorrecto de comandos de formato de texto en fórmulas:**
    *   **Línea 56:** `$T/\textit{Periodo de Oscilación}$`
        *   *Explicación:* El uso de `\textit` dentro de fórmulas matemáticas para escribir frases completas provoca que LaTeX no respete el espaciado correcto entre palabras. Se debe utilizar el comando `\text` del paquete `amsmath`: `$T/\text{período de oscilación}$`.
*   **Línea de definición flotante y huérfana:**
    *   **Línea 132:** `siendo $\mathbf{g}' = - \nabla \Phi'$`
        *   *Explicación:* Esta línea aparece aislada e insertada de manera abrupta tras la ecuación de la línea 127 y el párrafo descriptivo de la línea 130. Debe reubicarse inmediatamente debajo de la ecuación donde se introduce el vector $\mathbf{g}'$ por primera vez (Línea 114) y agregar el punto final correspondiente.
*   **Líneas en blanco incorrectas antes de textos explicativos subordinados:**
    *   **Líneas 26, 34, 42, 49, 131, 156, 170, 212, 218:** Existen líneas vacías en el código de origen antes de conjunciones o adverbios explicativos en minúsculas (como "donde", "siendo", "notando", "y"). En LaTeX, una línea vacía representa un cambio de párrafo (`\par`), lo cual añade una sangría indeseada y rompe la continuidad visual y gramatical del texto. Se deben eliminar estas líneas en blanco.

---

### 2. Ortografía, Gramática y Puntuación en Español

*   **Uso de guiones e inconsistencias en términos compuestos:**
    *   **Líneas 138, 173:** `fluido-dinámicas`
        *   *Explicación:* De acuerdo con las normas de la Real Academia Española (RAE), los términos compuestos formados por dos adjetivos o un sustantivo y adjetivo plenamente integrados deben escribirse sin guión intermedio. Se debe corregir a `fluidodinámicas`.
*   **Falta de tildes y mayúsculas inapropiadas:**
    *   **Línea 56:** `Periodo` debe cambiarse a `período` (con tilde y en minúscula).
*   **Preposiciones incorrectas o giros poco naturales:**
    *   **Línea 3:** `se sustenta bajo las ecuaciones` -> La preposición correcta que rige el verbo "sustentarse" es *en*. Se debe corregir a: `se sustenta en las ecuaciones`.
    *   **Línea 3:** `bajo el marco de la astrosismología` -> Es más natural y común en español académico decir `en el marco de la astrosismología`.
    *   **Línea 35:** `la gravitatoria es la única fuerza externa` -> El adjetivo "gravitatoria" no puede sustantivarse directamente de esta forma. Debe cambiarse a `la gravedad` o `la fuerza gravitatoria`.
    *   **Línea 197:** `empalmando con el vacío exterior` -> El gerundio de posterioridad "empalmando" es incorrecto. Se debe sustituir por `al empalmar con el vacío exterior` o `para su acoplamiento con el vacío exterior`.
*   **Uso incorrecto del gerundio adjetival (anglicismo patente):**
    *   **Línea 6:** `correspondiéndose con lo que vería...`
        *   *Explicación:* El gerundio en español no puede funcionar como adjetivo especificativo que califica a un sustantivo ("descripción"). Se debe reescribir como: `descripción Euleriana del fluido, la cual se corresponde con lo que vería...` o `..., que se corresponde con...`.
*   **Discordancia de género o ambigüedad sintáctica:**
    *   **Líneas 249-250:** `Modos de Gravedad (g-modes) Corresponden a la rama de bajas frecuencias, encontradas en el interior profundo...`
        *   *Explicación:* Si el participio "encontradas" refiere a "frecuencias", la frase resulta extraña, ya que son los modos de gravedad los que se localizan en el interior profundo. Se recomienda reescribir para evitar ambigüedad: `... de bajas frecuencias, cuyos modos se localizan en el interior profundo estelar...`.
*   **Redacciones redundantes o lenguaje informal:**
    *   **Línea 3:** `Es la base matemática...` -> El inicio del párrafo habla de "las ecuaciones" (plural) y este enunciado carece de sujeto explícito inmediato. Se sugiere reescribir: `Esta aproximación proporciona la base matemática ideal...`.
    *   **Línea 50:** `donde $c_p$ es la capacidad calorífica a presión constante, $a$ la constante de densidad de radiación...` -> Falta el verbo copulativo en las cláusulas coordinadas. Debe cambiarse a: `donde $c_p$ es la capacidad..., $a$ es la constante..., $\tilde{c}$ es la velocidad...`.
    *   **Línea 56:** `ocurren muchísimo más rápido` -> La palabra "muchísimo" resulta excesivamente coloquial para el registro científico. Se propone: `ocurren a escalas de tiempo significativamente menores que aquellas asociadas a la transferencia térmica...`.
    *   **Línea 83:** `en un punto en concreto` -> Redundancia. Cambiar a `en un punto concreto` o `en un punto específico`.
    *   **Línea 96:** Se presenta una sola oración de 55 palabras que encadena cinco gerundios (`Sustituyendo... asumiendo... despreciando... e integrando... asumiendo... se obtiene`). Es estilísticamente densa y confusa. Se propone dividirla:
        *   *Propuesta de redacción:* `Si se sustituyen estas expresiones en las ecuaciones de la hidrodinámica y se asume un estado de equilibrio estático ($\mathbf{v}_0 = 0$ y $\partial \rho_0 / \partial t = 0$), se pueden despreciar los términos de segundo orden o superiores. De este modo, integrando respecto al tiempo bajo la hipótesis de perturbaciones iniciales nulas, se obtiene la forma euleriana...`
    *   **Línea 109:** `un elemento de fluido del gas` -> Expresión redundante. Cambiar a `un elemento de fluido`.
    *   **Línea 191:** `al tratar con un sistema diferencial...` -> Sujeto tácito incoherente (anacoluto). Se sugiere: `dado que se trata de un sistema diferencial de cuarto orden, es imperativo establecer...`.
    *   **Línea 229:** `...la frecuencia mínima a la cual se pueden propagar los modos p está determinada por la frecuencia crítica... en las capas exteriores` -> Se repite "en las capas exteriores" al principio y al final del mismo enunciado. Debe eliminarse la redundancia final.
*   **Falta de puntuación al final de ecuaciones en bloque y listas:**
    *   *Explicación:* Las ecuaciones en bloque forman parte gramatical de la oración y deben llevar el signo de puntuación correspondiente (punto o coma) en su extremo derecho.
    *   **Líneas 87, 106, 120, 127, 221, 237, 241, 245, 252, 256:** Falta añadir un punto final (`.`) al concluir la frase.
    *   **Línea 201:** El ítem final de la lista termina en la expresión `\sigma^{-2}` y carece de punto final.

---

### 3. Citaciones y Referencias Cruzadas

*   **Referencias estáticas (Hardcoded):**
    *   **Línea 229:** Se incluye la referencia en texto plano `en Fig. 1` (dos veces). En LaTeX, esto es propenso a errores. Debe ser reemplazado por referencias dinámicas con el comando `\ref{fig:NombreEtiqueta}`.
*   **Falta de etiquetas (`\label`) en entornos flotantes:**
    *   **Líneas 8-12 (Figura 1):** El entorno `figure` carece del comando `\label`. Es imposible citar esta figura dinámicamente. Se sugiere añadir `\label{fig:euler_lagrange}`.
    *   **Líneas 159-163 (Figura 2):** Tampoco dispone de `\label`. Se sugiere añadir `\label{fig:spherical_harmonics}`.
*   **Inconsistencias en las leyendas de figuras:**
    *   **Línea 162:** `los armónicos esféricos $Y_m^l$`
        *   *Explicación:* En el texto se definen como $Y_l^m$ (Línea 154 y 168). El intercambio de los índices $l$ (grado) y $m$ (orden azimutal) en la leyenda constituye una contradicción técnica. Se debe corregir a `$Y_l^m$`.
*   **Etiquetas huérfanas:**
    *   El archivo define abundantes etiquetas para sus fórmulas (como `\label{eq:continuidad}`, `\label{eq:continuidad_linealizada_euleriana}`, etc.) pero no se realiza ninguna llamada mediante `\ref` a lo largo de todo el texto del capítulo.

---

### 4. Revisión de Estilo Impersonal

El capítulo mantiene una redacción pasiva e impersonal muy sólida y bien ejecutada a través de la pasiva refleja en español (por ejemplo, `se consideran`, `se obtiene`). No se localizan pronombres directos (*nosotros*, *nuestro*, *nuestros*, *nuestra*, *nuestras*, *nos*) ni formas verbales explícitas de primera persona del plural (*hemos*, *observamos*, *esperamos*). 

Sin embargo, existen algunas construcciones que, por el uso de gerundios activos o infinitivos personales implícitos, debilitan ligeramente el rigor del estilo impersonal de la prosa académica. A continuación se detallan estas ocurrencias y las propuestas de reescritura:

*   **Línea 19:** `notando que $\mathbf{v(\mathbf{r}, t)} = \frac{d \mathbf{r}}{d t}$.`
    *   *Crítica:* El gerundio activo "notando" presupone un sujeto implícito en primera persona que realiza la acción de notar.
    *   *Propuesta de cambio:* `donde se cumple que $\mathbf{v}(\mathbf{r}, t) = \frac{d \mathbf{r}}{d t}$.`
*   **Línea 96:** `Sustituyendo estas expresiones..., asumiendo que..., despreciando términos..., e integrando...`
    *   *Crítica:* El encadenamiento de gerundios instrumentales activos simula una narración en primera persona del procedimiento llevado a cabo por el autor.
    *   *Propuesta de cambio:* `Tras la sustitución de estas expresiones en las ecuaciones de la hidrodinámica, si se asume un estado de equilibrio estático ($\mathbf{v}_0 = 0$ y $\partial \rho_0 / \partial t = 0$) y se desprecian los términos de segundo orden o superiores, la integración respecto al tiempo (bajo la hipótesis de perturbaciones iniciales nulas) conduce a la forma euleriana...`
*   **Línea 118:** `Trabajando con las perturbaciones lagrangianas... y aproximando la derivada material..., se obtiene...`
    *   *Crítica:* Nuevamente, "Trabajando" y "aproximando" expresan una acción directa y personal del investigador.
    *   *Propuesta de cambio:* `Al emplear las perturbaciones lagrangianas $\delta p$ y $\delta \rho$ y aproximar la derivada material por la derivada temporal (debido a que $\mathbf{v}_0$ es nula), la integración del sistema proporciona:`
*   **Línea 124:** `Sustituyendo el resultado... y empleando la relación geométrica...`
    *   *Crítica:* Estructura de gerundios activos.
    *   *Propuesta de cambio:* `Al sustituir el resultado de la ecuación de continuidad lagrangiana... y emplear la relación geométrica...`
*   **Línea 138:** `Al separar el vector desplazamiento... se proyectan... Aplicando el gradiente...`
    *   *Crítica:* El gerundio "Aplicando" introduce una acción activa del sujeto en la explicación.
    *   *Propuesta de cambio:* `Mediante la separación del vector desplazamiento... se proyectan... Al aplicar el gradiente y la divergencia en coordenadas esféricas...`
*   **Línea 173:** `Sustituyendo estas formas separadas..., recordando que..., y eliminando..., el problema se transforma... Suprimiendo la tilde...`
    *   *Crítica:* Acumulación de gerundios activos que describen los pasos seguidos por el autor.
    *   *Propuesta de cambio:* `La inserción de estas formas separadas en el sistema de ecuaciones fluidodinámicas, junto con la propiedad del operador laplaciano sobre los armónicos esféricos... y la eliminación de la perturbación de densidad..., transforma el problema en un sistema de ecuaciones diferenciales... Si se suprimen la tilde y el subíndice "0"...`
*   **Línea 187:** `de haber asumido simetría esférica`
    *   *Crítica:* El infinitivo compuesto "haber asumido" connota una acción en el pasado llevada a cabo por el escritor.
    *   *Propuesta de cambio:* `de la hipótesis de simetría esférica...` o `de la asunción de simetría esférica...`.
*   **Línea 216:** `Despreciando las derivadas de estas últimas, el sistema anterior se combina...`
    *   *Crítica:* El gerundio instrumental "Despreciando" atribuye la acción al autor de forma implícita.
    *   *Propuesta de cambio:* `Si se desprecian las derivadas de estas últimas, el sistema anterior se combina...`
