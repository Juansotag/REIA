# **REIA: Realimentación Estudiantil con Inteligencia Artificial**
### **Documento Maestro de Especificación Técnica, Funcional y de Arquitectura**
**GovLab — Universidad de la Sabana**  
*Versión 1.0 — Documento de Definición Total*

---

## **1. Resumen Ejecutivo y Ficha Técnica**

| Atributo | Detalle |
| :--- | :--- |
| **Nombre del Proyecto** | REIA (*Realimentación Estudiantil con Inteligencia Artificial*) |
| **Institución Desarrolladora** | GovLab — Universidad de la Sabana |
| **Ámbito de Aplicación** | Educación básica primaria, secundaria y media en Colombia (Grados 5.º a 11.º) |
| **Normativa Pedagógica** | Marco de evaluación formativa institucional y Decreto 1290 de 2009 (MEN Colombia) |
| **Tecnologías Principales** | Python 3.11+, FastAPI, HTMX, Jinja2, PostgreSQL (Railway), Vanilla CSS |
| **Motores de IA Soportados** | Dual configurable: **OpenAI** (GPT-4o / GPT-4o-mini) y **Anthropic** (Claude 3.5 Sonnet / Claude 3.5 Haiku) |
| **Speech-to-Text (STT)** | Híbrido: Web Speech API (transcripción nativa en vivo) + OpenAI Whisper (respaldo de alta fidelidad) |
| **Identidad Visual** | Manual de marca GovLab / UniSabana: Tipografías *Publico Banner* y *Libre Franklin*, paleta `#00135B`, `#f8a719`, `#96272D` |
| **Infraestructura y Despliegue** | Railway (FastAPI Service + Managed PostgreSQL) |
| **Privacidad de Datos** | Protocolo estricto *Zero-PII LLM* con anonimización en origen y tokenización local |

---

## **2. Filosofía, Propósito y Valor Pedagógico**

### **2.1. El Problema en el Contexto Escolar Colombiano**
En la educación básica y media colombiana, los docentes gestionan grupos numerosos (a menudo más de 30 a 40 estudiantes por aula, sumando entre 150 y 300 estudiantes a cargo). La evaluación formativa y cualitativa continua —esencial para orientar el aprendizaje, detectar rezagos tempranos y prevenir la deserción— se ve asfixiada por:
1. **Sobrecarga de digitación y tiempo administrativo**: Redactar observaciones individualizadas y detalladas de forma periódica resulta humanamente inviable en la jornada docente tradicional.
2. **Subjetividad y dispersión de criterios**: Dificultad para registrar y trazar observaciones diarias alineadas con rúbricas de competencias específicas.
3. **Riesgos de Habeas Data (Ley 1581 de 2012)**: El uso no regulado de herramientas comerciales de IA (como ChatGPT) por parte de profesores expone datos sensibles de menores de edad (nombres, diagnósticos de aprendizaje, conflictos de convivencia, situaciones familiares) a servidores de terceros sin consentimiento ni salvaguardas.

### **2.2. La Solución REIA**
REIA es una solución web ágil, segura y centrada en el docente que:
* Permite ingresar bitácoras de observación diaria mediante **voz natural (Speech-to-Text)** en un flujo "modo ráfaga" sin fricción.
* **Infiere automáticamente** sugerencias de calificación para rúbricas multidimensionales a partir de los comentarios orales o escritos.
* **Anonimiza de forma inviolable** la información sensible antes de que cualquier dato abandone el servidor local, reemplazando identificadores y nombres por variables genéricas.
* Proporciona **trazabilidad longitudinal** de cada estudiante y del grupo mediante análisis estadístico (series temporales, medias, medianas, cuartiles y diagramas de caja y bigotes).
* Redacta automáticamente **informes cualitativos de alto valor pedagógico** y genera entregables oficiales descargables en **Word (.docx)** y **PDF** listos para imprimir y firmar.

---

## **3. Protocolo de Privacidad y Anonimización (Zero-PII)**

La regla de oro de REIA es que **ningún proveedor de Inteligencia Artificial (OpenAI, Anthropic, etc.) jamás recibirá nombres, documentos de identidad ni información identificable de los menores**.

```mermaid
flowchart TD
    subgraph Cliente_Navegador ["Navegador Docente (Cliente)"]
        A[Docente dicta observación por voz] --> B[Texto en pantalla con Nombres Reales]
        B --> C[Detección de Compañeros: Chiclets Interactivos]
    end

    subgraph Backend_Local ["Backend Seguro FastAPI (Railway)"]
        C -->|Envío de reporte| D[Módulo de Anonimización y Sanitización]
        E[(PostgreSQL Privado)] <-->|Lectura Nombres / IDs| D
        D --> F[Texto Tokenizado: Estudiante -> ID_ANONIMO, Compañeros -> COMPANERO_N]
        F --> G[Llamada a API de LLM: OpenAI / Anthropic]
    end

    subgraph LLM_Cloud ["Nube del Proveedor de IA"]
        G --> H[Procesamiento y Redacción con Placeholders: NOMBRE_ESTUDIANTE, PRONOMBRE]
    end

    subgraph Renderizado_Local ["Backend / Reemplazo Local"]
        H -->|Respuesta del LLM| I[Motor de Reemplazo Local: Token Swapper]
        E -->|Datos Reales| I
        I --> J[Informe Final con Datos Reales: Web, Word .docx, PDF]
    end
```

### **3.1. Identificadores Anónimos**
* En la base de datos PostgreSQL, la tabla `estudiantes` resguarda de forma segura el nombre completo, documento de identidad (TI/CC), edad, género y curso.
* Cada estudiante cuenta con un identificador único opaco (`uuid_anonimo`, ej. `EST_7F8A9B2C`). Este es el único identificador que se utiliza en el contexto de procesamiento analítico.

