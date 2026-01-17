"""
Script para crear todos los temarios como Syllabi en la base de datos
"""

import json
from database import SessionLocal
from models import User, Syllabus, StructuredTopic

# Datos de los temarios (extraídos de los PDFs)
TEMARIOS = {
    "Anexo_III_Técnicos de Informática": {
        "name": "Técnicos de Informática - Anexo III",
        "description": "Cuerpo de Funcionarios Técnicos, Escala Técnica de Gestión. Incluye materias comunes y específicas de informática, programación, redes y sistemas.",
        "comunes": [
            "La Constitución Española de 1978: estructura y contenido. Valores superiores y principios inspiradores. El Estado Social y Democrático de Derecho. La Corona. Las Cortes Generales. El Poder Judicial. Derechos y libertades. Deberes de los ciudadanos. Principios rectores de la política social y económica. Garantías. Defensor del Pueblo.",
            "La organización territorial del Estado. Gobierno de la Nación y Administración General del Estado. Comunidades Autónomas. Administración Local. Las relaciones entre los entes territoriales. Especial referencia a la comarcalización de Aragón.",
            "El Estatuto de Autonomía de Aragón: naturaleza y contenido. Competencias de la Comunidad Autónoma. La reforma del Estatuto. La organización institucional de la Comunidad Autónoma de Aragón. Las Cortes y el Justicia de Aragón.",
            "El Presidente y el Gobierno de Aragón. Los Consejeros. La Administración Pública de la Comunidad Autónoma. Los órganos administrativos: su régimen y el ejercicio de las competencias.",
            "La Unión Europea. Antecedentes y evolución histórica. Las fuentes del Derecho de la Unión Europea. Las Instituciones de la Unión Europea. La participación de las Comunidades Autónomas en la aplicación del Derecho Comunitario.",
            "Ley del Procedimiento Administrativo Común de las Administraciones Públicas: ámbito de aplicación y principios generales. Los interesados en el procedimiento. Términos y plazos.",
            "La iniciación del procedimiento. Ordenación e instrucción del procedimiento. Terminación del procedimiento.",
            "El régimen del silencio administrativo. Los recursos administrativos. Las reclamaciones económico-administrativas.",
            "Los contratos del sector público: concepto, tipos y régimen jurídico. La contratación electrónica. Preparación, adjudicación y ejecución de los contratos administrativos.",
            "Los bienes de las Administraciones Públicas. Régimen jurídico del patrimonio de las Administraciones Públicas. El dominio público. El patrimonio de las entidades locales."
        ],
        "especificos": [
            "La protección de datos personales. Régimen jurídico. El Reglamento (UE) 2016/679 del Parlamento Europeo y del Consejo. La Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales. Derechos de los ciudadanos. La Agencia Española de Protección de Datos.",
            "La sociedad de la información y sociedad del conocimiento. Comercio electrónico, banca digital y firma electrónica.",
            "Administración electrónica. Marco europeo: Declaración de Tallin. Programa ISA2. Marco español: Ley 39/2015 y 40/2015. Marco autonómico: Decreto Legislativo 2/2024 (Aragón Digital). Sede electrónica. Registro electrónico. Notificaciones electrónicas. Identificación y firma electrónica. Representación. Certificado y sello electrónicos.",
            "La administración electrónica en la Comunidad Autónoma de Aragón: El Sistema de Información Administrativa y portal del Gobierno de Aragón. El Registro General Electrónico de la Administración de la Comunidad Autónoma de Aragón. Tramitación electrónica de procedimientos. Procedimientos sobre gestión de personal.",
            "Políticas de igualdad de género. La Ley Orgánica 3/2007, de 22 de marzo, para la igualdad efectiva de mujeres y hombres. Políticas contra la violencia de género. Políticas de atención a personas con discapacidad y/o dependencia.",
            "Arquitectura y organización de computadores. Componentes internos y externos. Unidad de control, unidad aritmético-lógica, buses, memorias y periféricos. Tipos de microprocesadores y arquitecturas CPU (x86, ARM). Interfaces y buses estándar. Diseño lógico.",
            "Sistemas operativos. Características y elementos constitutivos. Gestión de procesos, memoria y entrada/salida. Sistema de archivos. Sistemas operativos de uso común: Linux y Windows.",
            "Arquitectura e infraestructura de las TIC. Estructura de comunicaciones. Acceso a redes públicas. Redes de área local. Arquitectura Cliente/Servidor. Arquitectura multinivel. Análisis y planificación de capacidades.",
            "Algoritmos y estructuras de datos. Tipos abstractos. Vectores, pilas, colas. Árboles y grafos. Ordenación y búsqueda.",
            "Virtualización y cloud computing. Servicios en la nube: IaaS, PaaS, SaaS. Tecnologías de virtualización: hipervisores, contenedores (Docker, Kubernetes).",
            "Sistemas de gestión de bases de datos. Bases de datos relacionales. SQL. Bases de datos NoSQL. El lenguaje PL/SQL. Diccionario de datos. Herramientas de administración.",
            "Almacenamiento de datos. Arquitectura SAN y NAS. Sistemas RAID. Gestión del ciclo de vida del dato. Estrategias de backup y recuperación.",
            "Seguridad TIC. Ciberseguridad. Esquema Nacional de Seguridad. Políticas de seguridad. Análisis de riesgos. Plan de continuidad del negocio. Auditorías de seguridad.",
            "Herramientas de inteligencia artificial generativa. LLMs (GPT, LLaMA). Técnicas de prompting. RAG. Casos de uso en la Administración.",
            "Paradigmas de programación. Lenguajes más relevantes: Java, Python, .NET. Desarrollo ágil. DevOps y CI/CD.",
            "Desarrollo web. HTML, CSS, JavaScript. Frameworks frontend (React, Angular, Vue). APIs REST y GraphQL. Arquitectura de microservicios."
        ]
    },
    "Anexo_XXVI_Ejecutivos de Informática": {
        "name": "Ejecutivos de Informática - Anexo XXVI",
        "description": "Cuerpo Ejecutivo, Escala de Ayudantes de Gestión. Incluye materias comunes y específicas de informática, gestión de sistemas y soporte técnico.",
        "comunes": [
            "La Constitución Española de 1978: estructura, contenido y principios que la informan. Los derechos fundamentales y sus garantías. La Corona. Las Cortes Generales. El Poder Judicial. El Tribunal Constitucional. El Defensor del Pueblo.",
            "La organización territorial del Estado. Gobierno de la Nación y Administración General del Estado. Comunidades Autónomas. Administración Local. Las relaciones entre los entes territoriales. Especial referencia a la comarcalización de Aragón.",
            "El Estatuto de Autonomía de Aragón. La organización institucional de la Comunidad Autónoma de Aragón. Las Cortes de Aragón. El Justicia de Aragón.",
            "Los órganos de gobierno y administración de la Comunidad Autónoma de Aragón. El Presidente y el Gobierno de Aragón. Los Consejeros. La Administración Pública de la Comunidad Autónoma. La estructura administrativa. El Sector Público de la Comunidad Autónoma de Aragón.",
            "La prevención de riesgos laborales: derechos y obligaciones en materia de seguridad y salud en el trabajo."
        ],
        "especificos": [
            "La protección de datos personales. Régimen jurídico. El Reglamento (UE) 2016/679. La Ley Orgánica 3/2018. Derechos de los ciudadanos. La Agencia Española de Protección de Datos.",
            "La sociedad de la información. Comercio electrónico. La firma electrónica. Servicios electrónicos públicos.",
            "Administración electrónica en Aragón. El Sistema de Información Administrativa. Tramitación electrónica de procedimientos.",
            "Políticas de igualdad de género. Políticas contra la violencia de género. Políticas de atención a personas con discapacidad.",
            "Informática básica. Representación de la información. Sistemas de numeración. Álgebra de Boole.",
            "Arquitectura y organización de computadores. Componentes hardware. CPU, memoria, periféricos. Buses e interfaces.",
            "Sistemas operativos. Características y elementos constitutivos. Gestión de procesos y memoria. Linux y Windows.",
            "Redes de comunicaciones. Modelo OSI. Protocolos TCP/IP. Redes LAN, WAN. Internet e intranet.",
            "Algoritmos y estructuras de datos. Tipos de datos. Pilas, colas, listas. Árboles y grafos.",
            "Bases de datos relacionales. Modelo entidad-relación. SQL básico. Normalización.",
            "Sistemas de gestión de bases de datos. Administración básica. Copias de seguridad.",
            "Desarrollo de aplicaciones. Ciclo de vida del software. Lenguajes de programación: Java, Python.",
            "Desarrollo web. HTML, CSS, JavaScript. Aplicaciones web dinámicas.",
            "Seguridad informática. Amenazas y vulnerabilidades. Medidas de protección. Copias de seguridad.",
            "Ofimática. Procesadores de texto. Hojas de cálculo. Presentaciones. Herramientas colaborativas."
        ]
    },
    "Anexo_XXVII_Delineantes": {
        "name": "Delineantes - Anexo XXVII",
        "description": "Cuerpo Ejecutivo, Escala de Ayudantes Facultativos. Incluye materias comunes y específicas de delineación, CAD, BIM, cartografía y construcción.",
        "comunes": [
            "La Constitución Española de 1978: estructura, contenido y principios que la informan. Los derechos fundamentales y sus garantías. La Corona. Las Cortes Generales. El Poder Judicial. El Tribunal Constitucional. El Defensor del Pueblo.",
            "La organización territorial del Estado. Gobierno de la Nación y Administración General del Estado. Comunidades Autónomas. Administración Local. Las relaciones entre los entes territoriales. Especial referencia a la comarcalización de Aragón.",
            "El Estatuto de Autonomía de Aragón. La organización institucional de la Comunidad Autónoma de Aragón. Las Cortes de Aragón. El Justicia de Aragón.",
            "Los órganos de gobierno y administración de la Comunidad Autónoma de Aragón. El Presidente y el Gobierno de Aragón. Los Consejeros. La Administración Pública de la Comunidad Autónoma. La estructura administrativa.",
            "La prevención de riesgos laborales: derechos y obligaciones en materia de seguridad y salud en el trabajo."
        ],
        "especificos": [
            "Croquización, acotación y rotulación técnica. Técnicas básicas de dibujo a mano alzada. Digitalización del croquis. Representación de elementos constructivos. Normas y técnicas de acotación. Normas UNE, ISO y DIN. Simbología normalizada.",
            "Escalas: conceptos, tipos, normativa y aplicación práctica en la representación técnica. Definición y finalidad de la escala. Escalas en trabajos CAD y GIS.",
            "Sistemas de representación. Concepto y clasificación. Sistema diédrico. Sistema axonométrico: perspectiva isométrica, dimétrica y trimétrica. Perspectivas: cónica, caballera y militar.",
            "Secciones constructivas: representación, tipos y aplicación en proyectos de edificación y obra civil. Secciones constructivas por el Código Técnico de la Edificación. Detalles constructivos.",
            "Geometría aplicada. Sistemas de coordenadas. Tangencias y enlaces. Curvas técnicas. Aplicación en CAD.",
            "Dibujo topográfico. Planimetría y altimetría. Escalas. Representación del relieve. Curvas de nivel.",
            "Cartografía y geodesia. Sistemas de referencia. Proyecciones cartográficas. UTM, ETRS89. Norma Cartográfica de Aragón.",
            "Topografía: definición. Mapas, planos y cartas. Instrumentos topográficos. Métodos de levantamiento. Replanteo de obras.",
            "Perfiles longitudinales y transversales. Mediciones y cubicaciones. Movimiento de tierras. Aplicación del PG-3.",
            "Sistemas de información geográfica (I): conceptos generales. Datos ráster y vectoriales. Software SIG: QGIS. Gestión de capas.",
            "Sistemas de información geográfica (II). Análisis espacial. Georreferenciación. Las Infraestructuras de Datos Espaciales (IDE) e ICEAragon.",
            "Cartografía catastral urbana. Sistemas de coordenadas. Modelos de datos y metadatación. Las IDE.",
            "Movimientos y obras de tierras. Excavaciones. Esponjamiento del terreno. Elementos de contención. Aplicación CTE y PG-3.",
            "Cimentaciones y estructuras: generalidades, elementos tipos y materiales. Representación gráfica. Muros de contención. Aplicación CTE.",
            "Muros de cerramiento y soporte: generalidades, materiales, elementos, aparejos y separaciones interiores. Aplicación CTE.",
            "Firmes y pavimentos. Clasificación de suelos. Aplicación PG-3.",
            "Obra civil y de edificación: elementos de la obra. Plantas, alzados, secciones y detalles.",
            "Cubiertas: tipos, elementos y materiales. Representación gráfica. Impermeabilización. Aplicación CTE.",
            "Instalaciones de fontanería y saneamiento. Representación en planos. Aplicación CTE DB-HS.",
            "Instalaciones eléctricas y de iluminación. Simbología. Representación. REBT.",
            "Instalaciones de climatización y ventilación. Representación. RITE.",
            "Instalaciones de gas. Representación. Reglamento técnico de distribución de combustibles gaseosos.",
            "Instalaciones de protección contra incendios. Representación. CTE DB-SI.",
            "Instalaciones de telecomunicaciones. ICT. Representación en planos.",
            "Escaleras. Tipos. Elementos principales. Cálculo de huella y contrahuella. Representación gráfica. Aplicación CTE.",
            "Seguridad y Salud en obras de construcción. Estudio de Seguridad y Salud. Plan de Seguridad y Salud. Representación gráfica de medidas preventivas.",
            "Documentación Técnica y Gestión de Proyectos. Partes del proyecto. Pliego de condiciones. Mediciones y presupuesto. Planos.",
            "Diseño asistido por ordenador: AutoCAD y Revit. Automatización en CAD: scripts, rutinas LISP. Bloques. Referencias.",
            "El trabajo colaborativo: BIM. Conceptos generales. Dimensiones: del 3D al 7D. Niveles LOD. Software existente."
        ]
    },
    "Anexo_XXXIV_Protección de Patrimonio": {
        "name": "Protección de Patrimonio - Anexo XXXIV",
        "description": "Cuerpo Auxiliar, Escala de Auxiliares Facultativos, Agentes de Protección de Patrimonio. Incluye materias comunes y específicas sobre patrimonio cultural aragonés.",
        "comunes": [
            "La Constitución Española de 1978: estructura y contenido. Derechos y deberes fundamentales.",
            "La organización territorial del Estado: las Comunidades Autónomas. La Administración Local.",
            "El Estatuto de Autonomía de Aragón. La organización institucional de la Comunidad Autónoma de Aragón. Las Cortes. El Justicia de Aragón.",
            "Los órganos de gobierno y administración de la Comunidad Autónoma de Aragón. El Gobierno de Aragón. La estructura administrativa.",
            "El personal de las Administraciones Públicas. Estructura y organización de la Función Pública de la Comunidad Autónoma de Aragón. Derechos y deberes de los funcionarios. Incompatibilidades. Régimen disciplinario."
        ],
        "especificos": [
            "Distribución competencial en materia de Patrimonio Cultural entre el Estado, la Comunidad Autónoma y las Entidades Locales.",
            "La Ley 3/1999, de 10 de marzo, del Patrimonio Cultural Aragonés (I y II). Disposiciones Generales. Los bienes integrantes del Patrimonio Cultural Aragonés.",
            "La Ley 3/1999, de 10 de marzo, del Patrimonio Cultural Aragonés (III). Régimen de protección y conservación del Patrimonio Cultural Aragonés.",
            "La Ley 3/1999, de 10 de marzo, del Patrimonio Cultural Aragonés (IV). Patrimonio arqueológico y paleontológico. Principales yacimientos de Aragón.",
            "La Ley 3/1999, de 10 de marzo, del Patrimonio Cultural Aragonés (V). El Patrimonio etnográfico e industrial. El Patrimonio documental y bibliográfico.",
            "Los Bienes de Interés Cultural en Aragón. Declaración, efectos y régimen jurídico. Bienes muebles e inmuebles. Conjuntos históricos.",
            "Los Museos de Aragón. Concepto, funciones y tipología. La Red de Museos de Aragón.",
            "Los Archivos de Aragón. Concepto y tipología. El Sistema de Archivos de Aragón.",
            "La protección del Patrimonio Cultural: inspección y régimen sancionador. Infracciones y sanciones.",
            "Técnicas de conservación preventiva del patrimonio. Condiciones ambientales. Almacenamiento y manipulación.",
            "Medidas de seguridad en edificios patrimoniales. Sistemas de alarma. Control de accesos. Planes de emergencia.",
            "Normativa de accesibilidad aplicada al patrimonio. Eliminación de barreras arquitectónicas.",
            "La incidencia y relación de la normativa de Prevención de Riesgos Laborales en la protección del Patrimonio.",
            "La Cartografía y Sistemas de Información Geográfica aplicados al patrimonio cultural.",
            "Organización territorial de Aragón. Principales características geográficas, históricas y culturales de las provincias aragonesas."
        ]
    }
}


