# **Guía Paso a Paso para la Creación e Implementación de REIA**
### **Manual Técnico de Construcción, Integración y Despliegue**
**GovLab — Universidad de la Sabana**  
*Herramienta: Realimentación Estudiantil con Inteligencia Artificial*

---

## **1. Introducción y Hoja de Ruta**

Esta guía detalla, fase por fase y paso a paso, la construcción integral de la herramienta **REIA** partiendo desde cero hasta su despliegue en producción sobre la plataforma **Railway**.

El desarrollo está organizado en **6 Fases Secuenciales**:

```mermaid
flowchart LR
    F0["Fase 0: Entorno y Estructura"] --> F1["Fase 1: Base de Datos y Seed"]
    F1 --> F2["Fase 2: Backend y Servicios Core"]
    F2 --> F3["Fase 3: Frontend Jinja2 + HTMX"]
    F3 --> F4["Fase 4: Pruebas y Validación"]
    F4 --> F5["Fase 5: Despliegue en Railway"]
```

---

## **Fase 0: Preparación del Entorno y Estructura del Repositorio**

### **Paso 0.1: Requisitos Previos del Sistema**
Asegurarse de tener instalado en el entorno de desarrollo:
* **Python 3.11+**
* **Git**
* **PostgreSQL** local (o acceso a una instancia gestionada en Railway)
* **Railway CLI** (`npm i -g @railway/cli`)

### **Paso 0.2: Inicialización del Proyecto y Entorno Virtual**
En la terminal (PowerShell o Bash), dentro del directorio del proyecto:

```bash
# Crear entorno virtual de Python
python -m venv venv

# Activar el entorno virtual
# En Windows:
.\venv\Scripts\Activate.ps1
# En Linux/Mac:
# source venv/bin/activate

# Actualizar gestor de paquetes
python -m pip install --upgrade pip
```

### **Paso 0.3: Definición de Dependencias (`requirements.txt`)**
Crear el archivo `requirements.txt` con las librerías necesarias:

```ini
# Framework Web y Servidor ASGI
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
jinja2>=3.1.3
python-multipart>=0.0.9

# Configuración y Entorno
pydantic>=2.6.4
pydantic-settings>=2.2.1
python-dotenv>=1.0.1

# Base de Datos y ORM
sqlalchemy>=2.0.28
psycopg2-binary>=2.9.9
alembic>=1.13.1

# Clientes de Inteligencia Artificial
openai>=1.14.0
anthropic>=0.19.0

# Procesamiento de Audio (STT Respaldo)
requests>=2.31.0

# Generación Documental y Gráficos
python-docx>=1.1.0
matplotlib>=3.8.3
seaborn>=0.13.2
weasyprint>=61.2  # Requiere librerías cairo/pango o xhtml2pdf como alternativa liviana
xhtml2pdf>=0.2.14

# Manipulación de Datos y Hojas de Cálculo
pandas>=2.2.1
openpyxl>=3.1.2
```

Instalar las dependencias:
```bash
pip install -r requirements.txt
```

### **Paso 0.4: Estructuración del Árbol de Carpetas**
Organizar el proyecto para desacoplar el servidor, la lógica de negocio, los templates y los assets institucionales:

```bash
REIA/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Punto de entrada de FastAPI
│   ├── config.py                # Variables de entorno y ajustes
│   ├── database.py              # Sesión de SQLAlchemy y conexión a Postgres
│   ├── models/                  # Entidades de base de datos
│   │   ├── __init__.py
│   │   ├── estudiante.py
│   │   ├── curso_clase.py
│   │   ├── rubrica.py
│   │   ├── reporte.py
│   │   └── modelo_informe.py
│   ├── schemas/                 # Validadores Pydantic
│   │   ├── __init__.py
│   │   ├── estudiante_schema.py
│   │   ├── rubrica_schema.py
│   │   ├── reporte_schema.py
│   │   └── informe_schema.py
│   ├── services/                # Lógica de negocio y motores
│   │   ├── __init__.py
│   │   ├── privacy_service.py   # Zero-PII, chiclets y reemplazo local
│   │   ├── llm_service.py       # Factory OpenAI y Anthropic
│   │   ├── stt_service.py       # Transcripción Whisper
│   │   ├── chart_service.py     # Generador de gráficas y boxplots
│   │   ├── docx_service.py      # Generador de informes Word
│   │   ├── pdf_service.py       # Generador de informes PDF
│   │   └── excel_service.py     # Importación / exportación masiva
│   └── routers/                 # Controladores HTMX y API
│       ├── __init__.py
│       ├── estudiantes_router.py
│       ├── cursos_clases_router.py
│       ├── rubricas_router.py
│       ├── reportes_router.py
│       ├── informes_router.py
│       └── configuracion_router.py
│
├── database/
│   ├── schema.sql               # Script DDL de tablas y restricciones
│   └── seed_data.sql            # Script con los 230 estudiantes y reportes 2026
│
├── static/
│   ├── css/
│   │   └── style.css            # Archivo maestro de estilos GovLab UniSabana
│   ├── fonts/
│   │   └── PublicoBannerWeb-LightItalic_govlab.woff2
│   ├── img/
│   │   └── GovLab_blanco.png
│   └── js/
│       ├── stt.js               # Web Speech API + audio recording
│       └── charts.js            # Lógica interactiva con Chart.js
│
├── templates/
│   ├── base.html                # Layout general con Navbar y Footer
│   ├── components/              # Partials reutilizables para HTMX
│   │   ├── chiclet_badge.html
│   │   └── modal.html
│   ├── estudiantes/
│   │   ├── index.html
│   │   ├── tabla.html
│   │   └── modal_form.html
│   ├── cursos_clases/
│   │   └── index.html
│   ├── rubricas/
│   │   ├── index.html
│   │   └── editor_rubrica.html
│   ├── reportes/
│   │   ├── index.html
│   │   └── tarjeta_rafaga.html  # Tarjeta del estudiante en Modo Ráfaga
│   ├── informes/
│   │   ├── index.html
│   │   ├── preview_panel.html
│   │   └── graficas.html
│   └── configuracion/
│       └── index.html
│
├── .env.example
├── .gitignore
├── Dockerfile
├── Procfile
└── requirements.txt
```

### **Paso 0.5: Disposición de Assets Institucionales**
1. Copiar `style.css` a `static/css/style.css`.
2. Copiar `PublicoBannerWeb-LightItalic_govlab.woff2` a `static/fonts/`.
3. Copiar `GovLab_blanco.png` a `static/img/`.

---

## **Fase 1: Capa de Base de Datos y Dataset Semilla (PostgreSQL)**

### **Paso 1.1: Creación del Script DDL (`database/schema.sql`)**
Construir el archivo SQL con la arquitectura híbrida (Relacional + JSONB):
* Tablas normalizadas: `estudiantes`, `cursos`, `clases`, `matriculas_curso`, `matriculas_clase`, `clases_curso`, `rubricas`, `dimensiones_rubrica`, `modelos_informe`.
* Tabla documental con llaves foráneas: `reportes` con columnas `calificaciones_dimensiones JSONB` y `metadata_adicional JSONB`.
* Índices de alto rendimiento:
  ```sql
  CREATE INDEX idx_estudiantes_uuid ON estudiantes(uuid_anonimo);
  CREATE INDEX idx_reportes_estudiante_fecha ON reportes(estudiante_id, fecha);
  CREATE INDEX idx_reportes_curso_clase ON reportes(curso_id, clase_id);
  CREATE INDEX idx_reportes_calificaciones ON reportes USING GIN (calificaciones_dimensiones);
  ```

### **Paso 1.2: Construcción del Generador del Dataset Semilla (`database/seed_data.sql`)**
El script debe contener:
1. **Catálogo de Cursos**:
   * Grados de 5.º a 11.º con una sección por grado (ej. *Quinto A*, *Sexto B*, *Séptimo A*, *Octavo C*, *Noveno B*, *Décimo A*, *Once B*).
2. **Catálogo de Clases / Materias**:
   * *Matemáticas*, *Lengua Castellana*, *Ciencias Sociales*, *Ciencias Naturales / Biología*, *Química*, *Física*, *Inglés*, *Ética y Valores*.