### **3.2. Detección de Terceros y Componente de "Chiclets" en el Texto**
Cuando un docente registra un comentario que involucra a otros alumnos (por ejemplo: *"Se presentó un desacuerdo fuerte con Andrés y Mateo durante el trabajo en grupo"*):
1. El backend compara las palabras clave del texto contra la nómina de estudiantes del curso.
2. Si detecta coincidencias con nombres de la base de datos, en la interfaz web se renderizan **Chiclets (Tags Interactivos)** resaltados:
   * Cada chiclet muestra el nombre detectado con un selector rápido: `[Confirmar: Andrés Felipe Castro]`, `[Cambiar estudiante]` o `[Descartar / Nombre común]`.
3. Al persistir y enviar al LLM, el backend sustituye automáticamente los nombres confirmados por variables `[COMPANERO_1]`, `[COMPANERO_2]`.
4. De este modo, la IA comprende la dinámica social y relacional del evento sin saber quiénes son los involucrados.

### **3.3. Reemplazo Local de Placeholders (Token Swapper)**
Al momento de generar un informe consolidado:
1. El prompt enviado al LLM le ordena redactar usando exclusivamente las variables `[NOMBRE_ESTUDIANTE]` y `[PRONOMBRE]` (concordancia gramatical según género: él/ella, su/sus).
2. Cuando el LLM devuelve el informe redactado, el backend de FastAPI ejecuta una sustitución en memoria antes de almacenar el informe o renderizarlo:
   * `[NOMBRE_ESTUDIANTE]` $\rightarrow$ *Sofía Valentina Ramírez Gutiérrez*
   * `[PRONOMBRE]` $\rightarrow$ *ella* / *la estudiante*
   * `[COMPANERO_1]` $\rightarrow$ *Andrés Castro* (si es pertinente en el contexto del informe)
3. La información personal nunca se guardó en logs externos ni se usó para entrenar modelos.

---

## **4. Arquitectura del Sistema y Pila Tecnológica**

```mermaid
graph LR
    subgraph Frontend ["Capa Frontend (Lightweight & Reactive)"]
        UI[Jinja2 Templates]
        HTMX[HTMX 1.9+]
        CSS[Vanilla CSS - Manual GovLab]
        JS_STT[Web Speech API Audio Engine]
        JS_CHART[Chart.js Interactivo]
    end

    subgraph Backend ["Capa Backend (Python 3.11+ / FastAPI)"]
        API[FastAPI Routers]
        STT_ROUTER[Whisper Audio Service]
        LLM_SERVICE[LLM Factory: OpenAI / Anthropic]
        VIZ_SERVICE[Matplotlib / Seaborn Headless Engine]
        DOC_SERVICE[python-docx & WeasyPrint Generator]
        EXCEL_SERVICE[openpyxl / pandas Import-Export]
    end

    subgraph DataLayer ["Capa de Datos (Railway Cloud)"]
        PG[(PostgreSQL 16+ Relacional + JSONB)]
    end

    UI <--> HTMX
    HTMX <--> API
    JS_STT -->|Audio Blob| STT_ROUTER
    API --> LLM_SERVICE
    API --> VIZ_SERVICE
    API --> DOC_SERVICE
    API --> EXCEL_SERVICE
    API <--> PG
```

### **4.1. Especificación de Tecnologías**

* **Backend**: **FastAPI** (Python 3.11+). Aprovecha la concurrencia nativa asíncrona (`asyncio`), inyección de dependencias y validación estricta con **Pydantic v2**.
* **Frontend y Reactividad**: **Jinja2 + HTMX**.
  * Permite una experiencia de usuario tipo Single-Page Application (SPA) con transiciones suaves y modales, sin el peso ni la fragilidad de frameworks JS complejos como React o Angular.
  * Todas las interacciones del "Modo Ráfaga" y filtros de gráficos operan mediante swaps parciales del DOM (`hx-post`, `hx-target`, `hx-swap="outerHTML"`).
* **Motor de Estilos (CSS)**: Vanilla CSS estructurado a partir del archivo maestro `style.css` del GovLab. Cumple 100% las directrices institucionales de la Universidad de la Sabana.
* **Persistencia**: **PostgreSQL** alojado en Railway. Utiliza un esquema híbrido altamente optimizado: tablas fuertemente normalizadas para el modelo relacional institucional y campos `JSONB` indexados con GIN para la flexibilidad de rúbricas y reportes.
* **Motor Dual de LLM**:
  * Implementación mediante patrón *Strategy/Factory*:
    * `OpenAIService`: Integración oficial con la librería `openai` (GPT-4o, GPT-4o-mini).
    * `AnthropicService`: Integración oficial con `anthropic` (Claude 3.5 Sonnet, Claude 3.5 Haiku).
  * Conmutador en caliente en la pestaña de Configuración sin necesidad de reiniciar el servicio.
* **Speech-to-Text Híbrido**:
  * *Primario*: `webkitSpeechRecognition` / Web Speech API en el navegador para transcripción instantánea palabra por palabra sin costo ni consumo de cuota de red.
  * *Secundario / Respaldo*: Grabación con `MediaRecorder` a formato `audio/webm` o `audio/wav` enviado a `/api/stt/transcribe` para procesamiento con OpenAI Whisper en caso de navegadores móviles o aulas con ruido ambiental.
* **Motor Gráfico Dual**:
  * *En la Web*: **Chart.js 4.x** para visualización dinámica, tooltips interactivos, visualización de cuartiles y leyendas configurables.
  * *En Documentos*: **Matplotlib / Seaborn** ejecutados en headless backend (`Agg`), generando imágenes PNG de 300 DPI con la paleta de colores institucional para incrustar directamente en Word y PDF.
* **Generación Documental**:
  * Formato Word: `python-docx` con estilos de encabezado institucional, fuentes del sistema y tablas formateadas.
  * Formato PDF: Motor HTML-to-PDF mediante `WeasyPrint` con hojas de estilo específicas `@media print`.
* **Procesamiento de Archivos**: `openpyxl` y `pandas` para importación y exportación masiva de estudiantes en formato Excel (.xlsx) y CSV.

---

## **5. Sistema de Diseño e Identidad Visual (GovLab — UniSabana)**

La interfaz de REIA respeta rigurosamente el manual de identidad visual institucional definido en `style.css`.