def main():
    db = SessionLocal()

    try:
        # Buscar usuario alejandro
        user = db.query(User).filter(User.username == "alejandro").first()
        if not user:
            print("Error: Usuario 'alejandro' no encontrado")
            return

        print(f"Usuario encontrado: ID={user.id}")
        print()

        for temario_key, temario_data in TEMARIOS.items():
            print(f"{'='*60}")
            print(f"Creando: {temario_data['name']}")
            print('='*60)

            # Verificar si ya existe
            existing = db.query(Syllabus).filter(
                Syllabus.user_id == user.id,
                Syllabus.name == temario_data['name']
            ).first()

            if existing:
                print(f"  Ya existe con ID: {existing.id}, saltando...")
                continue

            # Crear syllabus
            syllabus = Syllabus(
                name=temario_data['name'],
                description=temario_data['description'],
                user_id=user.id,
                is_public=False
            )
            db.add(syllabus)
            db.flush()
            print(f"  Syllabus creado con ID: {syllabus.id}")

            # Crear categoría "Materias Comunes"
            comunes_cat = StructuredTopic(
                user_id=user.id,
                syllabus_id=syllabus.id,
                title="Materias Comunes",
                content=f"Programa de materias comunes ({len(temario_data['comunes'])} temas)",
                order_index=1,
                parent_id=None
            )
            db.add(comunes_cat)
            db.flush()

            # Crear temas comunes
            for i, tema in enumerate(temario_data['comunes'], 1):
                topic = StructuredTopic(
                    user_id=user.id,
                    syllabus_id=syllabus.id,
                    title=f"Tema {i}. {tema}",
                    order_index=i,
                    parent_id=comunes_cat.id
                )
                db.add(topic)

            print(f"  Creados {len(temario_data['comunes'])} temas comunes")

            # Crear categoría "Materias Específicas"
            especificos_cat = StructuredTopic(
                user_id=user.id,
                syllabus_id=syllabus.id,
                title="Materias Específicas",
                content=f"Programa de materias específicas ({len(temario_data['especificos'])} temas)",
                order_index=2,
                parent_id=None
            )
            db.add(especificos_cat)
            db.flush()

            # Crear temas específicos
            for i, tema in enumerate(temario_data['especificos'], 1):
                topic = StructuredTopic(
                    user_id=user.id,
                    syllabus_id=syllabus.id,
                    title=f"Tema {i}. {tema}",
                    order_index=i,
                    parent_id=especificos_cat.id
                )
                db.add(topic)

            print(f"  Creados {len(temario_data['especificos'])} temas específicos")

            db.flush()
            print(f"  Total: {len(temario_data['comunes']) + len(temario_data['especificos']) + 2} elementos")
            print()

        # Commit all changes
        db.commit()
        print("="*60)
        print("¡Todos los syllabi creados correctamente!")
        print("="*60)

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