3. **Población de 230 Estudiantes**:
   * Nombres y apellidos colombianos combinados de manera realista (ej. *Sofía Valentina Ramírez Gutiérrez*, *Juan David Morales Castro*, *Mariana Gómez Ortiz*).
   * Identificaciones tipo TI con 10 dígitos.
   * Edades consistentes con cada grado (10-11 años en 5º hasta 16-18 años en 11º).
   * Asignación aleatoria pero coherente a los cursos y sus clases correspondientes.
4. **Catálogo de 4 Rúbricas Oficiales**:
   * *Rúbrica de Razonamiento Matemático* (3 dimensiones: Lógica, Resolución de Problemas, Comunicación).
   * *Rúbrica de Habilidades de Lenguaje* (3 dimensiones: Comprensión Lectora, Cohesión, Argumentación).
   * *Rúbrica de Competencias Científicas* (2 dimensiones: Hipótesis, Análisis de Evidencia).
   * *Rúbrica Socioemocional y de Convivencia* (3 dimensiones: Trabajo en Equipo, Manejo Emocional, Responsabilidad).
   * Cada dimensión configurada con descriptores cualitativos en la escala de 0.0 a 5.0 (Bajo 0.0-2.9, Básico 3.0-3.9, Alto 4.0-4.5, Superior 4.6-5.0).
5. **Cientos de Reportes Temporales del Año 2026**:
   * Generar registros cronológicos entre febrero de 2026 y noviembre de 2026.
   * Variedad pedagógica:
     * Casos de superación y liderazgo académico.
     * Casos de rezago conceptual o desatención.
     * Casos de convivencia y conflictos entre compañeros (ej. peleas en el recreo con mención a otros estudiantes para alimentar la prueba de los chiclets).
     * Casos personales y emocionales (situaciones familiares, timidez, desmotivación).

---

## **Fase 2: Arquitectura del Backend y Servicios Core**

### **Paso 2.1: Conexión a Base de Datos (`app/database.py`)**
Configurar SQLAlchemy con soporte síncrono/asíncrono y pool de conexiones:

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/reia_db")

# Ajuste para compatibilidad con esquemas de Railway
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### **Paso 2.2: Servicio de Privacidad y Anonimización (`app/services/privacy_service.py`)**
Implementar los 3 pilares de la privacidad *Zero-PII*:
1. **Detección de Nombres de Compañeros**:
   * Función `detectar_menciones(texto: str, estudiantes_curso: list)`: busca coincidencias léxicas de nombres propios del aula en el texto dictado y retorna una lista de candidatos para renderizar los *chiclets* interactivos.
2. **Sanitización del Reporte**:
   * Función `anonimizar_texto(texto: str, estudiante_principal, companeros_confirmados)`:
     * Reemplaza el nombre del estudiante por `[ESTUDIANTE]`.
     * Reemplaza nombres de terceros confirmados por `[COMPANERO_1]`, `[COMPANERO_2]`.
3. **Motor de Reemplazo Local (*Token Swapper*)**:
   * Función `reemplazar_tokens_locales(texto_ia: str, estudiante)`:
     * Sustituye `[NOMBRE_ESTUDIANTE]` por el nombre real (`estudiante.nombres + " " + estudiante.apellidos`).
     * Sustituye `[PRONOMBRE]` por `él` o `ella` según el género del alumno registrado en la BD.
     * Sustituye `[ID_ESTUDIANTE]` por `estudiante.numero_documento`.

### **Paso 2.3: Servicio Factory de Inteligencia Artificial (`app/services/llm_service.py`)**
Crear una interfaz abstracta y las implementaciones para OpenAI y Anthropic:

```python
from abc import ABC, abstractmethod
import json
import os

class BaseLLMService(ABC):
    @abstractmethod
    def inferir_rubrica(self, comentario_anonimo: str, rubrica_data: dict) -> dict:
        """Infiere puntuaciones sugeridas de 0.0 a 5.0 para cada dimensión."""
        pass

    @abstractmethod
    def redactar_informe(self, observaciones_anonimas: list, prompt_docente: str, es_individual: bool) -> str:
        """Redacta el informe formativo usando placeholders [NOMBRE_ESTUDIANTE] y [PRONOMBRE]."""
        pass

class OpenAIService(BaseLLMService):
    # Implementación usando openai.OpenAI() con GPT-4o / GPT-4o-mini
    ...

class AnthropicService(BaseLLMService):
    # Implementación usando anthropic.Anthropic() con Claude 3.5 Sonnet / Haiku
    ...

def get_llm_service(provider: str = None) -> BaseLLMService:
    # Lee de la variable de entorno o de la configuración activa
    selected = provider or os.getenv("LLM_PROVIDER_DEFAULT", "openai")
    if selected == "anthropic":
        return AnthropicService()
    return OpenAIService()
```

### **Paso 2.4: Servicio de Speech-to-Text (`app/services/stt_service.py`)**
* Implementar el endpoint que recibe archivos de audio subidos como `UploadFile`.
* Enviar el archivo a la API de Whisper (`client.audio.transcriptions.create(model="whisper-1", file=...)`).
* Devolver el JSON con el texto transcrito para su inserción en el campo del reporte.

### **Paso 2.5: Servicio de Analítica y Gráficas Headless (`app/services/chart_service.py`)**
Utilizar **Matplotlib** en modo sin interfaz gráfica (`matplotlib.use('Agg')`):
1. **Gráfica Longitudinal Individual**:
   * Diagrama de líneas con fechas en el eje X y calificaciones (0.0 a 5.0) en el eje Y.
   * Una línea por cada dimensión con colores de la paleta UniSabana (`#00135B`, `#f8a719`, `#96272D`, `#00387D`).
2. **Gráfica Agregada de Curso con Boxplots**:
   * Calcular por cada período temporal: Mínimo, $Q_1$, Mediana, $Q_3$, Máximo y Media.
   * Dibujar los diagramas de cajas y bigotes para mostrar la dispersión del grupo.
   * Trazar una línea punteada que conecta las medias aritméticas a lo largo del tiempo.
   * Exportar el gráfico resultante como imagen binaria en memoria (PNG de 300 DPI) para su incrustación en Word/PDF.

### **Paso 2.6: Servicios de Generación Documental (`docx_service.py` y `pdf_service.py`)**
1. **Generación Word (`python-docx`)**:
   * Insertar el membrete con el logo de GovLab y títulos en fuentes del sistema acordes.
   * Añadir la ficha técnica del estudiante o curso.
   * Insertar el texto generado por la IA tras el reemplazo local de nombres.
   * Embeber la imagen de la gráfica generada por `chart_service.py`.
   * Insertar la tabla con las notas y descriptores de la rúbrica.
   * Añadir el pie de página y los espacios para firma.
2. **Generación PDF**:
   * Renderizar una plantilla HTML optimizada para impresión con `@media print` y convertirla con `weasyprint` o `xhtml2pdf`.

### **Paso 2.7: Servicio de Importación/Exportación Masiva (`excel_service.py`)**
* Lectura de archivos `.xlsx` y `.csv` usando `pandas` y `openpyxl`.
* Validación de tipos de datos, formato de documento de identidad y duplicados.
* Generación de descargas de nómina en formato Excel con diseño limpio.

---

## **Fase 3: Desarrollo del Frontend con Jinja2 y HTMX**

### **Paso 3.1: Plantilla Maestra (`templates/base.html`)**
Integrar el layout corporativo de la Universidad de la Sabana y el GovLab:
* Encabezado con logo `GovLab_blanco.png`, título de la herramienta y selector de pestañas (`.nav-pill`).
* Carga de scripts:
  * `htmx.org` (CDN o archivo local en `static/js/vendor/htmx.min.js`).
  * `chart.js` (para gráficos interactivos en el navegador).
  * `style.css` y fuente `PublicoBannerWeb-LightItalic_govlab.woff2`.
* Contenedor `<main id="main-content">` donde HTMX realiza las sustituciones de contenido.
* Footer institucional GovLab.