### **5.1. Paleta de Colores**
* **Azul Oscuro Institucional (`--c-blue-dark: #00135B`)**: Color primario. Usado en barra de navegación principal, encabezados principales, botones primarios y líneas base de gráficos.
* **Azul Hover (`--c-blue-hover: #000e42`)**: Estados activos y hover de botones principales.
* **Azul Interacción (`--c-blue-light: #00387D`)**: Enlaces, focus de inputs y bordes activos.
* **Azul Suave (`--c-blue-soft: #93AAC9`)**: Botones secundarios y elementos complementarios.
* **Tinte Azul (`--c-blue-tint: #D9E1EF`)**: Bordes de tarjetas, fondos de tablas, separadores y burbujas de rol.
* **Dorado / Amarillo Institucional (`--c-yellow: #f8a719`)**: Acentos, pills de navegación activos, bordes de elementos destacados y estados de mejora.
* **Crema Cálido (`--c-cream: #F7EFD9`)**: Fondos de advertencias pedagógicas y cajas de recomendaciones.
* **Rojo Institucional (`--c-red: #96272D`)**: Alertas, botón de grabación en vivo (con animación de pulso) y botones de eliminación.
* **Fondo Principal (`--bg-main: #EEF2F8`)**: Fondo neutro de alta legibilidad y confort visual.

### **5.2. Tipografía Institucional**
* **Títulos y Display**: `Publico Banner Light Italic` (`/static/fonts/PublicoBannerWeb-LightItalic_govlab.woff2`), con fallback a Playfair Display y Georgia. Empleada en `h1`, `h2`, tarjetas principales y títulos de métricas.
* **Texto de Contenido y Controles**: `Libre Franklin` (Google Fonts) / `Franklin Gothic` / `Segoe UI`. Empleada en cuerpos de texto, tablas, etiquetas de formularios y controles interactivos.

### **5.3. Elementos de Marca**
* Navbar sticky con el logotipo oficial `GovLab_blanco.png`, separador vertical blanco y subtítulo en *Publico Banner*.
* Píldoras de navegación (`.nav-pill`) con estado activo en amarillo `#f8a719` y texto azul `#00135B`.
* Tarjetas con sombras suaves (`--shadow: 0 2px 8px rgba(0, 19, 91, 0.10)`) que se elevan en hover.
* Animaciones de pulso para el botón de grabación y transiciones fluidas de entrada (`fadeSlideIn`).

---

## **6. Descripción Detallada de Módulos (Pestañas)**

```mermaid
graph TD
    M1[1. Estudiantes] --- M2[2. Cursos y Clases]
    M2 --- M3[3. Rúbricas]
    M3 --- M4[4. Reportes Bitácora Diaria]
    M4 --- M5[5. Informes Consolidados]
    M5 --- M6[6. Configuración Sistema]
```

---

### **6.1. Pestaña 1: Estudiantes**

Esta pestaña es el repositorio central de datos del alumnado y el único lugar donde reside información PII.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  GESTIÓN DE ESTUDIANTES                                       [+ Nuevo] [📥 Importar] [📤]   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  Filtros: [ Todos los Cursos ▼ ] [ Todas las Clases ▼ ]   Buscar: [_________________ 🔍]     │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  ID Privado │ Nombre Completo            │ Doc. Identidad │ Grado   │ Cursos     │ Acciones │
│  EST_001    │ Sofía Valentina Ramírez G. │ TI 1025847392  │ Noveno  │ 9º B       │ ✏️ 👁️ 🗑️ │
│  EST_002    │ Juan David Morales Castro  │ TI 1034928110  │ Décimo  │ 10º A      │ ✏️ 👁️ 🗑️ │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### **Funcionalidades Clave:**
1. **Nómina y Directorio**:
   * Listado paginado y filtrable por curso, clase, grado y término de búsqueda libre.
   * Visualización del identificador anónimo asignado (`uuid_anonimo`), nombre completo, número de documento de identidad (TI/CC), edad, grado, género (para deducción de pronombre él/ella) y cursos/clases matriculados.
2. **Creación y Edición (Modal HTMX)**:
   * Formulario modal para crear o editar un estudiante.
   * Campos: Nombres, Apellidos, Tipo de Documento, Número de Documento, Fecha de Nacimiento / Edad, Género, Acudiente de Contacto (opcional), Asignación de Cursos y Clases.
3. **Carga Masiva (Importación Excel/CSV)**:
   * Zona de arrastrar y soltar archivos `.xlsx` o `.csv`.
   * Mapeo inteligente de columnas con previsualización de datos antes de confirmar la inserción en base de datos.
   * Detección y manejo de registros duplicados por documento de identidad.
4. **Exportación de Nómina**:
   * Descarga instantánea de la lista completa o filtrada en Excel y CSV.

---

### **6.2. Pestaña 2: Cursos y Clases**

Permite estructurar la oferta académica de la institución educativa.

#### **Definición de Conceptos en REIA:**
* **Clases**: Asignaturas o materias curriculares específicas impartidas por los docentes (ejemplos: *Matemáticas*, *Ciencias Sociales*, *Lengua Castellana*, *Química*, *Inglés*, *Educación Física*).
* **Cursos**: Grados y secciones que agrupan a los estudiantes como cohorte escolar (ejemplos: *Cuarto A*, *Séptimo B*, *Noveno B*, *Décimo A*, *Once C*).

#### **Funcionalidades Clave:**
1. **Gestor de Cursos**:
   * Creación de cursos con especificación de Grado (5º a 11º), Sección (A, B, C), Año Lectivo y Director de Curso.
   * Vista detallada de la nómina de estudiantes adscritos al curso.
   * Posibilidad de añadir o remover estudiantes en bloque.
2. **Gestor de Clases**:
   * Creación de asignaturas con Código, Área de Conocimiento e Intensidad Horaria.
   * Asignación de clases a cursos específicos o a estudiantes individuales.
3. **Matriz de Asignaciones**:
   * Interfaz interactiva para vincular qué cursos tienen qué clases y verificar la cobertura académica.

---

### **6.3. Pestaña 3: Rúbricas**

