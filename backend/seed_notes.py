"""
Script para crear datos de ejemplo del sistema de notas
Ejecutar: python seed_notes.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Note, NoteCollection, NoteHierarchy, User, NoteType, CollectionType
from database import Base, engine

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_notes():
    """Crear datos de ejemplo para el sistema de notas"""

    print("🌱 Iniciando seed de notas...")

    # Buscar usuario demo (o crear uno)
    user = db.query(User).filter(User.email == "demo@example.com").first()
    if not user:
        print("⚠️  Usuario demo no encontrado. Ejecuta seed_data.py primero.")
        return

    print(f"✅ Usuario encontrado: {user.username}")

    # ============================================================================
    # COLECCIÓN 1: TEMARIO - TEMA 1 CONSTITUCIÓN
    # ============================================================================

    print("\n📚 Creando colección: Temario Tema 1...")

    col_temario = NoteCollection(
        user_id=user.id,
        name="Tema 1 - La Constitución Española",
        description="Temario completo del primer tema de oposición",
        collection_type=CollectionType.TEMARIO,
        is_public=True
    )
    db.add(col_temario)
    db.commit()
    db.refresh(col_temario)

    # Notas del temario
    notas_temario = [
        {
            "title": "1. La Constitución Española de 1978",
            "type": NoteType.SECTION,
            "content": None,
        },
        {
            "title": "1.1 Antecedentes históricos",
            "type": NoteType.CONTENT,
            "content": """# Antecedentes Históricos de la Constitución

La Constitución Española de 1978 es el resultado de un proceso histórico de transición democrática.

## Contexto Histórico

Tras la muerte del dictador Francisco Franco en 1975, España inició un proceso de transición hacia la democracia. Este período estuvo marcado por:

- **1976**: Ley para la Reforma Política
- **1977**: Primeras elecciones democráticas
- **1978**: Aprobación de la Constitución

## Importancia

La Constitución supuso:
- El establecimiento de un Estado de Derecho
- La garantía de derechos fundamentales
- La separación de poderes
- El reconocimiento de las autonomías""",
            "tags": "importante,examen,básico",
        },
        {
            "title": "1.2 Estructura de la Constitución",
            "type": NoteType.CONTENT,
            "content": """# Estructura de la Constitución Española

La Constitución Española se divide en:

## Título Preliminar
Define los principios fundamentales del Estado

## Título I - Derechos y Deberes Fundamentales
- Artículos 10-55
- Derechos fundamentales y libertades públicas
- Principios rectores de la política social

## Título II - La Corona
- Artículos 56-65
- Funciones del Rey

## Otros Títulos
- Cortes Generales (III)
- Gobierno y Administración (IV)
- Relaciones entre Gobierno y Cortes (V)
- Poder Judicial (VI)
- Economía y Hacienda (VII)
- Organización Territorial (VIII)
- Tribunal Constitucional (IX)
- Reforma Constitucional (X)""",
            "tags": "estructura,importante",
        },
        {
            "title": "2. Derechos Fundamentales",
            "type": NoteType.SECTION,
            "content": None,
        },
        {
            "title": "2.1 Derecho a la vida - Art. 15",
            "type": NoteType.CONTENT,
            "content": """# Artículo 15 - Derecho a la Vida

**Artículo 15 CE**: *Todos tienen derecho a la vida y a la integridad física y moral, sin que, en ningún caso, puedan ser sometidos a tortura ni a penas o tratos inhumanos o degradantes. Queda abolida la pena de muerte, salvo lo que puedan disponer las leyes penales militares para tiempos de guerra.*

## Contenido del Derecho

El artículo 15 protege:
- **Derecho a la vida**: Bien jurídico fundamental
- **Integridad física y moral**: Protección contra torturas
- **Abolición pena de muerte**: Con excepción en tiempos de guerra

## Jurisprudencia Relevante

- STC 53/1985: Sobre el aborto
- STC 120/1990: Sobre huelga de hambre
- STC 154/2002: Sobre eutanasia

## Casos Prácticos

