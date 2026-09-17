"""
Script generador del dataset semilla oficial para REIA (GovLab - Universidad de la Sabana).
Genera database/seed_data.sql con 230 estudiantes colombianos de 5º a 11º grado,
sus cursos, clases, rúbricas y reportes simulados del año 2026.
"""

import json
import random
from datetime import date, timedelta

# Nombres y Apellidos auténticos colombianos
NOMBRES_MASC = [
    "Juan", "Santiago", "Mateo", "Sebastián", "Alejandro", "Nicolás", "Samuel", "David",
    "Daniel", "Andrés", "Gabriel", "Felipe", "Camilo", "Tomás", "Emiliano", "Lucas",
    "Joaquín", "Martín", "Diego", "Carlos", "Julián", "Jerónimo", "Simón", "Esteban",
    "Leonardo", "Manuel", "Isaac", "Cristian", "Kevin", "Miguel Ángel"
]

NOMBRES_FEM = [
    "Sofía", "Valentina", "Isabella", "Mariana", "Camila", "Luciana", "Gabriela", "Daniela",
    "Sara", "Juliana", "Salomé", "Valeria", "Catalina", "Paula", "María José", "Antonella",
    "Samantha", "Laura", "Victoria", "Manuela", "Elena", "Natalia", "Andrea", "Carolina",
    "Alejandra", "Ximena", "Abril", "Juana", "Lucía", "Ana Sofía"
]

APELLIDOS = [
    "Rodríguez", "González", "Martínez", "Gómez", "López", "Hernández", "Pérez", "García",
    "Sánchez", "Ramírez", "Torres", "Flores", "Díaz", "Vargas", "Castro", "Morales",
    "Ortiz", "Gutiérrez", "Chávez", "Ramos", "Herrera", "Medina", "Aguilar", "Castillo",
    "Rojas", "Jiménez", "Moreno", "Cárdenas", "Ospina", "Montoya", "Restrepo", "Quintero",
    "Valencia", "Cardona", "Duque", "Vélez", "Buitrago", "Henao", "Jaramillo", "Mejía"
]

CURSOS = [
    {"grado": 5, "nombre": "Quinto A", "seccion": "A", "director": "Lic. Esperanza Niño"},
    {"grado": 6, "nombre": "Sexto A", "seccion": "A", "director": "Lic. Mauricio Gómez"},
    {"grado": 7, "nombre": "Séptimo A", "seccion": "A", "director": "Lic. Claudia Patarroyo"},
    {"grado": 8, "nombre": "Octavo B", "seccion": "B", "director": "Lic. Fernando Salamanca"},
    {"grado": 9, "nombre": "Noveno B", "seccion": "B", "director": "Lic. Patricia Cifuentes"},
    {"grado": 10, "nombre": "Décimo A", "seccion": "A", "director": "Lic. Ricardo Moncada"},
    {"grado": 11, "nombre": "Once A", "seccion": "A", "director": "Lic. Marcela Restrepo"}
]

CLASES = [
    {"nombre": "Matemáticas", "area": "Ciencias Exactas", "desc": "Razonamiento lógico, álgebra, cálculo y geometría."},
    {"nombre": "Lengua Castellana", "area": "Humanidades y Letras", "desc": "Comprensión lectora, producción textual y argumentación."},
    {"nombre": "Ciencias Sociales", "area": "Ciencias Humanas", "desc": "Historia de Colombia, geografía y competencias ciudadanas."},
    {"nombre": "Ciencias Naturales y Biología", "area": "Ciencias Naturales", "desc": "Ecología, sistemas biológicos y método científico."},
    {"nombre": "Química", "area": "Ciencias Naturales", "desc": "Estructura molecular, estequiometría y laboratorio escolar."},
    {"nombre": "Física", "area": "Ciencias Exactas", "desc": "Mecánica clásica, termodinámica y ondas."},
    {"nombre": "Inglés", "area": "Lenguas Extranjeras", "desc": "Gramática, fluidez verbal y listening según marco MCER."},
    {"nombre": "Ética y Valores", "area": "Formación Integral", "desc": "Resolución de conflictos, convivencia y empatía escolar."}
]