Las rúbricas son el instrumento psicométrico y pedagógico que da rigor a las observaciones cualitativas.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  RÚBRICA: Competencias de Razonamiento Matemático (7º a 9º)                  [Guardar]      │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  DIMENSIÓN 1: Pensamiento Lógico y Estructurado               Peso: [35%]                   │
│  Escala: Continua de 0.0 a 5.0                                                               │
│  [0.0 - 2.9] Bajo: Presenta dificultades severas para estructurar secuencias deductivas.     │
│  [3.0 - 3.9] Básico: Aplica secuencias lógicas básicas pero con tropiezos en abstracción.    │
│  [4.0 - 4.5] Alto: Desarrolla razonamientos sólidos y demuestra comprensión conceptual.     │
│  [4.6 - 5.0] Superior: Plantea soluciones originales y formula deducciones formales óptimas. │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  + Añadir Dimensión  │  + Nueva Rúbrica                                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### **Estructura de la Rúbrica en REIA:**
* **Metadatos**: Nombre de la rúbrica, descripción pedagógica, área o materia sugerida.
* **Dimensiones**: Cada rúbrica se compone de 1 a $N$ dimensiones (ej. *Pensamiento Lógico*, *Comunicación Escrita*, *Trabajo Colaborativo*, *Resolución de Problemas*).
* **Escala de Calificación**:
  * Rango numérico continuo de **0.0 a 5.0** (alineado al sistema de evaluación nacional en Colombia).
  * 4 tramos de desempeño oficiales (Decreto 1290):
    1. **Desempeño Bajo**: 0.0 – 2.9
    2. **Desempeño Básico**: 3.0 – 3.9
    3. **Desempeño Alto**: 4.0 – 4.5
    4. **Desempeño Superior**: 4.6 – 5.0
  * Cada tramo contiene una descripción cualitativa predeterminada que sirve como ancla semántica para que la IA interprete los comentarios del profesor.
* **Operaciones CRUD**: Clonar rúbricas existentes, exportar en formato JSON y asociar a materias específicas.

---

### **6.4. Pestaña 4: Reportes (Bitácora Diaria y Modo Ráfaga)**

Es el corazón operativo de la herramienta en el día a día del docente. Diseñada para registrar retroalimentaciones a la velocidad de la voz.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  MODO RÁFAGA: Matemáticas — Noveno B  │  Estudiante 12 de 32  │  [ Saltar / Omitir ]        │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  Estudiante Actual: Sofía Valentina Ramírez G. (9º B)                                      │
│  Rúbrica Activa: Habilidades Matemáticas 9º                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  [ 🎙️ GRABAR OBSERVACIÓN (Espacio para hablar) ]  ● Grabando...                             │
│  Transcripción en vivo:                                                                     │
│  "Hoy Sofía demostró gran agilidad resolviendo ecuaciones cuadráticas, pero se distrajo     │
│   un momento conversando con [Andrés Castro ✕] durante la explicación grupal."             │
│                                                                                             │
│  Sugerencia de IA para Rúbrica (Basada en audio):                                           │
│  * Pensamiento Lógico:     [ 4.5 ] Alto      (Click para ajustar: ──●──)                    │
│  * Atención y Convivencia: [ 3.5 ] Básico    (Click para ajustar: ──●──)                    │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  [ ⬅️ Anterior ]                                            [ 💾 Guardar y Siguiente ➡️ ]    │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### **Flujo de Trabajo del "Modo Ráfaga":**
1. **Configuración de la Sesión**:
   * El docente selecciona el Curso (ej. *Noveno B*), la Clase (ej. *Matemáticas*), la Fecha del día y la Rúbrica a evaluar (opcional o requerida, máximo 1 rúbrica por reporte).
2. **Ciclo por Estudiante (Secuencia sin Recargas)**:
   * La interfaz muestra la tarjeta del estudiante en turno (con su número de lista, nombre y grado).
   * **Entrada por Voz (STT)**:
     * El docente presiona el botón de micrófono (o la barra espaciadora como atajo de teclado).
     * El botón entra en estado animado de pulso rojo (`#96272D`).
     * La Web Speech API transcribe en tiempo real en la caja de texto. Si el docente finaliza, puede usar Whisper con un botón secundario para corregir cualquier término técnico.
   * **Detección de Compañeros (Chiclets)**:
     * Si la transcripción menciona a otro alumno, aparece automáticamente una pastilla interactiva (*chiclet*) para confirmar o anonimizar.
   * **Inferencia Inteligente de Rúbrica**:
     * Al pausar la voz o presionar "Interpretar Rúbrica", el LLM analiza la observación a la luz de las dimensiones y tramos de la rúbrica activa.
     * La IA pre-selecciona las calificaciones sugeridas (ej. 4.5 en Dimensión A, 3.5 en Dimensión B).
     * El docente tiene total control: puede aceptar las sugerencias o mover los sliders/botones en un clic.
   * **Avance Inmediato**:
     * Al presionar **"Guardar y Siguiente"** (o atajo `Ctrl + Enter`), el reporte se serializa a JSONB y se almacena en PostgreSQL mediante una llamada asíncrona de HTMX.
     * La interfaz reemplaza de forma fluida la tarjeta con el siguiente estudiante de la lista.
   * **Botón "Omitir"**:
     * Si un estudiante no asistió o no requiere observación ese día, el docente pulsa "Omitir" y pasa al siguiente sin crear registro.

#### **Estructura del Payload JSON del Reporte en Base de Datos:**
```json
{
  "reporte_id": "rep_9a8b7c6d-5e4f",
  "uuid_anonimo": "EST_7F8A9B2C",
  "curso_id": 4,
  "clase_id": 12,
  "fecha": "2026-03-24",
  "rubrica_id": 2,
  "texto_original_local": "Hoy Sofía demostró gran agilidad resolviendo ecuaciones cuadráticas...",
  "texto_anonimizado": "Hoy [ESTUDIANTE] demostró gran agilidad resolviendo ecuaciones cuadráticas, pero se distrajo un momento conversando con [COMPANERO_1]...",
  "calificaciones_dimensiones": {
    "dim_1_pensamiento_logico": 4.5,
    "dim_2_atencion_convivencia": 3.5
  },
  "metadata_adicional": {
    "metodo_entrada": "STT_NATIVO",
    "calificacion_asistida_por_ia": true,
    "ajustada_manualmente": false,
    "tiempo_grabacion_segundos": 14.2
  }
}
```

