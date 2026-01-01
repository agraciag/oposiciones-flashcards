"""
Script para crear flashcards del Tema 2 - Estatuto de Autonomía de Aragón
Artículos clave del Estatuto reformado (Ley Orgánica 5/2007)
"""

import requests
import json

API_URL = "http://localhost:7999/api"

# Crear el deck si no existe
def create_deck():
    deck_data = {
        "name": "Tema 2 - Estatuto de Autonomía de Aragón",
        "description": "Artículos clave del Estatuto reformado (LO 5/2007): organización territorial, instituciones y competencias."
    }

    response = requests.post(f"{API_URL}/decks/", json=deck_data)
    if response.status_code == 200:
        deck = response.json()
        print(f"✅ Deck creado: {deck['name']} (ID: {deck['id']})")
        return deck['id']
    else:
        # Si ya existe, intentar obtener el ID desde el listado
        print("⚠️ Deck ya existe, buscando ID...")
        response = requests.get(f"{API_URL}/decks/")
        decks = response.json()
        for deck in decks:
            if "Tema 2" in deck['name']:
                print(f"✅ Usando deck existente: {deck['name']} (ID: {deck['id']})")
                return deck['id']
        return 2  # Fallback

# Flashcards de artículos clave del Estatuto
flashcards = [
    # TÍTULO PRELIMINAR
    {
        "article": "Art. 1",
        "front": "Art. 1 EAA - ¿Qué establece sobre Aragón?",
        "back": "Aragón, como expresión de su identidad histórica y en el ejercicio del derecho a la autonomía que la Constitución reconoce a toda nacionalidad, se constituye en Comunidad Autónoma.",
        "tags": "identidad,autonomia,titulo-preliminar"
    },
    {
        "article": "Art. 2",
        "front": "Art. 2 EAA - ¿Cuál es el territorio de Aragón?",
        "back": "El territorio de Aragón es el de los municipios comprendidos en las provincias de Huesca, Zaragoza y Teruel.",
        "tags": "territorio,provincias,huesca,zaragoza,teruel"
    },
    {
        "article": "Art. 3",
        "front": "Art. 3 EAA - ¿Cuáles son los símbolos de Aragón?",
        "back": "Aragón tiene bandera, escudo e himno propios. La bandera es la tradicional de cuatro barras rojas horizontales sobre fondo amarillo. El escudo, el himno y demás símbolos se regulan por ley.",
        "tags": "simbolos,bandera,escudo,himno"
    },
    {
        "article": "Art. 7",
        "front": "Art. 7 EAA - ¿Cuál es la capital de Aragón?",
        "back": "Zaragoza es la capital de Aragón y sede de las Cortes y del Gobierno.",
        "tags": "capital,zaragoza,sede-gobierno"
    },

    # TÍTULO I - DERECHOS Y PRINCIPIOS RECTORES
    {
        "article": "Art. 12",
        "front": "Art. 12 EAA - ¿Qué derechos sociales reconoce?",
        "back": "Derecho a acceso en condiciones de igualdad a los servicios públicos aragoneses. Derecho a una renta básica. Derecho a la vivienda digna. Protección a la familia.",
        "tags": "derechos-sociales,igualdad,renta-basica,vivienda"
    },
    {
        "article": "Art. 13",
        "front": "Art. 13 EAA - ¿Qué derechos reconoce en relación con los servicios públicos?",
        "back": "Derecho de acceso, en condiciones de igualdad, a los servicios públicos aragoneses. Derecho a un buen servicio y atención en las actuaciones administrativas.",
        "tags": "servicios-publicos,administracion,calidad"
    },

    # TÍTULO II - ORGANIZACIÓN TERRITORIAL
    {
        "article": "Art. 18",
        "front": "Art. 18 EAA - ¿Cuál es la organización territorial básica?",
        "back": "El municipio es la entidad territorial básica de Aragón. La provincia es entidad local con personalidad jurídica propia, división territorial para el cumplimiento de las actividades de la Comunidad Autónoma.",
        "tags": "organizacion-territorial,municipio,provincia"
    },
    {
        "article": "Art. 19",
        "front": "Art. 19 EAA - ¿Qué son las comarcas?",
        "back": "Las comarcas son entidades locales de Aragón determinadas por la agrupación de municipios. Se crean, modifican o suprimen por ley de Cortes de Aragón.",
        "tags": "comarcas,entidades-locales,cortes"
    },

    # TÍTULO III - LAS INSTITUCIONES
    {
        "article": "Art. 32",
        "front": "Art. 32 EAA - ¿Cuáles son las instituciones de Aragón?",
        "back": "Las instituciones de autogobierno de la Comunidad Autónoma son: las Cortes, el Presidente, el Gobierno y el Justicia de Aragón.",
        "tags": "instituciones,cortes,presidente,gobierno,justicia"
    },

    # Capítulo I - LAS CORTES DE ARAGÓN
    {
        "article": "Art. 33",
        "front": "Art. 33 EAA - ¿Qué son las Cortes de Aragón?",
        "back": "Las Cortes de Aragón representan al pueblo aragonés, ejercen la potestad legislativa, aprueban los presupuestos, impulsan y controlan la acción del Gobierno, y ejercen las demás competencias que les atribuye el Estatuto.",
        "tags": "cortes,legislativo,representacion,control-gobierno"
    },
    {
        "article": "Art. 34",
        "front": "Art. 34 EAA - ¿Cuántos diputados tienen las Cortes?",
        "back": "Las Cortes de Aragón están formadas por un mínimo de 65 y un máximo de 80 diputados elegidos por sufragio universal, libre, igual, directo y secreto.",
        "tags": "cortes,diputados,elecciones,sufragio"
    },
    {
        "article": "Art. 42",
        "front": "Art. 42 EAA - ¿Cuál es la duración del mandato de las Cortes?",
        "back": "Las Cortes de Aragón son elegidas por cuatro años. Su mandato termina cuatro años después de su elección o el día de disolución.",
        "tags": "cortes,mandato,cuatro-años,disolucion"
    },

    # Capítulo II - EL PRESIDENTE
    {
        "article": "Art. 48",
        "front": "Art. 48 EAA - ¿Quién elige al Presidente de Aragón?",
        "back": "El Presidente es elegido por las Cortes de Aragón de entre sus miembros y nombrado por el Rey.",
        "tags": "presidente,eleccion,cortes,rey"
    },
    {
        "article": "Art. 49",
        "front": "Art. 49 EAA - ¿Cuáles son las funciones del Presidente?",
        "back": "Representar a Aragón, dirigir el Gobierno, nombrar y separar a sus miembros, convocar elecciones, promulgar leyes en nombre del Rey, disolver las Cortes, entre otras.",
        "tags": "presidente,funciones,gobierno,representacion"
    },

    # Capítulo III - EL GOBIERNO
    {
        "article": "Art. 53",
        "front": "Art. 53 EAA - ¿Qué es el Gobierno de Aragón?",
        "back": "El Gobierno dirige la política aragonesa y ejerce la función ejecutiva y la potestad reglamentaria de acuerdo con el Estatuto y el resto del ordenamiento jurídico.",
        "tags": "gobierno,ejecutivo,potestad-reglamentaria"
    },
    {
        "article": "Art. 54",
        "front": "Art. 54 EAA - ¿Cómo está compuesto el Gobierno?",
        "back": "El Gobierno se compone del Presidente, de los Vicepresidentes, en su caso, y de los Consejeros.",
        "tags": "gobierno,composicion,presidente,consejeros"
    },

    # Capítulo IV - EL JUSTICIA DE ARAGÓN
    {
        "article": "Art. 58",
        "front": "Art. 58 EAA - ¿Qué es el Justicia de Aragón?",
        "back": "El Justicia de Aragón es el Defensor del Pueblo de la Comunidad Autónoma, actúa con independencia en la defensa de los derechos reconocidos en el Estatuto y supervisará la actividad de la Administración.",
        "tags": "justicia,defensor-pueblo,derechos,independencia"
    },
    {
        "article": "Art. 59",
        "front": "Art. 59 EAA - ¿Cómo se elige al Justicia de Aragón?",
        "back": "Es designado por las Cortes de Aragón por mayoría de tres quintos de sus miembros. Su mandato es de cinco años.",
        "tags": "justicia,eleccion,mayoria,cinco-años"
    },

    # TÍTULO IV - COMPETENCIAS
    {
        "article": "Art. 71",
        "front": "Art. 71 EAA - ¿Qué competencias exclusivas tiene Aragón?",
        "back": "Entre otras: organización territorial, régimen local, patrimonio, cultura, turismo, vivienda, agricultura, ganadería, medio ambiente, caza y pesca, deportes, ferias y mercados.",
        "tags": "competencias-exclusivas,organizacion,cultura,agricultura"
    },
    {
        "article": "Art. 75",
        "front": "Art. 75 EAA - ¿Qué competencias tiene en educación?",
        "back": "Competencias de desarrollo normativo y ejecución en materia de enseñanza en toda su extensión, niveles, grados, modalidades y especialidades.",
        "tags": "competencias,educacion,enseñanza"
    },
    {
        "article": "Art. 76",
        "front": "Art. 76 EAA - ¿Qué competencias tiene en sanidad?",
        "back": "Organización, administración y gestión de centros y servicios sanitarios. Planificación sanitaria. Salud pública y coordinación hospitalaria.",
        "tags": "competencias,sanidad,salud-publica"
    },
]

