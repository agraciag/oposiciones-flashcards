"""
Script para crear flashcards del Tema 3 - Organización del Estado
Corona, Cortes Generales, Gobierno y Poder Judicial
"""

import requests
import json

API_URL = "http://localhost:7999/api"

def create_deck():
    deck_data = {
        "name": "Tema 3 - Organización del Estado",
        "description": "Corona, Cortes Generales, Gobierno y Poder Judicial según la Constitución Española."
    }

    response = requests.post(f"{API_URL}/decks/", json=deck_data)
    if response.status_code == 200:
        deck = response.json()
        print(f"✅ Deck creado: {deck['name']} (ID: {deck['id']})")
        return deck['id']
    else:
        print("⚠️ Deck ya existe, buscando ID...")
        response = requests.get(f"{API_URL}/decks/")
        decks = response.json()
        for deck in decks:
            if "Tema 3" in deck['name']:
                print(f"✅ Usando deck existente: {deck['name']} (ID: {deck['id']})")
                return deck['id']
        return 4

flashcards = [
    # LA CORONA
    {
        "article": "Art. 56",
        "front": "Art. 56 CE - ¿Qué funciones tiene el Rey?",
        "back": "El Rey es el Jefe del Estado y asume la más alta representación del Estado español en las relaciones internacionales. Sus funciones son: sancionar y promulgar leyes, convocar y disolver Cortes, convocar referéndum, proponer candidato a Presidente del Gobierno, nombrar y separar a sus miembros, expedir decretos, etc.",
        "tags": "corona,rey,jefe-estado,funciones"
    },
    {
        "article": "Art. 57",
        "front": "Art. 57 CE - ¿Cómo se hereda la Corona?",
        "back": "La Corona de España es hereditaria en los sucesores de S.M. Don Juan Carlos I de Borbón. La sucesión sigue el orden regular de primogenitura y representación, siendo preferida la línea anterior a las posteriores; en la misma línea, el grado más próximo al más remoto; en el mismo grado, el varón a la mujer (modificado en 2006 para primogenitura absoluta en nuevos nacimientos).",
        "tags": "corona,sucesion,primogenitura"
    },
    {
        "article": "Art. 61",
        "front": "Art. 61 CE - ¿Qué juramento presta el Rey?",
        "back": "El Rey, al ser proclamado ante las Cortes Generales, prestará juramento de desempeñar fielmente sus funciones, guardar y hacer guardar la Constitución y las leyes y respetar los derechos de los ciudadanos y de las Comunidades Autónomas.",
        "tags": "corona,juramento,proclamacion"
    },
    {
        "article": "Art. 62",
        "front": "Art. 62 CE - ¿Qué actos corresponden al Rey?",
        "back": "Sancionar y promulgar las leyes, convocar y disolver las Cortes, convocar elecciones y referéndum, proponer candidato a Presidente del Gobierno, nombrar y separar a los miembros del Gobierno, expedir decretos, nombrar cargos civiles y militares, Alto Patronazgo de las Reales Academias, etc.",
        "tags": "corona,funciones,actos-regios"
    },
    {
        "article": "Art. 64",
        "front": "Art. 64 CE - ¿Quién refrenda los actos del Rey?",
        "back": "Los actos del Rey serán refrendados por el Presidente del Gobierno y, en su caso, por los Ministros competentes. La propuesta y el nombramiento del Presidente del Gobierno, y la disolución prevista en el artículo 99, serán refrendados por el Presidente del Congreso.",
        "tags": "corona,refrendo,responsabilidad"
    },

    # LAS CORTES GENERALES
    {
        "article": "Art. 66",
        "front": "Art. 66 CE - ¿Qué son las Cortes Generales?",
        "back": "Las Cortes Generales representan al pueblo español y están formadas por el Congreso de los Diputados y el Senado. Ejercen la potestad legislativa del Estado, aprueban sus Presupuestos, controlan la acción del Gobierno y las demás competencias que les atribuya la Constitución.",
        "tags": "cortes-generales,congreso,senado,legislativo"
    },
    {
        "article": "Art. 68",
        "front": "Art. 68 CE - ¿Cómo se compone el Congreso?",
        "back": "El Congreso se compone de un mínimo de 300 y un máximo de 400 Diputados, elegidos por sufragio universal, libre, igual, directo y secreto. La circunscripción electoral es la provincia. La ley distribuye el número total de Diputados, asignando una representación mínima inicial a cada circunscripción.",
        "tags": "congreso,diputados,elecciones,provincia"
    },
    {
        "article": "Art. 69",
        "front": "Art. 69 CE - ¿Cómo se compone el Senado?",
        "back": "El Senado es la Cámara de representación territorial. En cada provincia se eligen cuatro Senadores por sufragio universal. Las Comunidades Autónomas designan además un Senador y otro más por cada millón de habitantes.",
        "tags": "senado,senadores,territorial,ccaa"
    },
    {
        "article": "Art. 78",
        "front": "Art. 78 CE - ¿Qué son las Comisiones de Investigación?",
        "back": "El Congreso y el Senado, y, en su caso, ambas Cámaras conjuntamente, podrán nombrar Comisiones de investigación sobre cualquier asunto de interés público. Sus conclusiones no serán vinculantes para los Tribunales.",
        "tags": "cortes,comisiones,investigacion"
    },

    # EL GOBIERNO
    {
        "article": "Art. 97",
        "front": "Art. 97 CE - ¿Qué funciones tiene el Gobierno?",
        "back": "El Gobierno dirige la política interior y exterior, la Administración civil y militar y la defensa del Estado. Ejerce la función ejecutiva y la potestad reglamentaria de acuerdo con la Constitución y las leyes.",
        "tags": "gobierno,ejecutivo,funciones,administracion"
    },
    {
        "article": "Art. 98",
        "front": "Art. 98 CE - ¿Cómo se compone el Gobierno?",
        "back": "El Gobierno se compone del Presidente, de los Vicepresidentes en su caso, de los Ministros y de los demás miembros que establezca la ley.",
        "tags": "gobierno,composicion,presidente,ministros"
    },
    {
        "article": "Art. 99",
        "front": "Art. 99 CE - ¿Cómo se elige al Presidente del Gobierno?",
        "back": "El Rey, previa consulta con los representantes designados por los grupos políticos con representación parlamentaria, y a través del Presidente del Congreso, propondrá un candidato a la Presidencia del Gobierno. Si obtiene confianza de la mayoría absoluta, el Rey le nombrará Presidente. De no alcanzarla, se someterá a nueva votación 48 horas después, y la confianza se entenderá otorgada si obtiene mayoría simple.",
        "tags": "gobierno,presidente,investidura,congreso"
    },
    {
        "article": "Art. 101",
        "front": "Art. 101 CE - ¿Cuándo cesa el Gobierno?",
        "back": "El Gobierno cesa tras la celebración de elecciones generales, en los casos de pérdida de la confianza parlamentaria (moción de censura o cuestión de confianza), por dimisión o fallecimiento de su Presidente.",
        "tags": "gobierno,cese,confianza,dimision"
    },
    {
        "article": "Art. 108",
        "front": "Art. 108 CE - ¿Qué es la responsabilidad criminal del Gobierno?",
        "back": "El Gobierno responde solidariamente en su gestión política ante el Congreso de los Diputados.",
        "tags": "gobierno,responsabilidad,congreso"
    },

    # PODER JUDICIAL
    {
        "article": "Art. 117",
        "front": "Art. 117 CE - ¿Qué es el Poder Judicial?",
        "back": "La justicia emana del pueblo y se administra en nombre del Rey por Jueces y Magistrados integrantes del poder judicial, independientes, inamovibles, responsables y sometidos únicamente al imperio de la ley.",
        "tags": "poder-judicial,justicia,independencia,jueces"
    },
    {
        "article": "Art. 122",
        "front": "Art. 122 CE - ¿Qué es el CGPJ?",
        "back": "El Consejo General del Poder Judicial es el órgano de gobierno del mismo. Está integrado por el Presidente del Tribunal Supremo, que lo preside, y por veinte miembros nombrados por el Rey por un período de cinco años.",
        "tags": "cgpj,poder-judicial,gobierno-judicial"
    },
    {
        "article": "Art. 123",
        "front": "Art. 123 CE - ¿Qué es el Tribunal Supremo?",
        "back": "El Tribunal Supremo, con jurisdicción en toda España, es el órgano jurisdiccional superior en todos los órdenes, salvo lo dispuesto en materia de garantías constitucionales.",
        "tags": "tribunal-supremo,jurisdiccion,organo-superior"
    },
    {
        "article": "Art. 124",
        "front": "Art. 124 CE - ¿Qué es el Ministerio Fiscal?",
        "back": "El Ministerio Fiscal, sin perjuicio de las funciones encomendadas a otros órganos, tiene por misión promover la acción de la justicia en defensa de la legalidad, de los derechos de los ciudadanos y del interés público tutelado por la ley, de oficio o a petición de los interesados, así como velar por la independencia de los Tribunales.",
        "tags": "ministerio-fiscal,fiscalia,legalidad"
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
            "law_name": "Constitución Española",
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
    print("🚀 Creando flashcards Tema 3 - Organización del Estado")
    print("=" * 60)

    deck_id = create_deck()

    print(f"\n📚 Creando {len(flashcards)} flashcards...")
    print("=" * 60)

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