---

### **6.5. Pestaña 5: Informes (Consolidación, Gráficas y Exportación)**

Permite transformar semanas o meses de bitácoras dispersas en informes integrales, formativos y visualmente enriquecidos.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  GENERADOR DE INFORMES CONSOLIDADOS                                                         │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  Tipo: (●) Individual por Estudiante    ( ) Agregado por Curso / Clase                      │
│  Selección: [ Sofía Valentina Ramírez G. ▼ ]    Período: [ 2026-02-01 ] a [ 2026-06-30 ]    │
│  Clases: [☑ Matemáticas] [☑ Ciencias]     Rúbricas: [☑ Habilidades Matemáticas 9º]          │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  Instrucciones / Prompt para la IA:                                                         │
│  "Redactar un informe con tono pedagógico formativo y cercano, dirigido a los padres de     │
│   familia. Destacar las fortalezas en pensamiento lógico y proponer un plan de acción para  │
│   mejorar la concentración durante las actividades en equipo."                              │
│                                                                                             │
│  [ Plantillas Guardadas ▼ ]   [ 💾 Guardar como Modelo ]                                    │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  [ ⚡ Generar Vista Previa del Informe ]                                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### **6.5.1. Tipos de Informe:**
1. **Informe Individual**:
   * Centrado en la trayectoria formativa de un estudiante particular.
   * Agrupa todas las observaciones del período seleccionado para ese alumno.
   * Gráfica longitudinal con la evolución de cada dimensión evaluada.
   * Narrativa de la IA con análisis de fortalezas, áreas de oportunidad y recomendaciones concretas.
2. **Informe Colectivo / Agregado**:
   * Centrado en un Curso (ej. *Noveno B*) o una Clase específica (ej. *Ciencias Sociales 8º*).
   * Resume la tendencia general del grupo: desempeño promedio, dispersión del aprendizaje, tópicos de mayor dominio y retos colectivos.
   * Gráficas estadísticas con cajas y bigotes (Boxplots), medias y medianas.

#### **6.5.2. Especificación de Gráficas Estadísticas:**

##### **A. Gráfica Individual (Evolución de Líneas por Dimensión):**
* **Eje X**: Tiempo cronológico (agrupado por semanas o meses del año 2026).
* **Eje Y**: Escala de calificación oficial de la rúbrica (de `0.0` a `5.0`).
* **Series / Líneas**: Una línea de color diferenciado por cada dimensión de la rúbrica.
  * Los puntos representan las observaciones individuales registradas.
  * Línea de tendencia para identificar progreso o estancamiento.

```
Calificación (0-5)
  5.0 ┼                                      ●───● (Pensamiento Lógico)
  4.0 ┼                    ●─────────●───────
  3.0 ┼───────●───────────                    ●───● (Atención y Convivencia)
  2.0 ┼        \         /
  1.0 ┼         ●───────●
  0.0 ┼───┴─────────┴─────────┴─────────┴─────────┴─── Tiempo
       Feb 1     Feb 15    Mar 1     Mar 15    Abr 1
```

##### **B. Gráfica Agregada de Curso (Promedios, Medianas y Cajas y Bigotes):**
* Diseñada para mostrar la distribución real del curso sin enmascarar la dispersión.
* **Eje X**: Hitos temporales (semanas, quincenas o meses).
* **Eje Y**: Escala de 0.0 a 5.0.
* **Componentes por Punto Temporal**:
  1. **Caja y Bigotes (Boxplot)**:
     * Límite inferior del bigote: Valor mínimo o percentil 5.
     * Borde inferior de la caja: Primer cuartil ($Q_1$ o percentil 25).
     * Línea sólida central: **Mediana** ($Q_2$ o percentil 50).
     * Borde superior de la caja: Tercer cuartil ($Q_3$ o percentil 75).
     * Límite superior del bigote: Valor máximo o percentil 95.
  2. **Línea Punteada**: Evolución de la **Media Aritmética** grupal a lo largo del tiempo.
  3. En la interfaz web: Interactividad mediante Chart.js para ocultar dimensiones o inspeccionar datos atípicos (outliers) en hover.
  4. En exportaciones (Word/PDF): Gráfica generada en backend con `matplotlib.pyplot.boxplot` / `seaborn` con renderizado nítido a 300 DPI y la paleta de color institucional UniSabana.

#### **6.5.3. Guardado de Modelos de Informe (Plantillas):**
* Los docentes pueden guardar configuraciones recurrentes:
  * Ejemplo: *"Informe de Mitad de Trimestre para Padres de Familia"* (con su prompt base predefinido, rúbricas asociadas y filtros estándar).
  * Estas plantillas se guardan en la tabla `modelos_informe` y se pueden volver a disparar con un solo clic en fechas posteriores.

#### **6.5.4. Exportación Oficial (Word y PDF):**
Los documentos descargables cuentan con estructura editorial completa:
1. **Membrete Oficial**: Logotipo del GovLab y de la Universidad de la Sabana, nombre de la institución escolar, fecha de expedición y código de verificación.
2. **Ficha del Informe**: Nombre del estudiante (o curso), documento de identidad, grado, materias evaluadas y período de corte.
3. **Resumen Ejecutivo de la IA**: Síntesis cualitativa redactada con tono profesional, estructurada en:
   * *Fortalezas y Logros Destacados*.
   * *Aspectos Pedagógicos y Convivenciales por Fortalecer*.
   * *Recomendaciones y Plan de Acción Sugerido*.
4. **Gráfica Evolutiva Incrustada**: Gráfico de alta definición insertado en el cuerpo del documento.
5. **Tabla de Resumen de Rúbricas**: Matriz con los puntajes consolidados por dimensión y su descriptor cualitativo correspondiente.
6. **Espacio de Firmas**: Líneas de firma para el Docente Titular, Coordinador Académico y Orientador Escolar.

---

### **6.6. Pestaña 6: Configuración del Sistema**

