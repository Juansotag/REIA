from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ruta_raiz_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [302, 307]
    assert response.headers["location"] == "/reportes"

def test_pagina_estudiantes():
    response = client.get("/estudiantes")
    assert response.status_code == 200
    assert "Directorio de Estudiantes" in response.text

def test_pagina_cursos_clases():
    response = client.get("/cursos-clases")
    assert response.status_code == 200
    assert "Gestión de Cursos y Clases" in response.text

def test_crud_cursos():
    # Modal nuevo curso
    res_modal = client.get("/cursos-clases/modal-curso")
    assert res_modal.status_code == 200
    assert "Nuevo Curso" in res_modal.text

    # Crear curso de prueba
    res_crear = client.post("/cursos-clases/curso", data={
        "nombre": "Prueba 11-C",
        "grado": 11,
        "seccion": "C",
        "director_curso": "Profesor Test",
        "anio_lectivo": 2026
    }, follow_redirects=True)
    assert res_crear.status_code == 200
    assert "Prueba 11-C" in res_crear.text

def test_crud_clases():
    # Modal nueva clase
    res_modal = client.get("/cursos-clases/modal-clase")
    assert res_modal.status_code == 200
    assert "Nueva Asignatura" in res_modal.text

    # Crear clase de prueba
    res_crear = client.post("/cursos-clases/clase", data={
        "nombre": "Robótica y Programación",
        "area": "Tecnología",
        "descripcion": "Pensamiento computacional"
    }, follow_redirects=True)
    assert res_crear.status_code == 200
    assert "Robótica y Programación" in res_crear.text

def test_pagina_rubricas_y_crud():
    response = client.get("/rubricas")
    assert response.status_code == 200
    assert "Rúbricas de Evaluación" in response.text

    # Modal crear rúbrica
    res_modal = client.get("/rubricas/modal-crear")
    assert res_modal.status_code == 200
    assert "Nueva Rúbrica de Evaluación" in res_modal.text

    # Crear rúbrica discreta
    res_crear = client.post("/rubricas", data={
        "nombre": "Rúbrica Discreta Test",
        "descripcion": "Evaluación ordinal",
        "tipo_escala": "DISCRETA",
        "clase_id": "",
        "dim_nombre[]": ["Dominio Temático"],
        "dim_clave[]": ["dim_dominio"],
        "dim_peso[]": ["100"],
        "dim_bajo[]": ["Nivel 1"],
        "dim_basico[]": ["Nivel 3"],
        "dim_alto[]": ["Nivel 4"],
        "dim_superior[]": ["Nivel 5"]
    }, follow_redirects=True)
    assert res_crear.status_code == 200
    assert "Rúbrica Discreta Test" in res_crear.text
    assert "Escala Discreta" in res_crear.text

def test_pagina_reportes_y_edicion():
    from app.database import SessionLocal
    from app.models import Reporte
    db = SessionLocal()
    rep = db.query(Reporte).order_by(Reporte.fecha.desc()).first()
    rep_id = rep.id
    db.close()

    response = client.get("/reportes")
    assert response.status_code == 200
    assert "Bitácora de Observaciones y Reportes" in response.text

    # Modal detalle reporte
    res_det = client.get(f"/reportes/modal-detalle/{rep_id}")
    assert res_det.status_code == 200
    assert "Detalle de la Observación" in res_det.text

    # Modal editar reporte
    res_edit_modal = client.get(f"/reportes/modal-editar/{rep_id}")
    assert res_edit_modal.status_code == 200
    assert "Editar Reporte de Observación" in res_edit_modal.text

    # Post edición
    res_edit_post = client.post(f"/reportes/{rep_id}/editar", data={
        "texto_original": "Observación editada exitosamente por el docente.",
        "fecha": "2026-10-15",
        "dim_dim_1_logica": "4.8"
    })
    assert res_edit_post.status_code == 200
    assert "Observación editada exitosamente" in res_edit_post.text

def test_pagina_informes():
    response = client.get("/informes")
    assert response.status_code == 200
    assert "Informes de Evaluación Formativa" in response.text

def test_gestion_estudiantes_curso_y_clase():
    # Modal gestionar estudiantes del curso 1
    res_modal_curso = client.get("/cursos-clases/curso/1/modal-estudiantes")
    assert res_modal_curso.status_code == 200
    assert "Asignar Estudiantes al Curso" in res_modal_curso.text

    # Asignar estudiantes 1 y 2 al curso 1
    res_post_curso = client.post("/cursos-clases/curso/1/estudiantes", data={
        "estudiante_ids[]": ["1", "2"]
    }, follow_redirects=True)
    assert res_post_curso.status_code == 200

    # Quitar estudiante 1 del curso 1
    res_del_curso = client.delete("/cursos-clases/curso/1/estudiante/1", follow_redirects=True)
    assert res_del_curso.status_code == 200

    # Modal gestionar estudiantes de la clase 1
    res_modal_clase = client.get("/cursos-clases/clase/1/modal-estudiantes")
    assert res_modal_clase.status_code == 200
    assert "Asignar Estudiantes a la Asignatura" in res_modal_clase.text

    # Asignar estudiantes a la clase 1
    res_post_clase = client.post("/cursos-clases/clase/1/estudiantes", data={
        "estudiante_ids[]": ["1", "2", "3"]
    }, follow_redirects=True)
    assert res_post_clase.status_code == 200

def test_pagina_configuracion_y_env():
    response = client.get("/configuracion")
    assert response.status_code == 200
    assert "Configuración del Sistema" in response.text
    # Verificar que NO expone las claves en texto plano en el atributo value
    assert 'value="sk-proj-' not in response.text
    assert 'value="sk-ant-' not in response.text

    # Guardar configuración en .env
    res_guardar = client.post("/configuracion/guardar", data={
        "llm_provider": "openai",
        "openai_api_key": "sk-test-key-12345",
        "anthropic_api_key": "sk-ant-test-67890",
        "stt_engine": "hybrid"
    })
    assert res_guardar.status_code == 200
    assert "guardada de forma segura en .env" in res_guardar.text

