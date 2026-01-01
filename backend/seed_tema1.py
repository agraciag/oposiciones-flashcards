"""
Script para crear flashcards del Tema 1 - Constitución Española
Artículos 14-29: Derechos Fundamentales y Libertades Públicas
"""

import requests
import json

API_URL = "http://localhost:8000/api"

# Primero, crear el deck si no existe
def create_deck():
    deck_data = {
        "name": "Tema 1 - Constitución Española (Art. 14-29)",
        "description": "Derechos Fundamentales y Libertades Públicas. Sección 1ª del Capítulo II del Título I."
    }

    response = requests.post(f"{API_URL}/decks/", json=deck_data)
    if response.status_code == 200:
        deck = response.json()
        print(f"✅ Deck creado: {deck['name']} (ID: {deck['id']})")
        return deck['id']
    else:
        # Si ya existe, asumimos ID 1
        print("⚠️ Deck ya existe, usando ID 1")
        return 1

# Flashcards de derechos fundamentales (Art. 14-29)
flashcards = [
    {
        "article": "Art. 14",
        "front": "Art. 14 CE - ¿Qué principio fundamental establece?",
        "back": "Igualdad ante la ley sin discriminación por nacimiento, raza, sexo, religión, opinión o cualquier otra condición o circunstancia personal o social.",
        "tags": "igualdad,no-discriminacion,derechos-fundamentales"
    },
    {
        "article": "Art. 15",
        "front": "Art. 15 CE - ¿Qué derechos reconoce?",
        "back": "Derecho a la vida y a la integridad física y moral. Nadie puede ser sometido a tortura ni a penas o tratos inhumanos o degradantes. Queda abolida la pena de muerte (salvo leyes penales militares en tiempos de guerra).",
        "tags": "vida,integridad,tortura,pena-muerte"
    },
    {
        "article": "Art. 16",
        "front": "Art. 16 CE - ¿Qué libertades garantiza?",
        "back": "Libertad ideológica, religiosa y de culto. Nadie puede ser obligado a declarar sobre su ideología, religión o creencias.",
        "tags": "libertad-religiosa,ideologia,creencias,culto"
    },
    {
        "article": "Art. 17",
        "front": "Art. 17 CE - ¿Qué derecho regula?",
        "back": "Derecho a la libertad y seguridad. Detención preventiva máximo 72 horas. Procedimiento de habeas corpus.",
        "tags": "libertad,detencion,habeas-corpus,seguridad"
    },
    {
        "article": "Art. 18",
        "front": "Art. 18 CE - ¿Qué derechos fundamentales protege?",
        "back": "Derecho al honor, intimidad personal y familiar, y propia imagen. Inviolabilidad del domicilio. Secreto de las comunicaciones.",
        "tags": "intimidad,honor,domicilio,comunicaciones,privacidad"
    },
    {
        "article": "Art. 19",
        "front": "Art. 19 CE - ¿Qué libertad reconoce?",
        "back": "Libertad de residencia y circulación por el territorio nacional. Derecho a entrar y salir libremente de España.",
        "tags": "circulacion,residencia,movilidad"
    },
    {
        "article": "Art. 20",
        "front": "Art. 20 CE - ¿Qué derechos de expresión reconoce?",
        "back": "Libertad de expresión, producción y creación literaria/artística/científica. Libertad de cátedra. Derecho a comunicar/recibir información veraz. No censura previa.",
        "tags": "expresion,prensa,informacion,censura,catedra"
    },
    {
        "article": "Art. 21",
        "front": "Art. 21 CE - ¿Qué derecho de reunión establece?",
        "back": "Derecho de reunión pacífica y sin armas. No necesita autorización previa. Comunicación previa para reuniones en lugares de tránsito público y manifestaciones.",
        "tags": "reunion,manifestacion,pacifica"
    },
    {
        "article": "Art. 22",
        "front": "Art. 22 CE - ¿Qué derecho de asociación reconoce?",
        "back": "Derecho de asociación. Prohibidas asociaciones secretas y de carácter paramilitar. Disolución judicial.",
        "tags": "asociacion,organizacion,disolución"
    },
    {
        "article": "Art. 23",
        "front": "Art. 23 CE - ¿Qué derechos de participación política reconoce?",
        "back": "Derecho a participar en asuntos públicos directamente o por representantes. Derecho de sufragio activo y pasivo. Acceso en condiciones de igualdad a funciones y cargos públicos.",
        "tags": "participacion,sufragio,voto,funcion-publica"
    },
    {
        "article": "Art. 24",
        "front": "Art. 24 CE - ¿Qué garantías judiciales establece?",
        "back": "Tutela judicial efectiva. Derecho a juez ordinario predeterminado por ley. Defensa y asistencia letrada. Presunción de inocencia. No declarar contra sí mismo ni confesarse culpable.",
        "tags": "tutela-judicial,defensa,presuncion-inocencia,juez"
    },
    {
        "article": "Art. 25",
        "front": "Art. 25 CE - ¿Qué principios penales establece?",
        "back": "Principio de legalidad penal (nadie puede ser condenado sino por ley anterior). Penas orientadas a reeducación y reinserción social. Prohibición de trabajos forzados.",
        "tags": "legalidad-penal,penas,reeducacion,reinserccion"
    },
    {
        "article": "Art. 26",
        "front": "Art. 26 CE - ¿Qué dice sobre los Tribunales de Honor?",
        "back": "Se prohíben los Tribunales de Honor en el ámbito de la Administración civil y de las organizaciones profesionales.",
        "tags": "tribunales-honor,prohibicion"
    },
    {
        "article": "Art. 27",
        "front": "Art. 27 CE - ¿Qué derechos educativos reconoce?",
        "back": "Derecho a la educación. Libertad de enseñanza. Educación básica obligatoria y gratuita. Libertad de creación de centros docentes. Participación de padres, profesores y alumnos. Autonomía universitaria.",
        "tags": "educacion,enseñanza,universidad,centros-docentes"
    },
    {
        "article": "Art. 28",
        "front": "Art. 28 CE - ¿Qué derechos laborales reconoce?",
        "back": "Libertad de sindicación. Derecho de huelga de los trabajadores. Límites a las Fuerzas Armadas, Institutos armados y otros cuerpos sometidos a disciplina militar.",
        "tags": "sindicato,huelga,trabajadores,laboral"
    },
    {
        "article": "Art. 29",
        "front": "Art. 29 CE - ¿Qué derecho de petición establece?",
        "back": "Derecho de petición individual y colectiva por escrito. Prohibición del derecho de petición por las Fuerzas Armadas e Institutos armados de forma colectiva.",
        "tags": "peticion,escrito"
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
    print("🚀 Creando flashcards Tema 1 - Constitución Española")
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
        print(f"   - Web: http://localhost:3000/study")
        print(f"   - API: http://localhost:8000/api/study/next")