Permite calibrar los motores de la herramienta para pruebas internas:
* **Selector de Proveedor LLM**: Alternar entre OpenAI (ej. `gpt-4o`, `gpt-4o-mini`) y Anthropic (ej. `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`).
* **Gestión de API Keys**: Configuración de llaves maestras (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) almacenadas de forma segura en variables de entorno de Railway.
* **Configuración de STT**: Opción de forzar Whisper en backend o permitir el STT nativo del navegador.
* **Parámetros de Temperatura y Tokens**: Ajustes para calibrar la creatividad o precisión analítica de los reportes.

---

## **7. Modelo de Base de Datos y Esquema Relacional (PostgreSQL)**

El esquema implementa un modelo **Híbrido Relacional + Documental (JSONB)** que garantiza integridad referencial estricta para la estructura escolar y máxima adaptabilidad para la evolución de rúbricas y reportes.

```mermaid
erDiagram
    ESTUDIANTES ||--o{ MATRICULAS_CURSO : tiene
    CURSOS ||--o{ MATRICULAS_CURSO : agrupa
    ESTUDIANTES ||--o{ MATRICULAS_CLASE : cursa
    CLASES ||--o{ MATRICULAS_CLASE : ofrece
    CURSOS ||--o{ CLASES_CURSO : incluye
    CLASES ||--o{ CLASES_CURSO : asignada

    RUBRICAS ||--|{ DIMENSIONES_RUBRICA : contiene
    
    ESTUDIANTES ||--o{ REPORTES : recibe
    CURSOS ||--o{ REPORTES : contextualiza
    CLASES ||--o{ REPORTES : pertenece
    RUBRICAS ||--o| REPORTES : evalua

    MODELOS_INFORME ||--o{ INFORMES_GENERADOS : parametriza
```

### **7.1. Especificación de Tablas Principales**

#### **1. Tabla `estudiantes`**
Almacena la identidad civil de los estudiantes (PII aislado).
```sql
CREATE TABLE estudiantes (
    id SERIAL PRIMARY KEY,
    uuid_anonimo VARCHAR(64) UNIQUE NOT NULL, -- Identificador opaco enviado al pipeline de IA
    tipo_documento VARCHAR(10) NOT NULL,      -- 'TI', 'CC', 'RC', 'NES'
    numero_documento VARCHAR(30) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    genero VARCHAR(20) NOT NULL,              -- 'Masculino', 'Femenino', 'Otro'
    pronombre VARCHAR(10) NOT NULL,           -- 'él', 'ella', 'elle' (para concordancia gramatical)
    fecha_nacimiento DATE,
    edad INT,
    grado_actual INT NOT NULL,                -- 5 a 11
    acudiente_nombre VARCHAR(150),
    acudiente_contacto VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_estudiantes_uuid ON estudiantes(uuid_anonimo);
CREATE INDEX idx_estudiantes_grado ON estudiantes(grado_actual);
```

