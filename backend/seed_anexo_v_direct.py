"""
Script para crear el Syllabus del Anexo V - Arquitectos Técnicos
Inserción directa en la base de datos (sin API)
"""

from database import SessionLocal
from models import User, Syllabus, StructuredTopic
from datetime import datetime

# Temas comunes (10)
MATERIAS_COMUNES = [
    "Tema 1. La Constitución Española de 1978: Estructura y contenido. Derechos y deberes fundamentales. Su garantía y suspensión. La reforma constitucional. El Tribunal Constitucional. El Defensor del Pueblo.",
    "Tema 2. La Corona. Las Cortes Generales: composición, atribuciones y funcionamiento. El Poder Judicial. El Gobierno y la Administración. Relaciones del Gobierno con las Cortes Generales.",
    "Tema 3. La organización territorial del Estado en la Constitución. Las Comunidades Autónomas. Las relaciones entre el Estado y las Comunidades Autónomas. La financiación de las Comunidades Autónomas.",
    "Tema 4. La Administración Local: Provincias, Municipios y otras Entidades.",
    "Tema 5. El Estatuto de Autonomía de Aragón: naturaleza y contenido. Competencias de la Comunidad Autónoma. Organización institucional de la Comunidad Autónoma de Aragón: Las Cortes, el Presidente, la Diputación General y el Justicia de Aragón. Administración Local aragonesa.",
    "Tema 6. Políticas de igualdad de género. La Ley Orgánica 3/2007, de 22 de marzo, para la igualdad efectiva de mujeres y hombres. Políticas contra la violencia de género. La Ley Orgánica 1/2004, de 28 de diciembre, de medidas de protección integral contra la violencia de género. Políticas dirigidas a la atención de las personas con discapacidad y/o dependientes.",
    "Tema 7. El personal al servicio de las Administraciones Públicas. El Estatuto Básico del Empleado Público. Derechos y deberes de los funcionarios. Sistema retributivo. Régimen de incompatibilidades.",
    "Tema 8. Los procedimientos administrativos: el procedimiento administrativo común y el procedimiento sancionador. Revisión de los actos administrativos.",
    "Tema 9. El régimen patrimonial de las Administraciones Públicas. El dominio público y el patrimonio privado. Los contratos del sector público: clases, preparación, adjudicación y ejecución.",
    "Tema 10. La responsabilidad de las Administraciones Públicas."
]

# Temas específicos (45)
MATERIAS_ESPECIFICAS = [
    "Tema 1. Ley Orgánica de Educación: estructura y principios. Los centros docentes. Los centros privados. Los centros privados concertados.",
    "Tema 2. Los órganos de gobierno de los centros públicos. Órganos colegiados. El Claustro de profesores. El Consejo Escolar. El equipo directivo. Órganos de coordinación docente.",
    "Tema 3. Estructura del sistema educativo. Educación infantil. Educación primaria. Educación secundaria obligatoria. Bachillerato. Formación profesional.",
    "Tema 4. Evaluación del sistema educativo. Evaluación general del sistema educativo. Evaluaciones generales de diagnóstico. Evaluación de los centros. Evaluación de la función directiva.",
    "Tema 5. Ordenación de las enseñanzas de régimen especial en la Comunidad Autónoma de Aragón. Enseñanzas artísticas. Enseñanzas de idiomas. Enseñanzas deportivas.",
    "Tema 6. El planeamiento urbanístico: figuras de planeamiento.",
    "Tema 7. La clasificación urbanística del suelo.",
    "Tema 8. La ejecución del planeamiento: sistemas de gestión.",
    "Tema 9. La edificación: licencias y autorizaciones.",
    "Tema 10. El Código Técnico de la Edificación: estructura y contenido. Documentos Básicos.",
    "Tema 11. La seguridad estructural en la edificación. Acciones en la edificación. Cimentaciones.",
    "Tema 12. La seguridad estructural: fábrica. Acero. Madera.",
    "Tema 13. La seguridad en caso de incendio: propagación interior y exterior. Evacuación. Instalaciones de protección contra incendios.",
    "Tema 14. La seguridad de utilización y accesibilidad: seguridad frente al riesgo de caídas, de impacto, de aprisionamiento, de iluminación inadecuada. Seguridad frente al riesgo causado por vehículos. Seguridad frente al riesgo causado por la acción del rayo.",
    "Tema 15. Salubridad: protección frente a la humedad, recogida y evacuación de residuos, calidad del aire interior, suministro de agua, evacuación de aguas.",
    "Tema 16. Protección frente al ruido.",
    "Tema 17. Ahorro de energía: limitación de la demanda energética, rendimiento de las instalaciones térmicas, eficiencia energética de las instalaciones de iluminación, contribución solar mínima de agua caliente sanitaria, contribución fotovoltaica mínima de energía eléctrica.",
    "Tema 18. El Reglamento de Instalaciones Térmicas en los Edificios (RITE).",
    "Tema 19. Normativa de accesibilidad en Aragón.",
    "Tema 20. La ordenación de la edificación. Agentes de la edificación. Responsabilidades y garantías.",
    "Tema 21. La construcción: preparación del terreno, excavación, movimiento de tierras.",
    "Tema 22. Cimentaciones: superficiales y profundas. Contenciones.",
    "Tema 23. Estructuras de hormigón armado y pretensado. Estructuras de acero. Estructuras de madera. Estructuras mixtas. Estructuras de fábrica.",
    "Tema 24. Cerramientos y particiones. Fachadas. Cubiertas. Tabiquería.",
    "Tema 25. Acabados interiores: revestimientos, pavimentos, falsos techos.",
    "Tema 26. Carpinterías exteriores e interiores. Vidriería. Cerrajería.",
    "Tema 27. Instalaciones de fontanería. Aparatos sanitarios.",
    "Tema 28. Instalaciones de saneamiento. Evacuación de aguas residuales y pluviales.",
    "Tema 29. Instalaciones de electricidad en baja tensión. Reglamento Electrotécnico de Baja Tensión.",
    "Tema 30. Instalaciones de climatización y ventilación.",
    "Tema 31. Instalaciones de gas. Reglamento técnico de distribución y utilización de combustibles gaseosos.",
    "Tema 32. Instalaciones de telecomunicaciones. Infraestructura común de telecomunicaciones.",
    "Tema 33. Instalaciones de protección contra incendios.",
    "Tema 34. Instalaciones de transporte: ascensores, escaleras mecánicas y aparatos elevadores.",
    "Tema 35. La seguridad y salud en las obras de construcción. El coordinador en materia de seguridad y salud. El estudio de seguridad y salud. El plan de seguridad y salud.",
    "Tema 36. Mediciones y presupuestos de obras de edificación. Criterios de medición.",
    "Tema 37. Programación de obras. Planificación temporal. Métodos de programación: PERT, CPM, GANTT.",
    "Tema 38. Control de calidad en la edificación. Control de recepción de productos. Control de ejecución. Control de la obra terminada.",
    "Tema 39. El proyecto de obras: documentos. Estudios previos. Anteproyecto. Proyecto básico. Proyecto de ejecución.",
    "Tema 40. La dirección de obra. El libro de órdenes. El acta de replanteo. Certificaciones. Modificaciones de obra. La recepción de la obra.",
    "Tema 41. El mantenimiento de edificios. El libro del edificio. Inspección Técnica de Edificios.",
    "Tema 42. La eficiencia energética de los edificios. Certificación energética. Auditorías energéticas.",
    "Tema 43. Patología de la edificación: lesiones mecánicas, físicas, químicas y biológicas.",
    "Tema 44. La rehabilitación de edificios. Intervenciones estructurales. Refuerzos.",
    "Tema 45. El patrimonio arquitectónico. La protección del patrimonio cultural. Niveles de protección. Intervenciones en edificios protegidos."
]


