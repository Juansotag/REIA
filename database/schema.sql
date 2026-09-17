-- =====================================================================
-- REIA: Realimentación Estudiantil con Inteligencia Artificial
-- GovLab — Universidad de la Sabana
-- DDL Maestro de Base de Datos (PostgreSQL / SQLite compatible)
-- =====================================================================

-- 1. Tabla de Estudiantes (Aislamiento PII)
CREATE TABLE IF NOT EXISTS estudiantes (
    id SERIAL PRIMARY KEY,
    uuid_anonimo VARCHAR(64) UNIQUE NOT NULL,
    tipo_documento VARCHAR(10) NOT NULL DEFAULT 'TI',
    numero_documento VARCHAR(30) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    genero VARCHAR(20) NOT NULL,              -- 'Masculino', 'Femenino', 'Otro'
    pronombre VARCHAR(10) NOT NULL,           -- 'él', 'ella', 'elle'
    fecha_nacimiento DATE,
    edad INT NOT NULL,
    grado_actual INT NOT NULL,                -- 5 a 11
    acudiente_nombre VARCHAR(150),
    acudiente_contacto VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_estudiantes_uuid ON estudiantes(uuid_anonimo);
CREATE INDEX IF NOT EXISTS idx_estudiantes_grado ON estudiantes(grado_actual);

-- 2. Tabla de Cursos (Grados y Secciones)
CREATE TABLE IF NOT EXISTS cursos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,              -- Ej. 'Noveno B', 'Décimo A'
    grado INT NOT NULL,                       -- 5 a 11
    seccion VARCHAR(5) NOT NULL,              -- 'A', 'B', 'C'
    anio_lectivo INT NOT NULL DEFAULT 2026,
    director_curso VARCHAR(150),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla de Clases (Asignaturas curriculares)
CREATE TABLE IF NOT EXISTS clases (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,             -- Ej. 'Matemáticas', 'Ciencias Sociales'
    area VARCHAR(100) NOT NULL,               -- 'Ciencias Exactas', 'Humanidades', etc.
    descripcion TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Matrículas e Intermedias
CREATE TABLE IF NOT EXISTS matriculas_curso (
    id SERIAL PRIMARY KEY,
    estudiante_id INT NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    curso_id INT NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    anio_lectivo INT NOT NULL DEFAULT 2026,
    UNIQUE (estudiante_id, curso_id, anio_lectivo)
);

CREATE TABLE IF NOT EXISTS matriculas_clase (
    id SERIAL PRIMARY KEY,
    estudiante_id INT NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    clase_id INT NOT NULL REFERENCES clases(id) ON DELETE CASCADE,
    anio_lectivo INT NOT NULL DEFAULT 2026,
    UNIQUE (estudiante_id, clase_id, anio_lectivo)
);

CREATE TABLE IF NOT EXISTS clases_curso (
    id SERIAL PRIMARY KEY,
    curso_id INT NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    clase_id INT NOT NULL REFERENCES clases(id) ON DELETE CASCADE,
    docente_encargado VARCHAR(150),
    UNIQUE (curso_id, clase_id)
);

-- 5. Rúbricas y Dimensiones
CREATE TABLE IF NOT EXISTS rubricas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    clase_id INT REFERENCES clases(id) ON DELETE SET NULL,
    escala_min NUMERIC(3,1) DEFAULT 0.0,
    escala_max NUMERIC(3,1) DEFAULT 5.0,
    tipo_escala VARCHAR(20) DEFAULT 'CONTINUA', -- 'CONTINUA' o 'DISCRETA'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dimensiones_rubrica (
    id SERIAL PRIMARY KEY,
    rubrica_id INT NOT NULL REFERENCES rubricas(id) ON DELETE CASCADE,
    clave VARCHAR(50) NOT NULL,                 -- Ej. 'razonamiento_logico'
    nombre VARCHAR(150) NOT NULL,              -- Ej. 'Pensamiento Lógico y Estructurado'
    descripcion TEXT,
    peso_porcentual NUMERIC(5,2) DEFAULT 0.0,
    descriptor_bajo TEXT,                      -- 0.0 a 2.9
    descriptor_basico TEXT,                    -- 3.0 a 3.9
    descriptor_alto TEXT,                      -- 4.0 a 4.5
    descriptor_superior TEXT                   -- 4.6 a 5.0
);

-- 6. Reportes (Bitácora Diaria de Observaciones con JSONB)
CREATE TABLE IF NOT EXISTS reportes (
    id SERIAL PRIMARY KEY,
    uuid_anonimo VARCHAR(64) NOT NULL,
    estudiante_id INT NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    curso_id INT NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    clase_id INT NOT NULL REFERENCES clases(id) ON DELETE CASCADE,
    rubrica_id INT REFERENCES rubricas(id) ON DELETE SET NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    texto_original TEXT NOT NULL,               -- Texto en interfaz local con nombres
    texto_anonimizado TEXT NOT NULL,            -- Texto sanitizado para el LLM
    calificaciones_dimensiones JSONB NOT NULL DEFAULT '{}'::jsonb, -- {"dim_1": 4.5, "dim_2": 3.8}
    metadata_adicional JSONB DEFAULT '{}'::jsonb,  -- Info de STT, chiclets confirmados, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reportes_estudiante_fecha ON reportes(estudiante_id, fecha);
CREATE INDEX IF NOT EXISTS idx_reportes_curso_clase ON reportes(curso_id, clase_id);

-- 7. Modelos de Informe e Informes Generados
CREATE TABLE IF NOT EXISTS modelos_informe (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    tipo_informe VARCHAR(20) NOT NULL,          -- 'INDIVIDUAL' o 'AGREGADO'
    prompt_base TEXT NOT NULL,
    filtros_predeterminados JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS informes_generados (
    id SERIAL PRIMARY KEY,
    modelo_informe_id INT REFERENCES modelos_informe(id) ON DELETE SET NULL,
    tipo_informe VARCHAR(20) NOT NULL,          -- 'INDIVIDUAL' o 'AGREGADO'
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
