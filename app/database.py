import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database/reia_local.db")

# Ajuste para compatibilidad con esquemas de Railway
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

is_sqlite = DATABASE_URL.startswith("sqlite")

connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializa las tablas y carga el seed si la BD está vacía."""
    from app.models import Estudiante, Curso, Clase, Rubrica, DimensionRubrica, Reporte, ModeloInforme, InformeGenerado
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    # Verificar si ya existen estudiantes
    db = SessionLocal()
    try:
        count = db.query(Estudiante).count()
        if count == 0:
            print("[REIA DB] Base de datos vacía detectada. Inicializando con dataset semilla...")
            # Cargar mediante script de python directo para compatibilidad tanto con SQLite como con Postgres
            poblar_bd_directo(db)
            print(f"[REIA DB] ¡Inicialización completa! {db.query(Estudiante).count()} estudiantes cargados.")
        else:
            print(f"[REIA DB] Base de datos activa con {count} estudiantes.")
    except Exception as e:
        print(f"[REIA DB] Error al verificar/inicializar BD: {e}")
    finally:
        db.close()

def poblar_bd_directo(db):
    """Puebla la BD usando las entidades ORM para máxima compatibilidad multiplataforma."""
    from app.models import Curso, Clase, Rubrica, DimensionRubrica, Estudiante, Reporte, ModeloInforme
    import random
    from datetime import date
    
    # Cursos
    cursos_data = [
        {"grado": 5, "nombre": "Quinto A", "seccion": "A", "director": "Lic. Esperanza Niño"},
        {"grado": 6, "nombre": "Sexto A", "seccion": "A", "director": "Lic. Mauricio Gómez"},
        {"grado": 7, "nombre": "Séptimo A", "seccion": "A", "director": "Lic. Claudia Patarroyo"},
        {"grado": 8, "nombre": "Octavo B", "seccion": "B", "director": "Lic. Fernando Salamanca"},
        {"grado": 9, "nombre": "Noveno B", "seccion": "B", "director": "Lic. Patricia Cifuentes"},
        {"grado": 10, "nombre": "Décimo A", "seccion": "A", "director": "Lic. Ricardo Moncada"},
        {"grado": 11, "nombre": "Once A", "seccion": "A", "director": "Lic. Marcela Restrepo"}
    ]
    cursos_map = {}
    for c in cursos_data:
        curso = Curso(nombre=c["nombre"], grado=c["grado"], seccion=c["seccion"], anio_lectivo=2026, director_curso=c["director"])
        db.add(curso)
        db.flush()
        cursos_map[c["grado"]] = curso.id

    # Clases
    clases_data = [
        {"nombre": "Matemáticas", "area": "Ciencias Exactas", "desc": "Razonamiento lógico, álgebra y geometría."},
        {"nombre": "Lengua Castellana", "area": "Humanidades y Letras", "desc": "Comprensión lectora, producción textual y argumentación."},
        {"nombre": "Ciencias Sociales", "area": "Ciencias Humanas", "desc": "Historia de Colombia, geografía y competencias ciudadanas."},
        {"nombre": "Ciencias Naturales y Biología", "area": "Ciencias Naturales", "desc": "Ecología, sistemas biológicos y método científico."},
        {"nombre": "Química", "area": "Ciencias Naturales", "desc": "Estructura molecular y laboratorio escolar."},
        {"nombre": "Física", "area": "Ciencias Exactas", "desc": "Mecánica clásica, termodinámica y ondas."},
        {"nombre": "Inglés", "area": "Lenguas Extranjeras", "desc": "Gramática, fluidez verbal y listening."},
        {"nombre": "Ética y Valores", "area": "Formación Integral", "desc": "Resolución de conflictos, convivencia y empatía escolar."}
    ]
    clases_list = []
    for cl in clases_data:
        clase = Clase(nombre=cl["nombre"], area=cl["area"], descripcion=cl["desc"])
        db.add(clase)
        db.flush()
        clases_list.append(clase)

    # Rúbricas
    r1 = Rubrica(nombre="Razonamiento y Pensamiento Matemático", descripcion="Evaluación de habilidades lógicas, modelación y resolución de problemas.", escala_min=0.0, escala_max=5.0, tipo_escala="CONTINUA")
    r2 = Rubrica(nombre="Habilidades de Comunicación y Lenguaje", descripcion="Comprensión crítica, redacción coherente y argumentación oral.", escala_min=0.0, escala_max=5.0, tipo_escala="CONTINUA")
    r3 = Rubrica(nombre="Indagación Científica y Pensamiento Crítico", descripcion="Formulación de hipótesis y análisis de evidencias.", escala_min=0.0, escala_max=5.0, tipo_escala="CONTINUA")
    r4 = Rubrica(nombre="Convivencia y Habilidades Socioemocionales", descripcion="Trabajo en equipo, autorregulación y empatía.", escala_min=0.0, escala_max=5.0, tipo_escala="CONTINUA")
    db.add_all([r1, r2, r3, r4])
    db.flush()

    # Dimensiones
    dims = [
        DimensionRubrica(rubrica_id=r1.id, clave="dim_1_logica", nombre="Pensamiento Lógico y Estructurado", peso_porcentual=35.0, descriptor_bajo="Dificultades severas en secuencias deductivas.", descriptor_basico="Sigue secuencias simples con orientación.", descriptor_alto="Estructura argumentos lógicos sólidos.", descriptor_superior="Deducciones abstractas impecables e innovadoras."),
        DimensionRubrica(rubrica_id=r1.id, clave="dim_2_resolucion", nombre="Resolución de Problemas y Modelación", peso_porcentual=40.0, descriptor_bajo="No logra formular un plan ante problemas.", descriptor_basico="Aplica algoritmos pero yerra en problemas abiertos.", descriptor_alto="Modela y resuelve problemas contextualizados.", descriptor_superior="Múltiples estrategias de resolución originales."),
        DimensionRubrica(rubrica_id=r1.id, clave="dim_3_precision", nombre="Precisión y Comunicación Matemática", peso_porcentual=25.0, descriptor_bajo="Errores operativos y notación confusa.", descriptor_basico="Notación adecuada pero explicaciones desordenadas.", descriptor_alto="Lenguaje matemático claro y ordenado.", descriptor_superior="Expresión simbólica y gráfica sobresaliente."),
        
        DimensionRubrica(rubrica_id=r2.id, clave="dim_1_comprension", nombre="Comprensión Lectora e Inferencia", peso_porcentual=40.0, descriptor_bajo="Lectura superficial sin captar ideas clave.", descriptor_basico="Identifica datos explícitos pero le cuesta inferir.", descriptor_alto="Infiere intenciones del autor y sintetiza.", descriptor_superior="Lectura crítica profunda e intertextualidad."),
        DimensionRubrica(rubrica_id=r2.id, clave="dim_2_cohesion", nombre="Coherencia y Cohesión Escrita", peso_porcentual=35.0, descriptor_bajo="Párrafos inconexos y fallas ortográficas.", descriptor_basico="Estructura oracional básica con conectores.", descriptor_alto="Párrafos fluidos y correcta ortografía.", descriptor_superior="Estilo literario o ensayístico elocuente."),
        DimensionRubrica(rubrica_id=r2.id, clave="dim_3_oralidad", nombre="Argumentación y Participación Verbal", peso_porcentual=25.0, descriptor_bajo="Inseguridad o apatía durante debates.", descriptor_basico="Expone puntos breves si se le pregunta.", descriptor_alto="Participa con argumentos fundamentados.", descriptor_superior="Liderazgo discursivo y réplica constructiva."),

        DimensionRubrica(rubrica_id=r3.id, clave="dim_1_hipotesis", nombre="Formulación de Hipótesis y Metodología", peso_porcentual=50.0, descriptor_bajo="No formula hipótesis contrastables.", descriptor_basico="Preguntas guiadas e instrucciones básicas.", descriptor_alto="Diseña planes de indagación válidos.", descriptor_superior="Pensamiento experimental riguroso y autónomo."),
        DimensionRubrica(rubrica_id=r3.id, clave="dim_2_evidencia", nombre="Análisis de Evidencias y Conclusiones", peso_porcentual=50.0, descriptor_bajo="Conclusiones no fundamentadas en datos.", descriptor_basico="Registra observaciones pero cuesta relacionar.", descriptor_alto="Interpreta gráficos y extrae conclusiones.", descriptor_superior="Modela fenómenos empíricos y discute errores."),

        DimensionRubrica(rubrica_id=r4.id, clave="dim_1_equipo", nombre="Trabajo en Equipo y Escucha Activa", peso_porcentual=35.0, descriptor_bajo="Aislamiento o actitudes individualistas.", descriptor_basico="Colabora de forma pasiva.", descriptor_alto="Aporta activamente y escucha a otros.", descriptor_superior="Fomenta la sinergia grupal y motiva."),
        DimensionRubrica(rubrica_id=r4.id, clave="dim_2_autorregulacion", nombre="Autorregulación y Manejo Emocional", peso_porcentual=35.0, descriptor_bajo="Reacciones explosivas o frustración.", descriptor_basico="Le cuesta mantener calma pero cede.", descriptor_alto="Maneja adecuadamente situaciones tensas.", descriptor_superior="Madurez emocional sobresaliente y mediación."),
        DimensionRubrica(rubrica_id=r4.id, clave="dim_3_responsabilidad", nombre="Responsabilidad y Respeto Comunitario", peso_porcentual=30.0, descriptor_bajo="Incumplimiento de normas escolares.", descriptor_basico="Cumple deberes mínimos tras llamados.", descriptor_alto="Respetuoso de acuerdos y puntual.", descriptor_superior="Ejemplo de civismo y cuidado de la comunidad.")
    ]
    db.add_all(dims)
    db.flush()

    # Nombres colombianos
    nombres_masc = ["Juan", "Santiago", "Mateo", "Sebastián", "Nicolás", "Samuel", "David", "Daniel", "Andrés", "Felipe", "Camilo", "Tomás", "Lucas", "Diego", "Carlos", "Julián"]
    nombres_fem = ["Sofía", "Valentina", "Isabella", "Mariana", "Camila", "Luciana", "Gabriela", "Daniela", "Sara", "Juliana", "Salomé", "Valeria", "Catalina", "Paula", "María José", "Laura"]
    apellidos = ["Rodríguez", "González", "Martínez", "Gómez", "López", "Hernández", "Pérez", "García", "Sánchez", "Ramírez", "Torres", "Díaz", "Vargas", "Castro", "Morales", "Ortiz", "Gutiérrez", "Rojas", "Jiménez", "Moreno"]

    distribucion = [(5, 32), (6, 33), (7, 33), (8, 33), (9, 33), (10, 33), (11, 33)]
    estudiantes_creados = []
    est_counter = 1
    doc_base = 1025840000

    random.seed(2026)
    for grado, count in distribucion:
        c_id = cursos_map[grado]
        edad_base = grado + 5
        for _ in range(count):
            genero = random.choice(["Masculino", "Femenino"])
            if genero == "Masculino":
                nombres = random.choice(nombres_masc) + " " + random.choice(nombres_masc)
                pronombre = "él"
            else:
                nombres = random.choice(nombres_fem) + " " + random.choice(nombres_fem)
                pronombre = "ella"
            ap = random.choice(apellidos) + " " + random.choice(apellidos)
            edad = edad_base + random.choice([0, 0, 1])
            doc = f"TI-{doc_base + est_counter}"
            uuid_a = f"EST_{est_counter:04d}_{random.randint(1000, 9999):x}"
            acudiente = f"{random.choice(nombres_fem if genero == 'Masculino' else nombres_masc)} {ap.split()[0]}"
            contacto = f"31{random.randint(0, 9)}{random.randint(1000000, 9999999)}"

            est = Estudiante(
                uuid_anonimo=uuid_a,
                tipo_documento="TI",
                numero_documento=doc,
                nombres=nombres,
                apellidos=ap,
                genero=genero,
                pronombre=pronombre,
                edad=edad,
                grado_actual=grado,
                acudiente_nombre=acudiente,
                acudiente_contacto=contacto
            )
            # Asociar a curso
            curso_obj = db.query(Curso).filter_by(id=c_id).first()
            if curso_obj:
                est.cursos.append(curso_obj)
            
            # Asociar a clases
            est.clases.append(clases_list[0]) # Matemáticas
            est.clases.append(clases_list[1]) # Lenguaje
            est.clases.append(clases_list[2]) # Sociales
            est.clases.append(clases_list[6]) # Inglés
            est.clases.append(clases_list[7]) # Ética
            if grado <= 9:
                est.clases.append(clases_list[3]) # Ciencias
            else:
                est.clases.append(clases_list[4]) # Química
                est.clases.append(clases_list[5]) # Física

            db.add(est)
            db.flush()
            estudiantes_creados.append((est, c_id))
            est_counter += 1

    # Reportes 2026
    fechas = [
        date(2026, 2, 9), date(2026, 2, 23), date(2026, 3, 9), date(2026, 3, 23),
        date(2026, 4, 6), date(2026, 4, 20), date(2026, 5, 4), date(2026, 5, 18),
        date(2026, 6, 1), date(2026, 8, 10), date(2026, 9, 7), date(2026, 10, 5)
    ]

    plantillas = [
        (1, {"dim_1_logica": 4.6, "dim_2_resolucion": 4.4, "dim_3_precision": 4.5},
         "Hoy {nombre} demostró un excelente dominio al resolver ecuaciones. Explicó con mucha claridad su procedimiento.",
         "Hoy [ESTUDIANTE] demostró un excelente dominio al resolver ecuaciones. Explicó con mucha claridad su procedimiento."),
        (1, {"dim_1_logica": 2.8, "dim_2_resolucion": 2.5, "dim_3_precision": 3.0},
         "A {nombre} le cuesta bastante el manejo de fracciones y signos negativos. Mostró frustración al resolver ejercicios.",
         "A [ESTUDIANTE] le cuesta bastante el manejo de fracciones y signos negativos. Mostró frustración al resolver ejercicios."),
        (2, {"dim_1_comprension": 4.5, "dim_2_cohesion": 4.2, "dim_3_oralidad": 4.0},
         "{nombre} realizó un ensayo sobresaliente sobre literatura colombiana contemporánea.",
         "[ESTUDIANTE] realizó un ensayo sobresaliente sobre literatura colombiana contemporánea."),
        (4, {"dim_1_equipo": 2.0, "dim_2_autorregulacion": 1.8, "dim_3_responsabilidad": 2.5},
         "Durante el descanso se presentó un altercado entre {nombre} y {companero}. Hubo gritos y empujones por un desacuerdo deportivo.",
         "Durante el descanso se presentó un altercado entre [ESTUDIANTE] y [COMPANERO_1]. Hubo gritos y empujones por un desacuerdo deportivo."),
        (4, {"dim_1_equipo": 4.7, "dim_2_autorregulacion": 4.5, "dim_3_responsabilidad": 4.8},
         "{nombre} mostró un liderazgo excepcional para integrar a todos los compañeros en la actividad colaborativa.",
         "[ESTUDIANTE] mostró un liderazgo excepcional para integrar a todos los compañeros en la actividad colaborativa."),
        (4, {"dim_1_equipo": 3.0, "dim_2_autorregulacion": 3.0, "dim_3_responsabilidad": 3.5},
         "Noté a {nombre} bastante desanimado y distraído. Al conversar en privado mencionó problemas personales familiares.",
         "Noté a [ESTUDIANTE] bastante desanimado y distraído. Al conversar en privado mencionó problemas personales familiares.")
    ]

    for est_obj, c_id in estudiantes_creados:
        fechas_sel = sorted(random.sample(fechas, random.randint(3, 5)))
        nombre_completo = f"{est_obj.nombres} {est_obj.apellidos}"
        
        for f in fechas_sel:
            p = random.choice(plantillas)
            rub_id = p[0]
            califs = p[1].copy()
            for k in califs:
                califs[k] = max(0.0, min(5.0, round(califs[k] + random.uniform(-0.3, 0.3), 1)))
            
            txt_orig = p[2].format(nombre=nombre_completo, companero="un compañero")
            txt_anon = p[3]
            clase_id = 1 if rub_id == 1 else (2 if rub_id == 2 else 8)

            rep = Reporte(
                uuid_anonimo=est_obj.uuid_anonimo,
                estudiante_id=est_obj.id,
                curso_id=c_id,
                clase_id=clase_id,
                rubrica_id=rub_id,
                fecha=f,
                texto_original=txt_orig,
                texto_anonimizado=txt_anon,
                calificaciones_dimensiones=califs,
                metadata_adicional={"metodo_entrada": "VOZ_STT", "calificacion_asistida": True}
            )
            db.add(rep)

    # Modelos de Informe
    m1 = ModeloInforme(
        nombre="Informe de Rendimiento Trimestral para Padres",
        descripcion="Informe pedagógico formativo y cercano, destacando fortalezas y plan de acción para el hogar.",
        tipo_informe="INDIVIDUAL",
        prompt_base="Redactar un informe comprensivo y motivador dirigido a los padres de familia de [NOMBRE_ESTUDIANTE]. Describir su evolución en el trimestre, destacar sus logros principales y brindar recomendaciones prácticas para apoyar su proceso educativo en casa sin sobrecargarle."
    )
    m2 = ModeloInforme(
        nombre="Informe Diagnóstico de Clima de Aula y Convivencia",
        descripcion="Evaluación grupal sobre trabajo en equipo, autorregulación y cohesión de aula.",
        tipo_informe="AGREGADO",
        prompt_base="Analizar el desempeño y clima social del grupo. Señalar las materias con mayor solidez colectiva, los patrones de convivencia observados y estrategias recomendadas para el director de grupo."
    )
    db.add_all([m1, m2])
    db.commit()