Este derecho es **absoluto** y no admite restricciones, salvo las contempladas en la propia Constitución.""",
            "tags": "importante,examen,jurisprudencia",
            "article_number": "Art. 15 CE",
            "legal_reference": "BOE-A-1978-31229",
        },
    ]

    print("  📝 Creando notas del temario...")
    hierarchy_nodes = []
    parent_section = None

    for i, nota_data in enumerate(notas_temario):
        nota = Note(
            user_id=user.id,
            title=nota_data["title"],
            content=nota_data.get("content"),
            note_type=nota_data["type"],
            tags=nota_data.get("tags"),
            legal_reference=nota_data.get("legal_reference"),
            article_number=nota_data.get("article_number")
        )
        db.add(nota)
        db.commit()
        db.refresh(nota)

        # Determinar parent_id
        if nota.note_type == NoteType.SECTION:
            parent_id = None
            parent_section = None
        else:
            # Si hay una sección previa, usarla como padre
            if hierarchy_nodes:
                for h in reversed(hierarchy_nodes):
                    node_nota = db.query(Note).filter(Note.id == h.note_id).first()
                    if node_nota.note_type == NoteType.SECTION:
                        parent_section = h
                        break
            parent_id = parent_section.id if parent_section else None

        # Crear jerarquía
        hierarchy = NoteHierarchy(
            collection_id=col_temario.id,
            note_id=nota.id,
            parent_id=parent_id,
            order_index=i,
            is_featured=(nota_data.get("tags") and "importante" in nota_data.get("tags", ""))
        )
        db.add(hierarchy)
        db.commit()
        db.refresh(hierarchy)
        hierarchy_nodes.append(hierarchy)

        print(f"    ✓ {nota.title}")

    # ============================================================================
    # COLECCIÓN 2: NORMATIVA - CONSTITUCIÓN COMPLETA
    # ============================================================================

    print("\n⚖️  Creando colección: Constitución Completa...")

    col_normativa = NoteCollection(
        user_id=user.id,
        name="Constitución Española - Texto Completo",
        description="Normativa completa de la Constitución Española de 1978",
        collection_type=CollectionType.NORMATIVA,
        is_public=True
    )
    db.add(col_normativa)
    db.commit()
    db.refresh(col_normativa)

    # Reutilizar la nota del Art. 15 en la colección de normativa
    print("  📝 Reutilizando nota del Art. 15 en normativa...")

    # Buscar la nota del Art. 15
    nota_art15 = db.query(Note).filter(
        Note.user_id == user.id,
        Note.article_number == "Art. 15 CE"
    ).first()

    if nota_art15:
        # Crear nueva jerarquía para la misma nota en diferente colección
        hierarchy_normativa = NoteHierarchy(
            collection_id=col_normativa.id,
            note_id=nota_art15.id,
            parent_id=None,
            order_index=0,
            is_featured=True  # Destacada en normativa también
        )
        db.add(hierarchy_normativa)
        db.commit()

        print(f"    ✓ La nota '{nota_art15.title}' ahora aparece en ambas colecciones")

    # Añadir más artículos a normativa
    notas_normativa_extra = [
        {
            "title": "Art. 1 - Forma de Estado",
            "content": """# Artículo 1 - Forma de Estado

**Artículo 1 CE**:

1. España se constituye en un Estado social y democrático de Derecho, que propugna como valores superiores de su ordenamiento jurídico la libertad, la justicia, la igualdad y el pluralismo político.

2. La soberanía nacional reside en el pueblo español, del que emanan los poderes del Estado.

3. La forma política del Estado español es la Monarquía parlamentaria.

## Valores Superiores

- **Libertad**
- **Justicia**
- **Igualdad**
- **Pluralismo político**

## Características del Estado

- **Social**: Intervención en economía y derechos sociales
- **Democrático**: Soberanía popular
- **De Derecho**: Sometimiento a la ley""",
            "article_number": "Art. 1 CE",
            "legal_reference": "BOE-A-1978-31229",
            "tags": "fundamental,examen",
        },
        {
            "title": "Art. 14 - Igualdad ante la ley",
            "content": """# Artículo 14 - Igualdad

**Artículo 14 CE**: *Los españoles son iguales ante la ley, sin que pueda prevalecer discriminación alguna por razón de nacimiento, raza, sexo, religión, opinión o cualquier otra condición o circunstancia personal o social.*

## Principio de Igualdad

Este artículo establece:
- Igualdad formal ante la ley
- Prohibición de discriminación
- Cláusula abierta de no discriminación

## Causas de Discriminación Prohibidas

- Nacimiento
- Raza
- Sexo
- Religión
- Opinión
- Cualquier otra condición personal o social

## Jurisprudencia

- STC 22/1981: Primera sentencia sobre igualdad
- STC 128/1987: Igualdad material
- STC 59/2008: Igualdad de género""",
            "article_number": "Art. 14 CE",
            "legal_reference": "BOE-A-1978-31229",
            "tags": "fundamental,examen,importante",
        },
    ]

    print("  📝 Creando artículos adicionales...")
    for i, nota_data in enumerate(notas_normativa_extra, start=1):
        nota = Note(
            user_id=user.id,
            title=nota_data["title"],
            content=nota_data["content"],
            note_type=NoteType.CONTENT,
            tags=nota_data.get("tags"),
            legal_reference=nota_data.get("legal_reference"),
            article_number=nota_data.get("article_number")
        )
        db.add(nota)
        db.commit()
        db.refresh(nota)

        hierarchy = NoteHierarchy(
            collection_id=col_normativa.id,
            note_id=nota.id,
            parent_id=None,
            order_index=i,
            is_featured=("importante" in nota_data.get("tags", ""))
        )
        db.add(hierarchy)
        db.commit()

        print(f"    ✓ {nota.title}")

    print("\n✨ Seed de notas completado!")
    print(f"   📚 Colecciones creadas: 2")
    print(f"   📝 Notas creadas: {len(notas_temario) + len(notas_normativa_extra)}")
    print(f"   🔗 Nota reutilizada: Art. 15 CE (aparece en 2 colecciones)")


if __name__ == "__main__":
    try:
        seed_notes()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