def generar_sql():
    random.seed(2026)
    sql_lines = [
        "-- =====================================================================",
        "-- DATASET SEMILLA REIA - 230 ESTUDIANTES COLOMBIANOS (2026)",
        "-- GovLab : Universidad de la Sabana",
        "-- =====================================================================\n"
    ]

    # Cursos
    sql_lines.append("-- 1. Insertar Cursos")
    for c in CURSOS:
        sql_lines.append(
            f"INSERT INTO cursos (nombre, grado, seccion, anio_lectivo, director_curso) "
            f"VALUES ('{c['nombre']}', {c['grado']}, '{c['seccion']}', 2026, '{c['director']}');"
        )
    sql_lines.append("")

    # Clases
    sql_lines.append("-- 2. Insertar Clases")
    for cl in CLASES:
        sql_lines.append(
            f"INSERT INTO clases (nombre, area, descripcion) "
            f"VALUES ('{cl['nombre']}', '{cl['area']}', '{cl['desc']}');"
        )
    sql_lines.append("")

    # Rúbricas
    sql_lines.append("-- 3. Insertar Rúbricas y Dimensiones Oficiales")
    sql_lines.append(
        "INSERT INTO rubricas (id, nombre, descripcion, escala_min, escala_max, tipo_escala) VALUES "
        "(1, 'Razonamiento y Pensamiento Matemático', 'Evaluación de habilidades lógicas, modelación y resolución de problemas.', 0.0, 5.0, 'CONTINUA'),"
        "(2, 'Habilidades de Comunicación y Lenguaje', 'Comprensión crítica, redacción coherente y argumentación oral.', 0.0, 5.0, 'CONTINUA'),"
        "(3, 'Indagación Científica y Pensamiento Crítico', 'Formulación de hipótesis, análisis de evidencias y rigor metodológico.', 0.0, 5.0, 'CONTINUA'),"
        "(4, 'Convivencia y Habilidades Socioemocionales', 'Trabajo en equipo, autorregulación y empatía.', 0.0, 5.0, 'CONTINUA');"
    )

    sql_lines.append(
        "INSERT INTO dimensiones_rubrica (rubrica_id, clave, nombre, peso_porcentual, descriptor_bajo, descriptor_basico, descriptor_alto, descriptor_superior) VALUES "
        "(1, 'dim_1_logica', 'Pensamiento Lógico y Estructurado', 35.0, 'Dificultades severas en secuencias deductivas.', 'Sigue secuencias simples con orientación.', 'Estructura argumentos lógicos sólidos.', 'Plantea deducciones abstractas impecables e innovadoras.'),"
        "(1, 'dim_2_resolucion', 'Resolución de Problemas y Modelación', 40.0, 'No logra formular un plan ante enunciados complejos.', 'Aplica algoritmos conocidos pero yerra en problemas abiertos.', 'Modela y resuelve problemas contextualizados con solvencia.', 'Propone múltiples estrategias de resolución y valida hipótesis.'),"
        "(1, 'dim_3_precision', 'Precisión y Comunicación Matemática', 25.0, 'Errores operativos constantes y notación confusa.', 'Notación adecuada pero explicaciones desordenadas.', 'Usa lenguaje matemático con claridad y orden.', 'Expresión simbólica y gráfica de nivel superior.'),"
        
        "(2, 'dim_1_comprension', 'Comprensión Lectora e Inferencia', 40.0, 'Lectura superficial sin captar ideas clave.', 'Identifica datos explícitos pero le cuesta inferir.', 'Infiere intenciones del autor y sintetiza argumentos.', 'Lectura crítica profunda relacionando intertextualidad.'),"
        "(2, 'dim_2_cohesion', 'Coherencia y Cohesión Escrita', 35.0, 'Párrafos inconexos y fallas ortográficas notorias.', 'Estructura oracional básica con conectores simples.', 'Párrafos fluidos, excelente vocabulario y correcta ortografía.', 'Estilo literario o ensayístico pulcro y elocuente.'),"
        "(2, 'dim_3_oralidad', 'Argumentación y Participación Verbal', 25.0, 'Inseguridad o apatía durante debates.', 'Expone puntos breves cuando se le pregunta directamente.', 'Participa con argumentos fundamentados y respeto.', 'Liderazgo discursivo y capacidad de réplica constructiva.'),"
        
        "(3, 'dim_1_hipotesis', 'Formulación de Hipótesis y Metodología', 50.0, 'No define variables ni formula hipótesis contrastables.', 'Formula preguntas guiadas y sigue instrucciones básicas.', 'Diseña planes de indagación y formula hipótesis válidas.', 'Pensamiento experimental riguroso y autónomo.'),"
        "(3, 'dim_2_evidencia', 'Análisis de Evidencias y Conclusiones', 50.0, 'Conclusiones no fundamentadas en los datos obtenidos.', 'Registra observaciones pero le cuesta relacionar variables.', 'Interpreta gráficos y extrae conclusiones coherentes.', 'Modela fenómenos empíricos y discute fuentes de error.'),"

        "(4, 'dim_1_equipo', 'Trabajo en Equipo y Escucha Activa', 35.0, 'Aislamiento o actitudes individualistas obstructivas.', 'Colabora de forma pasiva en el grupo.', 'Aporta activamente y escucha las ideas de otros.', 'Fomenta la sinergia grupal y motiva a sus compañeros.'),"
        "(4, 'dim_2_autorregulacion', 'Autorregulación y Manejo Emocional', 35.0, 'Reacciones explosivas o frustración desbordada.', 'Le cuesta mantener la calma bajo presión pero cede.', 'Maneja adecuadamente situaciones tensas o desacuerdos.', 'Madurez emocional sobresaliente y mediación asertiva.'),"
        "(4, 'dim_3_responsabilidad', 'Responsabilidad y Respeto Comunitario', 30.0, 'Incumplimiento de normas y faltas de respeto.', 'Cumple con deberes mínimos tras llamados de atención.', 'Respetuoso de acuerdos pedagógicos y puntual.', 'Ejemplo de civismo, ética y cuidado del entorno.');"
    )
    sql_lines.append("")

    # Generación de 230 Estudiantes
    sql_lines.append("-- 4. Insertar 230 Estudiantes")
    distribucion_grados = [
        (5, 32), (6, 33), (7, 33), (8, 33), (9, 33), (10, 33), (11, 33)
    ]
    
    estudiantes = []
    est_id = 1
    doc_base = 1025800000

    for grado, cantidad in distribucion_grados:
        edad_base = grado + 5  # 5to -> 10 años, 11vo -> 16 años
        curso_id = grado - 4   # 1 a 7
        for _ in range(cantidad):
            genero = random.choice(["Masculino", "Femenino"])
            if genero == "Masculino":
                nombre = random.choice(NOMBRES_MASC) + " " + random.choice(NOMBRES_MASC)
                pronombre = "él"
            else:
                nombre = random.choice(NOMBRES_FEM) + " " + random.choice(NOMBRES_FEM)
                pronombre = "ella"
            
            apellidos = random.choice(APELLIDOS) + " " + random.choice(APELLIDOS)
            edad = edad_base + random.choice([0, 0, 1])
            doc_num = f"TI-{doc_base + est_id}"
            uuid_anon = f"EST_{est_id:04d}_{random.randint(1000, 9999):x}"
            acudiente = f"{random.choice(NOMBRES_FEM if genero == 'Masculino' else NOMBRES_MASC)} {apellidos.split()[0]}"
            contacto = f"31{random.randint(0, 9)}{random.randint(1000000, 9999999)}"
            
            est = {
                "id": est_id,
                "uuid": uuid_anon,
                "doc": doc_num,
                "nombres": nombre,
                "apellidos": apellidos,
                "nombre_completo": f"{nombre} {apellidos}",
                "genero": genero,
                "pronombre": pronombre,
                "edad": edad,
                "grado": grado,
                "curso_id": curso_id,
                "acudiente": acudiente,
                "contacto": contacto
            }
            estudiantes.append(est)

            sql_lines.append(
                f"INSERT INTO estudiantes (id, uuid_anonimo, tipo_documento, numero_documento, nombres, apellidos, genero, pronombre, edad, grado_actual, acudiente_nombre, acudiente_contacto) "
                f"VALUES ({est_id}, '{uuid_anon}', 'TI', '{doc_num}', '{nombre}', '{apellidos}', '{genero}', '{pronombre}', {edad}, {grado}, '{acudiente}', '{contacto}');"
            )
            
            # Matrícula a curso
            sql_lines.append(
                f"INSERT INTO matriculas_curso (estudiante_id, curso_id, anio_lectivo) VALUES ({est_id}, {curso_id}, 2026);"
            )

            # Matrícula a clases según grado
            # Clases generales para todos: Matemáticas(1), Lenguaje(2), Sociales(3), Inglés(7), Ética(8)
            clases_estudiante = [1, 2, 3, 7, 8]
            if grado <= 9:
                clases_estudiante.append(4)  # Ciencias Naturales
            else:
                clases_estudiante.extend([5, 6])  # Química y Física en 10º y 11º

            for cid in clases_estudiante:
                sql_lines.append(
                    f"INSERT INTO matriculas_clase (estudiante_id, clase_id, anio_lectivo) VALUES ({est_id}, {cid}, 2026);"
                )
            
            est_id += 1

    sql_lines.append("")

    # Generación de Reportes a lo largo de 2026
    sql_lines.append("-- 5. Insertar Cientos de Reportes Temporales del Año Lectivo 2026")
    
    plantillas_reportes = [
        # (tipo, rubrica_id, dims_scores, texto_template, anon_template)
        (
            "matematicas_exito",
            1,
            {"dim_1_logica": 4.8, "dim_2_resolucion": 4.6, "dim_3_precision": 4.5},
            "Hoy {nombre} demostró un excelente dominio al resolver problemas de ecuaciones. Explicó con mucha claridad su procedimiento ante el salón.",
            "Hoy [ESTUDIANTE] demostró un excelente dominio al resolver problemas de ecuaciones. Explicó con mucha claridad su procedimiento ante el salón."
        ),
        (
            "matematicas_dificultad",
            1,
            {"dim_1_logica": 2.8, "dim_2_resolucion": 2.5, "dim_3_precision": 3.0},
            "Se evidenció que a {nombre} le cuesta bastante el manejo de fracciones y signos negativos. Mostró frustración al no obtener el resultado esperado.",
            "Se evidenció que a [ESTUDIANTE] le cuesta bastante el manejo de fracciones y signos negativos. Mostró frustración al no obtener el resultado esperado."
        ),
        (
            "lenguaje_lectura",
            2,
            {"dim_1_comprension": 4.5, "dim_2_cohesion": 4.2, "dim_3_oralidad": 4.0},
            "{nombre} realizó un ensayo sobresaliente sobre la literatura colombiana contemporánea, demostrando un pensamiento crítico maduro.",
            "[ESTUDIANTE] realizó un ensayo sobresaliente sobre la literatura colombiana contemporánea, demostrando un pensamiento crítico maduro."
        ),
        (
            "lenguaje_dificultad",
            2,
            {"dim_1_comprension": 2.6, "dim_2_cohesion": 2.7, "dim_3_oralidad": 3.2},
            "{nombre} presentó dificultades notables en la coherencia y ortografía de su reporte escrito. Le cuesta organizar párrafos secuenciales.",
            "[ESTUDIANTE] presentó dificultades notables en la coherencia y ortografía de su reporte escrito. Le cuesta organizar párrafos secuenciales."
        ),
        (
            "convivencia_conflicto",
            4,
            {"dim_1_equipo": 2.0, "dim_2_autorregulacion": 1.8, "dim_3_responsabilidad": 2.5},
            "Durante el descanso se presentó un altercado fuerte entre {nombre} y {companero}. Hubo gritos y empujones por un desacuerdo deportivo.",
            "Durante el descanso se presentó un altercado fuerte entre [ESTUDIANTE] y [COMPANERO_1]. Hubo gritos y empujones por un desacuerdo deportivo."
        ),
        (
            "convivencia_trabajo_equipo",
            4,
            {"dim_1_equipo": 4.7, "dim_2_autorregulacion": 4.5, "dim_3_responsabilidad": 4.8},
            "{nombre} mostró un liderazgo excepcional y gran empatía para integrar a todos los compañeros en la actividad colaborativa.",
            "[ESTUDIANTE] mostró un liderazgo excepcional y gran empatía para integrar a todos los compañeros en la actividad colaborativa."
        ),
        (
            "asunto_personal_emocional",
            4,
            {"dim_1_equipo": 3.0, "dim_2_autorregulacion": 3.0, "dim_3_responsabilidad": 3.5},
            "Noté a {nombre} bastante desanimado y distraído el día de hoy. Al conversar en privado mencionó problemas familiares que le quitan el sueño.",
            "Noté a [ESTUDIANTE] bastante desanimado y distraído el día de hoy. Al conversar en privado mencionó problemas familiares que le quitan el sueño."
        )
    ]

    reporte_id = 1
    # Generar reportes periódicos para el año 2026 entre Feb 2 y Oct 30
    fechas_muestreo = [
        date(2026, 2, 9), date(2026, 2, 23),
        date(2026, 3, 9), date(2026, 3, 23),
        date(2026, 4, 6), date(2026, 4, 20),
        date(2026, 5, 4), date(2026, 5, 18),
        date(2026, 6, 1), date(2026, 6, 15),
        date(2026, 8, 10), date(2026, 8, 24),
        date(2026, 9, 7), date(2026, 9, 21),
        date(2026, 10, 5), date(2026, 10, 19)
    ]

    for est in estudiantes:
        # Cada estudiante recibe entre 3 y 7 observaciones a lo largo del año
        num_reportes = random.randint(3, 7)
        fechas_est = sorted(random.sample(fechas_muestreo, num_reportes))
        
        companeros_posibles = [e for e in estudiantes if e["curso_id"] == est["curso_id"] and e["id"] != est["id"]]

        for f in fechas_est:
            plantilla = random.choice(plantillas_reportes)
            rubrica_id = plantilla[1]
            calificaciones = plantilla[2].copy()

            # Variación aleatoria leve en notas
            for k in calificaciones:
                ruido = round(random.uniform(-0.4, 0.4), 1)
                calificaciones[k] = max(0.0, min(5.0, round(calificaciones[k] + ruido, 1)))

            companero = random.choice(companeros_posibles)["nombre_completo"] if companeros_posibles else "un compañero"
            
            texto_orig = plantilla[3].format(nombre=est["nombre_completo"], companero=companero)
            texto_anon = plantilla[4]

            clase_id = 1 if rubrica_id == 1 else (2 if rubrica_id == 2 else (4 if rubrica_id == 3 else 8))
            
            calif_json = json.dumps(calificaciones).replace("'", "''")
            meta_json = json.dumps({"metodo_entrada": "VOZ_STT", "calificacion_asistida": True}).replace("'", "''")

            sql_lines.append(
                f"INSERT INTO reportes (id, uuid_anonimo, estudiante_id, curso_id, clase_id, rubrica_id, fecha, texto_original, texto_anonimizado, calificaciones_dimensiones, metadata_adicional) "
                f"VALUES ({reporte_id}, '{est['uuid']}', {est['id']}, {est['curso_id']}, {clase_id}, {rubrica_id}, '{f.isoformat()}', '{texto_orig}', '{texto_anon}', '{calif_json}', '{meta_json}');"
            )
            reporte_id += 1

    # Insertar Modelos de Informe predeterminados
    sql_lines.append("")
    sql_lines.append("-- 6. Insertar Modelos de Informe Preconfigurados")
    sql_lines.append(
        "INSERT INTO modelos_informe (nombre, descripcion, tipo_informe, prompt_base) VALUES "
        "('Informe de Rendimiento Trimestral para Padres', 'Informe pedagógico formativo y cercano, destacando fortalezas y plan de acción para el hogar.', 'INDIVIDUAL', 'Redactar un informe comprensivo y motivador dirigido a los padres de familia de [NOMBRE_ESTUDIANTE]. Describir su evolución en el trimestre, destacar sus logros principales y brindar recomendaciones prácticas para apoyar su proceso educativo en casa sin sobrecargarle.'),"
        "('Informe Diagnóstico de Clima de Aula y Convivencia', 'Evaluación grupal sobre trabajo en equipo, autorregulación y cohesión de aula.', 'AGREGADO', 'Analizar el desempeño y clima social del grupo. Señalar las materias con mayor solidez colectiva, los patrones de convivencia observados y estrategias recomendadas para el director de grupo.');"
    )

    return "\n".join(sql_lines)

if __name__ == "__main__":
    contenido = generar_sql()
    with open("database/seed_data.sql", "w", encoding="utf-8") as f:
        f.write(contenido)
    print("¡database/seed_data.sql generado exitosamente!")
