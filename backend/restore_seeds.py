"""
Script para restaurar todos los mazos de seed con autenticación
"""

import requests

API_URL = "http://localhost:7999/api"

# Credenciales
USERNAME = "alejandro"
PASSWORD = "oposit2026"

def get_token():
    """Obtener token de autenticación"""
    response = requests.post(
        f"{API_URL}/auth/token",
        data={"username": USERNAME, "password": PASSWORD}
    )

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"❌ Error obteniendo token: {response.json()}")
        return None

def create_deck_with_cards(token, deck_data, flashcards):
    """Crear un mazo con sus tarjetas"""
    headers = {"Authorization": f"Bearer {token}"}

    # Crear mazo
    response = requests.post(f"{API_URL}/decks/", json=deck_data, headers=headers)

    if response.status_code == 200:
        deck = response.json()
        deck_id = deck['id']
        print(f"✅ Mazo creado: {deck['name']} (ID: {deck_id})")

        # Crear tarjetas
        created = 0
        failed = 0

        for card in flashcards:
            card_data = {
                "deck_id": deck_id,
                "front": card["front"],
                "back": card["back"],
                "article_number": card.get("article"),
                "tags": card.get("tags", "")
            }

            response = requests.post(f"{API_URL}/flashcards/", json=card_data, headers=headers)

            if response.status_code == 200:
                created += 1
            else:
                failed += 1
                print(f"  ⚠️  Error en tarjeta: {card.get('article', 'N/A')}")

        print(f"  📊 Tarjetas creadas: {created}/{len(flashcards)}")
        return True
    else:
        print(f"❌ Error creando mazo: {response.json()}")
        return False

def main():
    print("🚀 Restaurando mazos de OpositApp\n")

    # Obtener token
    token = get_token()
    if not token:
        print("❌ No se pudo autenticar")
        return

    print(f"✅ Autenticado como {USERNAME}\n")
    print("="*60)

    # Tema 1 - Constitución
    print("\n📚 TEMA 1 - Constitución Española (Art. 14-29)")
    tema1_flashcards = [
        {"article": "Art. 14", "front": "Art. 14 CE - ¿Qué principio fundamental establece?", "back": "Igualdad ante la ley sin discriminación por nacimiento, raza, sexo, religión, opinión o cualquier otra condición o circunstancia personal o social.", "tags": "igualdad,no-discriminacion"},
        {"article": "Art. 15", "front": "Art. 15 CE - ¿Qué derechos reconoce?", "back": "Derecho a la vida y a la integridad física y moral. Nadie puede ser sometido a tortura ni a penas o tratos inhumanos o degradantes. Queda abolida la pena de muerte.", "tags": "vida,integridad,tortura"},
        {"article": "Art. 16", "front": "Art. 16 CE - ¿Qué libertades garantiza?", "back": "Libertad ideológica, religiosa y de culto. Nadie puede ser obligado a declarar sobre su ideología, religión o creencias.", "tags": "libertad-religiosa,ideologia"},
        {"article": "Art. 17", "front": "Art. 17 CE - ¿Qué derecho regula?", "back": "Derecho a la libertad y seguridad. Detención preventiva máximo 72 horas. Procedimiento de habeas corpus.", "tags": "libertad,detencion,habeas-corpus"},
        {"article": "Art. 18", "front": "Art. 18 CE - ¿Qué derechos fundamentales protege?", "back": "Derecho al honor, intimidad personal y familiar, y propia imagen. Inviolabilidad del domicilio. Secreto de las comunicaciones.", "tags": "intimidad,honor,domicilio"},
        {"article": "Art. 19", "front": "Art. 19 CE - ¿Qué libertad reconoce?", "back": "Libertad de residencia y circulación por el territorio nacional. Derecho a entrar y salir libremente de España.", "tags": "circulacion,residencia"},
        {"article": "Art. 20", "front": "Art. 20 CE - ¿Qué derechos de expresión reconoce?", "back": "Libertad de expresión, producción y creación literaria/artística/científica. Libertad de cátedra. Derecho a comunicar/recibir información veraz. No censura previa.", "tags": "expresion,prensa,informacion"},
    ]

    create_deck_with_cards(
        token,
        {
            "name": "Tema 1 - Constitución Española (Art. 14-29)",
            "description": "Derechos Fundamentales y Libertades Públicas. Sección 1ª del Capítulo II del Título I."
        },
        tema1_flashcards
    )

    print("\n="*60)
    print("\n✅ Proceso completado")
    print(f"\n💡 Ahora puedes acceder a http://localhost:2998/decks")

if __name__ == "__main__":
    main()