#### **2. Tabla `cursos`**
Agrupaciones de grado y sección (cohortes de aula).
```sql
CREATE TABLE cursos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,              -- 'Noveno B', 'Décimo A', 'Cuarto A'
    grado INT NOT NULL,                       -- 4, 5, ..., 11
    seccion VARCHAR(5) NOT NULL,              -- 'A', 'B', 'C'
    anio_lectivo INT NOT NULL DEFAULT 2026,
    director_curso VARCHAR(150),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **3. Tabla `clases`**
Materias o asignaturas académicas.
```sql
CREATE TABLE clases (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,             -- 'Matemáticas', 'Ciencias Sociales', 'Química'
    area VARCHAR(100) NOT NULL,               -- 'Ciencias Exactas', 'Humanidades', etc.
    descripcion TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **4. Tablas Intermedias de Matrícula (`matriculas_curso`, `matriculas_clase`, `clases_curso`)**
```sql
CREATE TABLE matriculas_curso (
    id SERIAL PRIMARY KEY,
    estudiante_id INT NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    curso_id INT NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    anio_lectivo INT NOT NULL DEFAULT 2026,
    UNIQUE (estudiante_id, curso_id, anio_lectivo)
);

CREATE TABLE matriculas_clase (
    id SERIAL PRIMARY KEY,
    estudiante_id INT NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    clase_id INT NOT NULL REFERENCES clases(id) ON DELETE CASCADE,
    anio_lectivo INT NOT NULL DEFAULT 2026,
    UNIQUE (estudiante_id, clase_id, anio_lectivo)
);

CREATE TABLE clases_curso (
    id SERIAL PRIMARY KEY,
    curso_id INT NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    clase_id INT NOT NULL REFERENCES clases(id) ON DELETE CASCADE,
    docente_encargado VARCHAR(150),
    UNIQUE (curso_id, clase_id)
);
```

#### **5. Tablas `rubricas` y `dimensiones_rubrica`**
```sql
CREATE TABLE rubricas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    clase_id INT REFERENCES clases(id) ON DELETE SET NULL,
    escala_min NUMERIC(3,1) DEFAULT 0.0,
    escala_max NUMERIC(3,1) DEFAULT 5.0,
    tipo_escala VARCHAR(20) DEFAULT 'CONTINUA', -- 'CONTINUA' o 'DISCRETA'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE dimensiones_rubrica (
    id SERIAL PRIMARY KEY,
    rubrica_id INT NOT NULL REFERENCES rubricas(id) ON DELETE CASCADE,
    clave VARCHAR(50) NOT NULL,                -- 'razonamiento_logico'
    nombre VARCHAR(150) NOT NULL,             -- 'Pensamiento Lógico y Estructurado'
    descripcion TEXT,
    peso_porcentual NUMERIC(5,2) DEFAULT 0.0,
    descriptor_bajo TEXT,                     -- 0.0 a 2.9
    descriptor_basico TEXT,                   -- 3.0 a 3.9
    descriptor_alto TEXT,                     -- 4.0 a 4.5
    descriptor_superior TEXT                  -- 4.6 a 5.0
);
```

#### **6. Tabla `reportes` (Bitácora de Observaciones con JSONB)**
```sql
CREATE TABLE reportes (
    id SERIAL PRIMARY KEY,
    uuid_anonimo VARCHAR(64) NOT NULL,
    estudiante_id INT NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    curso_id INT NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    clase_id INT NOT NULL REFERENCES clases(id) ON DELETE CASCADE,
    rubrica_id INT REFERENCES rubricas(id) ON DELETE SET NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    texto_original TEXT NOT NULL,              -- Texto con nombres para vista del profesor
    texto_anonimizado TEXT NOT NULL,           -- Texto sanitizado para el pipeline de IA
    calificaciones_dimensiones JSONB NOT NULL DEFAULT '{}'::jsonb, -- {"dim_1": 4.2, "dim_2": 3.5}
    metadata_adicional JSONB DEFAULT '{}'::jsonb, -- info de audio, atajos, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reportes_estudiante_fecha ON reportes(estudiante_id, fecha);
CREATE INDEX idx_reportes_curso_clase ON reportes(curso_id, clase_id);
CREATE INDEX idx_reportes_jsonb_calificaciones ON reportes USING GIN (calificaciones_dimensiones);
```

#### **7. Tablas `modelos_informe` e `informes_generados`**
```sql
CREATE TABLE modelos_informe (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    tipo_informe VARCHAR(20) NOT NULL,         -- 'INDIVIDUAL' o 'AGREGADO'
    prompt_base TEXT NOT NULL,
    filtros_predeterminados JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE informes_generados (
    id SERIAL PRIMARY KEY,
    modelo_informe_id INT REFERENCES modelos_informe(id) ON DELETE SET NULL,
    tipo_informe VARCHAR(20) NOT NULL,
    estudiante_id INT REFERENCES estudiantes(id) ON DELETE CASCADE,
    curso_id INT REFERENCES cursos(id) ON DELETE CASCADE,
    clase_id INT REFERENCES clases(id) ON DELETE CASCADE,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    prompt_utilizado TEXT,
    contenido_narrativo TEXT NOT NULL,
    datos_grafica JSONB NOT NULL,
    archivo_docx_path VARCHAR(255),
    archivo_pdf_path VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## **8. Diseño del Dataset Semilla (Seed Data de 230 Estudiantes)**

Tal como lo requieren las indicaciones del proyecto, se construirá un script completo `seed_data.sql` que poblará la base de datos con un entorno realista para pruebas inmediatas en el año lectivo 2026:

### **8.1. Estructura de los 230 Estudiantes:**
* **Grados cubiertos**: De 5.º a 11.º de educación básica y media.
* **Secciones únicas por grado**: Cada estudiante pertenece a un curso formal (ej. *Quinto A*, *Sexto B*, *Séptimo A*, *Octavo C*, *Noveno B*, *Décimo A*, *Once B*).
* **Demografía realista de Colombia**:
  * Nombres y apellidos colombianos auténticos (distribución equitativa masculina y femenina).
  * Documentos tipo Tarjeta de Identidad (TI) con numeración de 10 dígitos realista.
  * Edades estrictamente calibradas por grado:
    * 5.º Grado: 10 a 11 años.
    * 6.º Grado: 11 a 12 años.
    * 7.º Grado: 12 a 13 años.
    * 8.º Grado: 13 a 14 años.
    * 9.º Grado: 14 a 15 años.
    * 10.º Grado: 15 a 16 años.
    * 11.º Grado: 16 a 18 años.
  * Asignación coherente a las clases obligatorias del currículo colombiano (Matemáticas, Lengua Castellana, Ciencias Naturales/Biología/Química/Física, Ciencias Sociales, Inglés, Educación Artística, Ética y Valores).

### **8.2. Catálogo de Rúbricas Pre-configuradas:**
1. **Rúbrica de Habilidades Matemáticas y Lógicas**:
   * *Dimensión 1*: Razonamiento Cuantitativo y Lógico.
   * *Dimensión 2*: Modelación y Resolución de Problemas.
   * *Dimensión 3*: Comunicación Matemática y Precisión Conceptual.
2. **Rúbrica de Expresión y Habilidades de Lenguaje**:
   * *Dimensión 1*: Comprensión Lectora e Inferencia Crítica.
   * *Dimensión 2*: Coherencia, Cohesión y Riqueza Léxica.
   * *Dimensión 3*: Argumentación y Sustentación Verbal.
3. **Rúbrica de Competencias Científicas e Indagación**:
   * *Dimensión 1*: Formulación de Hipótesis y Metodología.
   * *Dimensión 2*: Análisis e Interpretación de Evidencias.
4. **Rúbrica Socioemocional y de Convivencia Escolar**:
   * *Dimensión 1*: Trabajo en Equipo y Escucha Asertiva.
   * *Dimensión 2*: Manejo Emocional y Autorregulación en Conflictos.
   * *Dimensión 3*: Sentido de Responsabilidad y Compromiso Comunitario.

### **8.3. Simulación de Reportes a lo largo de 2026:**
El dataset incluirá cientos de reportes temporales distribuidos cronológicamente entre febrero de 2026 y noviembre de 2026 para permitir probar las gráficas evolutivas:
* **Casos Pedagógicos Positivos**: Estudiantes con progreso sostenido, liderazgo en proyectos, mejora notable en cálculo mental o redacción.
* **Dificultades de Aprendizaje**: Estudiantes con retrasos en lectura comprensiva, dispersión de atención, dificultades con álgebra o fracciones.
* **Situaciones de Convivencia y Conflictos**: Desacuerdos durante trabajos grupales, peleas o agresiones verbales en el recreo (donde se evidenciará el uso de chiclets para anonimizar a los compañeros involucrados).
* **Asuntos Personales y Emocionales**: Cambios anímicos por dinámicas familiares, timidez excesiva, desmotivación o ausentismo justificado.

---

## **9. Contratos de API y Rutas del Sistema (FastAPI + HTMX)**

| Método | Endpoint | Descripción | Formato Respuesta |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Redirección o dashboard principal | HTML (Jinja2) |
| `GET` | `/estudiantes` | Vista principal de gestión de estudiantes | HTML (Jinja2) |
| `GET` | `/estudiantes/tabla` | Fragmento de tabla filtrada | HTML (HTMX fragment) |
| `POST` | `/estudiantes/modal-crear` | Retorna el modal para nuevo estudiante | HTML (HTMX fragment) |
| `POST` | `/estudiantes` | Registra un nuevo estudiante en BD | HTML (Row / Swap) |
| `POST` | `/estudiantes/importar` | Carga masiva mediante archivo Excel/CSV | HTML (Feedback / Table) |
| `GET` | `/estudiantes/exportar` | Descarga de nómina en Excel (.xlsx) | Archivo binario |
| `GET` | `/cursos-clases` | Vista de gestión de cursos y asignaturas | HTML (Jinja2) |
| `POST` | `/cursos-clases/asignar` | Vincula estudiantes a cursos o clases | HTML (HTMX fragment) |
| `GET` | `/rubricas` | Catálogo y editor de rúbricas | HTML (Jinja2) |
| `POST` | `/rubricas` | Guarda o actualiza una rúbrica con dimensiones | HTML (Card / Table) |
| `GET` | `/reportes` | Interfaz de captura de observaciones / Modo Ráfaga | HTML (Jinja2) |
| `GET` | `/reportes/modo-rafaga` | Tarjeta del estudiante activo en la secuencia | HTML (HTMX fragment) |
| `POST` | `/reportes/interpretar-audio`| IA infiere puntuaciones de rúbrica a partir del texto | JSON / HTML Sliders |
| `POST` | `/reportes/guardar-avanzar` | Persiste reporte actual y retorna siguiente tarjeta | HTML (Card Swap) |
| `POST` | `/api/stt/transcribe` | Transcribe audio grabado usando Whisper backend | JSON `{ "texto": "..." }` |
| `GET` | `/informes` | Generador y visualizador de informes | HTML (Jinja2) |
| `POST` | `/informes/preview` | Genera vista previa del informe con gráficas | HTML (Preview Panel) |
| `POST` | `/informes/exportar/docx` | Genera y descarga el informe oficial en Word | Archivo binario (.docx) |
| `POST` | `/informes/exportar/pdf` | Genera y descarga el informe oficial en PDF | Archivo binario (.pdf) |
| `GET` | `/configuracion` | Ajustes de llaves API, modelo LLM y STT | HTML (Jinja2) |
| `POST` | `/configuracion` | Actualiza configuración en caliente | HTML (Status badge) |

---

## **10. Despliegue en Railway y Flujo Operativo**

### **10.1. Variables de Entorno Requeridas (`.env`)**
```ini
# Configuración del Servidor
PORT=8000
ENVIRONMENT=production
SECRET_KEY=govlab_unisabana_reia_secret_2026

# Base de Datos PostgreSQL (Railway gestionado)
DATABASE_URL=postgresql://postgres:password@postgres.railway.internal:5432/railway

# Proveedores de Inteligencia Artificial
LLM_PROVIDER_DEFAULT=openai  # 'openai' o 'anthropic'
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Modelos por Defecto
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_MODEL=claude-3-5-haiku-20241022

# Configuración de Speech-to-Text
STT_DEFAULT_ENGINE=hybrid    # 'hybrid', 'native', 'whisper'
```

### **10.2. Estructura de Carpetas del Proyecto**
```
REIA/
│
├── static/
│   ├── css/
│   │   └── style.css            # Estilos institucionales UniSabana
│   ├── fonts/
│   │   └── PublicoBannerWeb-LightItalic_govlab.woff2
│   ├── img/
│   │   └── GovLab_blanco.png    # Logotipo oficial
│   └── js/
│       ├── stt.js               # Lógica Web Speech API + MediaRecorder
│       └── charts.js            # Inicialización de Chart.js
│
├── templates/                   # Plantillas Jinja2 con partials HTMX
│   ├── base.html                # Layout maestro con navbar y footer GovLab
│   ├── estudiantes/
│   ├── cursos_clases/
│   ├── rubricas/
│   ├── reportes/
│   ├── informes/
│   └── configuracion/
│
├── app/
│   ├── main.py                  # Entrada FastAPI y montaje de rutas
│   ├── config.py                # Pydantic Settings
│   ├── database.py              # Engine SQLAlchemy y sesiones
│   ├── models/                  # Modelos relacionales ORM
│   ├── schemas/                 # Esquemas Pydantic
│   ├── services/
│   │   ├── llm_service.py       # Factory OpenAI / Anthropic
│   │   ├── privacy_service.py   # Tokenizador, detección de chiclets y swapper
│   │   ├── stt_service.py       # Whisper API adapter
│   │   ├── chart_service.py     # Matplotlib / Seaborn headless generator
│   │   ├── docx_service.py      # Generador de informes Word
│   │   └── pdf_service.py       # Generador de informes PDF
│   └── routers/                 # Controladores HTMX
│
├── database/
│   ├── schema.sql               # DDL de tablas e índices
│   └── seed_data.sql            # 230 estudiantes, cursos, clases y reportes 2026
│
├── requirements.txt
├── Dockerfile
├── Procfile
└── Indicaciones.md
```

---

## **11. Conclusión y Checklist de Validación**

Este documento constituye la **definición total, no ambigua y exhaustiva** de REIA. Reúne todos los acuerdos técnicos y pedagógicos:
* [x] **Privacidad Inviolable**: Esquema *Zero-PII* con chiclets para compañeros y reemplazo local en memoria.
* [x] **Diseño Institucional 100% Homologado**: Fuentes *Publico Banner* y paleta corporativa de la Universidad de la Sabana / GovLab.
* [x] **Flexibilidad de IA**: Conmutación transparente entre OpenAI y Anthropic.
* [x] **Velocidad Docente**: Modo Ráfaga con STT híbrido y sugerencia automática de rúbricas.
* [x] **Rigor Estadístico**: Gráficas longitudinales individuales y diagramas de caja y bigotes (boxplots) con medias para informes de curso.
* [x] **Entregables de Calidad**: Exportación directa a Word (.docx) y PDF con membrete y firmas.
* [x] **Base de Datos Robusta**: PostgreSQL relacional + JSONB, acompañada de un dataset semilla de 230 estudiantes colombianos en el año lectivo 2026.