### **Paso 3.2: Pestaña 1 — Estudiantes (`templates/estudiantes/`)**
* Vista de tabla con paginación y buscador instantáneo (`hx-get="/estudiantes/tabla" hx-trigger="keyup changed delay:300ms"`).
* Modal para crear/editar estudiante sin recargar la página.
* Zona de carga masiva de archivos Excel/CSV con retroalimentación inmediata de filas importadas.

### **Paso 3.3: Pestaña 2 — Cursos y Clases (`templates/cursos_clases/`)**
* Selector de dos columnas: cursos (grados/secciones) y clases (materias).
* Visualizador de nómina por grupo.
* Controles para mover o asignar estudiantes de forma masiva entre cursos y materias.

### **Paso 3.4: Pestaña 3 — Rúbricas (`templates/rubricas/`)**
* Editor visual de dimensiones.
* Controles para definir los descriptores de los 4 tramos (Bajo, Básico, Alto, Superior) y escala de 0.0 a 5.0.
* Función para duplicar o clonar rúbricas existentes.

### **Paso 3.5: Pestaña 4 — Reportes y Modo Ráfaga (`templates/reportes/`)**
* **Panel de Selección**: Docente elige Curso, Clase y Rúbrica.
* **Tarjeta de Secuencia ("Modo Ráfaga")**:
  * Muestra el estudiante actual (ej. *"Estudiante 5 de 32: Juan Morales"*).
  * Botón de micrófono interactivo que activa `stt.js` (Web Speech API nativo con animación de pulso rojo `.recording`).
  * Área de texto que recibe la transcripción en vivo.
  * Renderizado automático de **Chiclets** al detectar nombres de compañeros, permitiendo al docente confirmar la identidad con un clic.
  * Botón "Interpretar con IA": dispara una llamada HTMX a `/reportes/interpretar-audio` y pre-califica las dimensiones de la rúbrica con sliders interactivos.
  * Botones de pie:
    * **"Guardar y Siguiente"**: envia el reporte vía HTMX, persiste el JSONB en Postgres y reemplaza el contenedor con la tarjeta del siguiente alumno.
    * **"Omitir"**: pasa al siguiente alumno sin guardar registro si no hubo observación ese día.

### **Paso 3.6: Pestaña 5 — Informes Consolidados (`templates/informes/`)**
* Selectores de tipo de informe: **Individual** vs **Agregado por Curso/Clase**.
* Selector de estudiante o grupo, fechas de corte y rúbricas a considerar.
* Cuadro de texto para ingresar instrucciones o prompt adicional para el LLM.
* Selector y botón para guardar o cargar "Modelos de Informe" predefinidos.
* Botón **"Generar Vista Previa"**:
  * Realiza la llamada a la IA con el texto anonimizado.
  * Ejecuta el reemplazo local de variables en memoria.
  * Renderiza la gráfica interactiva con Chart.js en la pantalla.
  * Muestra los botones de descarga oficial: **"Descargar Word (.docx)"** y **"Descargar PDF"**.

### **Paso 3.7: Pestaña 6 — Configuración (`templates/configuracion/`)**
* Selector de proveedor de IA activo: radio buttons para conmutar entre **OpenAI** y **Anthropic**.
* Selector de motor STT: **Nativo del Navegador** vs **Whisper en Servidor**.
* Campo para actualizar API keys de forma local/temporal para pruebas internas.

---

## **Fase 4: Pruebas Integrales y Validación**

### **Paso 4.1: Validación de la Regla de Oro (Zero-PII)**
* Ejecutar interceptor o inspección de logs HTTP en las llamadas salientes a OpenAI y Anthropic.
* Certificar que en los payloads JSON enviados a los proveedores **nunca aparezca ningún nombre ni documento de identidad**.
* Verificar que en la respuesta generada por la IA se utilicen correctamente los placeholders `[NOMBRE_ESTUDIANTE]` y `[PRONOMBRE]`.
* Verificar que en el documento final descargado (Word/PDF) los placeholders hayan sido reemplazados exitosamente por el nombre civil del estudiante.

