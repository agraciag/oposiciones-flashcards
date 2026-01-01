"""
Script para crear flashcards del Tema 4 - Administración Pública
Ley 40/2015 de Régimen Jurídico del Sector Público
"""

import requests
import json

API_URL = "http://localhost:7999/api"

def create_deck():
    deck_data = {
        "name": "Tema 4 - Administración Pública",
        "description": "Ley 40/2015 de Régimen Jurídico del Sector Público: organización, funcionamiento y relaciones entre administraciones."
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
            if "Tema 4" in deck['name']:
                print(f"✅ Usando deck existente: {deck['name']} (ID: {deck['id']})")
                return deck['id']
        return 5

flashcards = [
    # DISPOSICIONES GENERALES
    {
        "article": "Art. 1",
        "front": "Art. 1 LRJSP - ¿Cuál es el objeto de esta ley?",
        "back": "Regular: a) Los requisitos de validez y eficacia de los actos administrativos. b) El funcionamiento electrónico del sector público. c) Los principios de la potestad sancionadora. d) El régimen jurídico del sector público.",
        "tags": "objeto,validez,sector-publico"
    },
    {
        "article": "Art. 2",
        "front": "Art. 2 LRJSP - ¿Qué entidades integran el sector público?",
        "back": "El sector público institucional está integrado por: Organismos autónomos, Entidades públicas empresariales, Sociedades mercantiles estatales, Fundaciones del sector público, Fondos sin personalidad jurídica, y Consorcios.",
        "tags": "sector-publico,organismos,entidades"
    },
    {
        "article": "Art. 3",
        "front": "Art. 3 LRJSP - ¿Qué principios rigen la actuación administrativa?",
        "back": "Servicio efectivo a los ciudadanos, simplicidad, claridad y proximidad, participación, objetividad y transparencia, eficacia en el cumplimiento de objetivos, economía, suficiencia y adecuación de medios, eficiencia en la asignación y utilización de recursos públicos, y responsabilidad.",
        "tags": "principios,actuacion,transparencia,eficacia"
    },

    # ÓRGANOS ADMINISTRATIVOS
    {
        "article": "Art. 5",
        "front": "Art. 5 LRJSP - ¿Qué requisitos tienen los órganos administrativos?",
        "back": "Los órganos administrativos deben ser creados, regidos y coordinados de acuerdo con la Constitución y las leyes. Carecen de personalidad jurídica propia.",
        "tags": "organos,competencia,jerarquia"
    },
    {
        "article": "Art. 9",
        "front": "Art. 9 LRJSP - ¿Qué es la competencia?",
        "back": "La competencia es irrenunciable y se ejercerá por los órganos que la tengan atribuida como propia, salvo los casos de delegación, avocación, encomienda de gestión, delegación de firma y suplencia.",
        "tags": "competencia,irrenunciable,delegacion"
    },
    {
        "article": "Art. 10",
        "front": "Art. 10 LRJSP - ¿Qué es la delegación de competencias?",
        "back": "Los órganos de las Administraciones pueden delegar el ejercicio de competencias en otros órganos de la misma Administración, aunque sean jerárquicamente dependientes. La delegación debe publicarse.",
        "tags": "delegacion,competencias,publicacion"
    },
    {
        "article": "Art. 11",
        "front": "Art. 11 LRJSP - ¿Qué es la avocación?",
        "back": "Los órganos superiores podrán avocar para sí el conocimiento de un asunto cuya resolución corresponda ordinariamente o por delegación a sus órganos administrativos dependientes, cuando circunstancias de índole técnica, económica, social, jurídica o territorial lo hagan conveniente.",
        "tags": "avocacion,jerarquia,superior"
    },
    {
        "article": "Art. 15",
        "front": "Art. 15 LRJSP - ¿Qué es la encomienda de gestión?",
        "back": "La realización de actividades de carácter material, técnico o de servicios de la competencia de un órgano puede encomendarse a otros órganos o entidades del mismo o de distinto sector público. No supone cesión de titularidad de la competencia.",
        "tags": "encomienda-gestion,actividades,competencia"
    },

    # RELACIONES ENTRE ADMINISTRACIONES
    {
        "article": "Art. 140",
        "front": "Art. 140 LRJSP - ¿Qué principios rigen las relaciones entre administraciones?",
        "back": "Las relaciones entre la Administración General del Estado y las Comunidades Autónomas se rigen por los principios de: lealtad institucional, cooperación, colaboración, coordinación, respeto a los ámbitos competenciales respectivos, ponderación de los intereses públicos.",
        "tags": "relaciones,principios,cooperacion,lealtad"
    },
    {
        "article": "Art. 141",
        "front": "Art. 141 LRJSP - ¿Qué es el deber de colaboración?",
        "back": "La Administración General del Estado, las de las Comunidades Autónomas y las Entidades que integran la Administración Local deben colaborar y auxiliarse para aquellas actividades que contribuyan a la consecución de fines comunes.",
        "tags": "colaboracion,administraciones,coordinacion"
    },

    # RESPONSABILIDAD PATRIMONIAL
    {
        "article": "Art. 32",
        "front": "Art. 32 LRJSP - ¿Cuándo responden las administraciones?",
        "back": "Los particulares tendrán derecho a ser indemnizados por las Administraciones Públicas de toda lesión que sufran en sus bienes y derechos, salvo en casos de fuerza mayor, siempre que la lesión sea consecuencia del funcionamiento normal o anormal de los servicios públicos.",
        "tags": "responsabilidad-patrimonial,indemnizacion,lesion"
    },
    {
        "article": "Art. 34",
        "front": "Art. 34 LRJSP - ¿Cuáles son los requisitos de la responsabilidad patrimonial?",
        "back": "Que el particular sufra una lesión en sus bienes o derechos, que la lesión sea antijurídica, que sea efectiva, evaluable económicamente e individualizada, y que exista relación de causalidad entre el funcionamiento del servicio público y el daño.",
        "tags": "responsabilidad,requisitos,lesion,causalidad"
    },

    # POTESTAD SANCIONADORA
    {
        "article": "Art. 25",
        "front": "Art. 25 LRJSP - ¿Qué principios rigen la potestad sancionadora?",
        "back": "Legalidad, irretroactividad, tipicidad, responsabilidad, proporcionalidad, prescripción y non bis in idem (no sancionar dos veces por el mismo hecho).",
        "tags": "sancionador,principios,legalidad,proporcionalidad"
    },
    {
        "article": "Art. 28",
        "front": "Art. 28 LRJSP - ¿Qué es el principio de proporcionalidad en las sanciones?",
        "back": "Las sanciones deben ser proporcionadas a la gravedad de los hechos constitutivos de la infracción, debiendo observarse la debida adecuación entre la gravedad del hecho y la sanción aplicada.",
        "tags": "proporcionalidad,sanciones,gravedad"
    },
    {
        "article": "Art. 29",
        "front": "Art. 29 LRJSP - ¿Cuándo prescriben las infracciones?",
        "back": "Las infracciones muy graves prescriben a los tres años, las graves a los dos años, y las leves a los seis meses. El plazo de prescripción comienza a contarse desde el día en que la infracción se hubiera cometido.",
        "tags": "prescripcion,infracciones,plazos"
    },

    # FUNCIONAMIENTO ELECTRÓNICO
    {
        "article": "Art. 41",
        "front": "Art. 41 LRJSP - ¿Qué es el derecho de acceso electrónico?",
        "back": "Todos tienen derecho a relacionarse con las Administraciones Públicas utilizando medios electrónicos. Las Administraciones Públicas deberán garantizar que los ciudadanos puedan relacionarse con ellas a través de medios electrónicos.",
        "tags": "administracion-electronica,acceso,derechos"
    },
    {
        "article": "Art. 43",
        "front": "Art. 43 LRJSP - ¿Qué son los sistemas de identificación electrónica?",
        "back": "Los sistemas de identificación electrónica permitidos son: DNI electrónico o certificado electrónico en los términos de la ley de firma electrónica; sistemas basados en claves concertadas; y otros sistemas aceptados por las Administraciones.",
        "tags": "identificacion-electronica,dni,certificado-digital"
    },

    # CONFLICTOS DE ATRIBUCIONES
    {
        "article": "Art. 19",
        "front": "Art. 19 LRJSP - ¿Qué son los conflictos de atribuciones?",
        "back": "Los conflictos de atribuciones que se susciten entre órganos de una misma Administración serán resueltos por el superior jerárquico común.",
        "tags": "conflictos,atribuciones,jerarquia"
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
            "law_name": "Ley 40/2015 RJSP",
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
    print("🚀 Creando flashcards Tema 4 - Administración Pública")
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