def create_flashcards(deck_id):
    created = 0
    failed = 0

    for card_data in flashcards:
        flashcard = {
            "deck_id": deck_id,
            "front": card_data["front"],
            "back": card_data["back"],
            "article_number": card_data["article"],
            "law_name": "Estatuto de Autonomía de Aragón (LO 5/2007)",
            "tags": card_data["tags"]
        }

        try:
            response = requests.post(f"{API_URL}/flashcards/", json=flashcard)
            if response.status_code == 200:
                created += 1
                print(f"✅ {card_data['article']}: {card_data['front'][:50]}...")
            else:
                failed += 1
                print(f"❌ Error creando {card_data['article']}: {response.text}")
        except Exception as e:
            failed += 1
            print(f"❌ Error creando {card_data['article']}: {e}")

    return created, failed

if __name__ == "__main__":
    print("🚀 Creando flashcards Tema 2 - Estatuto de Autonomía de Aragón")
    print("=" * 60)

    # Crear deck
    deck_id = create_deck()

    print(f"\n📚 Creando {len(flashcards)} flashcards...")
    print("=" * 60)

    # Crear flashcards
    created, failed = create_flashcards(deck_id)

    print("\n" + "=" * 60)
    print(f"✅ Flashcards creadas: {created}")
    print(f"❌ Flashcards fallidas: {failed}")
    print(f"📊 Total: {len(flashcards)}")
    print("=" * 60)

    if created > 0:
        print(f"\n🎉 ¡Listo! Puedes empezar a estudiar en:")
        print(f"   - Web: http://localhost:2998/study")
        print(f"   - Cloudflare: https://cards.alejandrogracia.com/study")
        print(f"   - API: http://localhost:7999/api/study/next")