### **Paso 4.2: Prueba de Eficiencia en Modo Ráfaga**
* Simular el registro de 10 estudiantes consecutivos en una clase de 9.º grado.
* Medir el tiempo de transición entre presionar "Guardar y Siguiente" y la visualización de la tarjeta del siguiente estudiante (el tiempo debe ser menor a 400 milisegundos gracias a HTMX).

### **Paso 4.3: Verificación de Rigor Estadístico en Gráficas**
* Generar un informe agregado para la clase de Matemáticas en 9.º B sobre el dataset de 2026.
* Verificar que el diagrama de cajas y bigotes refleje con exactitud los percentiles ($Q_1, Q_2, Q_3$), los valores extremos y la línea punteada de la media aritmética.

### **Paso 4.4: Validación de Exportación de Documentos**
* Descargar el archivo `.docx` y abrirlo en Microsoft Word:
  * Verificar que el logotipo de GovLab se visualice con nitidez.
  * Verificar que la gráfica incrustada mantenga su resolución sin distorsión.
  * Verificar los saltos de página y el pie con espacios de firma.
* Descargar el archivo `.pdf` y verificar su fidelidad visual idéntica.

---

## **Fase 5: Despliegue en Railway**

### **Paso 5.1: Preparación del Archivo de Despliegue (`Dockerfile`)**
Crear un `Dockerfile` optimizado que instale dependencias de sistema para fuentes y renderizado de documentos:

```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema para WeasyPrint, fuentes y gráficos
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libcairo2 \
    fonts-liberation \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main.py:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Paso 5.2: Creación del Proyecto en Railway y Aprovisionamiento de PostgreSQL**
1. Iniciar sesión en Railway (`railway login`).
2. Crear un nuevo proyecto: `railway init` (o crearlo desde el Dashboard web de Railway).
3. Añadir el servicio de base de datos: **Add Service $\rightarrow$ Database $\rightarrow$ Add PostgreSQL**.
4. Railway generará automáticamente la variable de entorno `DATABASE_URL` vinculada.

### **Paso 5.3: Configuración de Variables de Entorno en Railway**
En el panel del servicio web en Railway, definir:
* `DATABASE_URL`: `${{Postgres.DATABASE_URL}}`
* `OPENAI_API_KEY`: Llave de OpenAI
* `ANTHROPIC_API_KEY`: Llave de Anthropic
* `LLM_PROVIDER_DEFAULT`: `openai` (o `anthropic`)
* `ENVIRONMENT`: `production`

### **Paso 5.4: Inicialización y Carga del Dataset Semilla (230 Estudiantes)**
Desde la terminal conectada a Railway (o usando la consola de Railway / `psql`):

```bash
# Ejecutar la creación de tablas
railway run psql $DATABASE_URL -f database/schema.sql

# Poblar la base de datos con los 230 estudiantes y reportes de 2026
railway run psql $DATABASE_URL -f database/seed_data.sql
```

### **Paso 5.5: Despliegue Continuo (Deploy) y Verificación Final**
1. Conectar el repositorio de GitHub a Railway para habilitar deploys automáticos en cada `git push`.
2. Verificar en la pestaña de *Deploy Logs* que Uvicorn arranque sin errores en el puerto configurado.
3. Abrir la URL pública generada por Railway (ej. `https://reia-govlab.up.railway.app`) y comprobar la navegación por todas las pestañas, la captura de audio y la generación de reportes.

---

## **6. Resumen de Entregables del Proyecto**

Al completar esta guía, la herramienta contará con:
1. Repositorio limpio con arquitectura desacoplada y modular.
2. Base de datos PostgreSQL con 230 estudiantes colombianos y reportes simulados del año 2026.
3. Frontend interactivo con diseño institucional UniSabana / GovLab.
4. Módulo de Speech-to-Text híbrido con inferencia automática de rúbricas.
5. Algoritmo inviolable de anonimización Zero-PII con chiclets de compañeros y sustitución local en memoria.
6. Motor analítico con diagramas de cajas y bigotes (boxplots) y exportación oficial a Word y PDF.
7. Despliegue operativo y funcional en la nube de Railway.