def main():
    db = SessionLocal()

    try:
        # Buscar usuario alejandro
        user = db.query(User).filter(User.username == "alejandro").first()
        if not user:
            print("Error: Usuario 'alejandro' no encontrado")
            return

        print(f"Usuario encontrado: ID={user.id}")

        # Crear syllabus
        print("Creando syllabus 'Arquitectos Técnicos - Anexo V'...")
        syllabus = Syllabus(
            name="Arquitectos Técnicos - Anexo V",
            description="Temario completo para el Cuerpo de Arquitectos Técnicos de la Administración de la Comunidad Autónoma de Aragón. Incluye 10 temas de materias comunes y 45 temas de materias específicas.",
            user_id=user.id,
            is_public=False
        )
        db.add(syllabus)
        db.flush()  # Get the ID
        print(f"Syllabus creado con ID: {syllabus.id}")

        # Crear categoría "Materias Comunes"
        print("\nCreando categoría 'Materias Comunes'...")
        comunes = StructuredTopic(
            user_id=user.id,
            syllabus_id=syllabus.id,
            title="Materias Comunes",
            content="Programa de materias comunes (10 temas) para oposiciones de Arquitectos Técnicos.",
            order_index=1,
            parent_id=None
        )
        db.add(comunes)
        db.flush()
        print(f"  Categoría creada con ID: {comunes.id}")

        # Crear temas comunes
        print(f"Creando {len(MATERIAS_COMUNES)} temas comunes...")
        for i, tema in enumerate(MATERIAS_COMUNES, 1):
            topic = StructuredTopic(
                user_id=user.id,
                syllabus_id=syllabus.id,
                title=tema,
                order_index=i,
                parent_id=comunes.id
            )
            db.add(topic)
            print(f"  - Tema {i} creado")

        db.flush()

        # Crear categoría "Materias Específicas"
        print("\nCreando categoría 'Materias Específicas'...")
        especificas = StructuredTopic(
            user_id=user.id,
            syllabus_id=syllabus.id,
            title="Materias Específicas",
            content="Programa de materias específicas (45 temas) para oposiciones de Arquitectos Técnicos.",
            order_index=2,
            parent_id=None
        )
        db.add(especificas)
        db.flush()
        print(f"  Categoría creada con ID: {especificas.id}")

        # Crear temas específicos
        print(f"Creando {len(MATERIAS_ESPECIFICAS)} temas específicos...")
        for i, tema in enumerate(MATERIAS_ESPECIFICAS, 1):
            topic = StructuredTopic(
                user_id=user.id,
                syllabus_id=syllabus.id,
                title=tema,
                order_index=i,
                parent_id=especificas.id
            )
            db.add(topic)
            print(f"  - Tema {i} creado")

        # Commit all changes
        db.commit()

        print(f"\n{'='*60}")
        print(f"Syllabus creado exitosamente!")
        print(f"  - ID: {syllabus.id}")
        print(f"  - Total temas: {len(MATERIAS_COMUNES) + len(MATERIAS_ESPECIFICAS) + 2}")
        print(f"{'='*60}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
