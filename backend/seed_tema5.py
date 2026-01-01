"""
Script para crear flashcards del Tema 5 - Procedimiento Administrativo Común
Ley 39/2015 del Procedimiento Administrativo Común de las Administraciones Públicas
"""

import requests
import json

API_URL = "http://localhost:7999/api"

def create_deck():
    deck_data = {
        "name": "Tema 5 - Procedimiento Administrativo Común",
        "description": "Ley 39/2015 PACAP: actos administrativos, procedimiento, recursos y reclamaciones."
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
            if "Tema 5" in deck['name']:
                print(f"✅ Usando deck existente: {deck['name']} (ID: {deck['id']})")
                return deck['id']
        return 6

flashcards = [
    # DISPOSICIONES GENERALES
    {
        "article": "Art. 1",
        "front": "Art. 1 LPACAP - ¿Cuál es el objeto de esta ley?",
        "back": "Regular los requisitos de validez y eficacia de los actos administrativos, el procedimiento administrativo común, la iniciativa legislativa y la potestad reglamentaria, la responsabilidad patrimonial de las administraciones y el régimen sancionador.",
        "tags": "objeto,procedimiento,validez"
    },
    {
        "article": "Art. 3",
        "front": "Art. 3 LPACAP - ¿Qué principios rigen el procedimiento?",
        "back": "Servicio efectivo a los ciudadanos, transparencia, participación en la gestión pública, racionalización y agilización de procedimientos, buena fe, confianza legítima, y aquellos principios señalados en la LRJSP.",
        "tags": "principios,transparencia,participacion"
    },

    # ACTOS ADMINISTRATIVOS
    {
        "article": "Art. 39",
        "front": "Art. 39 LPACAP - ¿Qué requisitos de forma tienen los actos?",
        "back": "Los actos administrativos se producirán por escrito (salvo que su naturaleza exija otra forma). Deberán expresar: el órgano que dicta el acto, lugar y fecha, hechos, fundamentos de derecho, expresión clara de la resolución, recursos y órgano ante el que interponerlos, y firma del titular.",
        "tags": "actos,forma,requisitos,motivacion"
    },
    {
        "article": "Art. 47",
        "front": "Art. 47 LPACAP - ¿Cuándo son nulos los actos administrativos?",
        "back": "Son nulos los actos que: lesionen derechos fundamentales, dictados por órgano manifiestamente incompetente, de contenido imposible, constitutivos de infracción penal, dictados prescindiendo del procedimiento, contrarios al ordenamiento que supongan supresión o limitación de derechos, y aquellos en los que así lo establezca una ley.",
        "tags": "nulidad,actos,invalidez"
    },
    {
        "article": "Art. 48",
        "front": "Art. 48 LPACAP - ¿Cuándo son anulables los actos?",
        "back": "Son anulables los actos que incurran en cualquier infracción del ordenamiento jurídico, incluso la desviación de poder. La anulabilidad se sanea transcurrido el plazo para recurrir sin haberlo hecho.",
        "tags": "anulabilidad,actos,vicios"
    },
    {
        "article": "Art. 56",
        "front": "Art. 56 LPACAP - ¿Qué es la eficacia de los actos?",
        "back": "Los actos administrativos producen efectos desde la fecha en que se dicten, salvo que en ellos se disponga otra cosa. La eficacia quedará demorada cuando así lo exija el contenido del acto o esté supeditada a su notificación, publicación o aprobación superior.",
        "tags": "eficacia,actos,efectos,notificacion"
    },

    # PROCEDIMIENTO ADMINISTRATIVO
    {
        "article": "Art. 21",
        "front": "Art. 21 LPACAP - ¿Cómo se inicia el procedimiento?",
        "back": "El procedimiento puede iniciarse de oficio (por acuerdo del órgano competente, por petición razonada de otros órganos, por denuncia o por propia iniciativa) o a solicitud del interesado.",
        "tags": "inicio,procedimiento,oficio,solicitud"
    },
    {
        "article": "Art. 53",
        "front": "Art. 53 LPACAP - ¿Qué es el interesado?",
        "back": "Se consideran interesados: quienes lo promuevan como titulares de derechos o intereses, los que sin haber iniciado el procedimiento tengan derechos que puedan resultar afectados, y aquellos cuyos intereses legítimos puedan resultar afectados por la resolución.",
        "tags": "interesados,legitimacion,derechos"
    },
    {
        "article": "Art. 75",
        "front": "Art. 75 LPACAP - ¿Qué es la instrucción del procedimiento?",
        "back": "Comprende la realización de alegaciones, la aportación de documentos u otros elementos de juicio, la práctica de pruebas, informes, trámite de audiencia y, en su caso, informes públicos.",
        "tags": "instruccion,alegaciones,prueba"
    },
    {
        "article": "Art. 82",
        "front": "Art. 82 LPACAP - ¿Qué es el trámite de audiencia?",
        "back": "El trámite de audiencia permite a los interesados consultar el expediente, obtener copia de documentos y formular alegaciones antes de la propuesta de resolución. Se puede prescindir cuando no figuren hechos ni alegaciones distintos a los de la solicitud.",
        "tags": "audiencia,alegaciones,expediente"
    },
    {
        "article": "Art. 86",
        "front": "Art. 86 LPACAP - ¿Cómo se adopta la resolución?",
        "back": "Pondrá fin al procedimiento y resolverá todas las cuestiones planteadas por los interesados y aquellas derivadas del mismo. Cuando existan informes preceptivos favorables ya incorporados al procedimiento se podrá formular y notificar la resolución sin necesidad de propuesta de resolución.",
        "tags": "resolucion,procedimiento,terminacion"
    },
    {
        "article": "Art. 21.1",
        "front": "Art. 21 LPACAP - ¿Qué plazos tiene el procedimiento?",
        "back": "El plazo máximo en el que debe notificarse la resolución expresa no podrá exceder de seis meses salvo que una norma con rango de Ley establezca uno mayor. Los plazos se expresan en días hábiles (salvo en plazos de comparecencia, audiencia o cumplimiento, que son calendario).",
        "tags": "plazos,resolucion,silencio"
    },

    # SILENCIO ADMINISTRATIVO
    {
        "article": "Art. 24",
        "front": "Art. 24 LPACAP - ¿Qué es el silencio administrativo?",
        "back": "En procedimientos iniciados a solicitud del interesado, si no se notifica resolución expresa en plazo, puede entenderse estimada la solicitud por silencio administrativo positivo, salvo que una norma o el derecho de la UE establezcan lo contrario (silencio negativo).",
        "tags": "silencio-administrativo,plazos,estimacion"
    },
    {
        "article": "Art. 25",
        "front": "Art. 25 LPACAP - ¿Cuándo se produce silencio negativo?",
        "back": "Cuando se trate de procedimientos cuya estimación tuviera como consecuencia la transferencia al solicitante o a terceros de facultades relativas al dominio público o servicio público, el silencio tiene sentido desestimatorio.",
        "tags": "silencio-negativo,dominio-publico"
    },

    # RECURSOS ADMINISTRATIVOS
    {
        "article": "Art. 112",
        "front": "Art. 112 LPACAP - ¿Qué recursos existen?",
        "back": "Contra los actos administrativos cabe: recurso de alzada ante el superior jerárquico, recurso potestativo de reposición ante el mismo órgano, y en vía judicial, recurso contencioso-administrativo.",
        "tags": "recursos,alzada,reposicion"
    },
    {
        "article": "Art. 121",
        "front": "Art. 121 LPACAP - ¿Qué plazo tiene el recurso de alzada?",
        "back": "Un mes si el acto fuera expreso. Si el acto no fuera expreso, tres meses a contar desde el día siguiente a aquel en que se produzca el silencio administrativo.",
        "tags": "alzada,plazos,recursos"
    },
    {
        "article": "Art. 123",
        "front": "Art. 123 LPACAP - ¿Qué plazo tiene el recurso de reposición?",
        "back": "Un mes si el acto fuera expreso. Si el acto no fuera expreso, tres meses a contar desde el día siguiente a aquel en que se produzca el silencio administrativo.",
        "tags": "reposicion,plazos,recursos"
    },
    {
        "article": "Art. 124",
        "front": "Art. 124 LPACAP - ¿Qué efectos tiene el silencio en los recursos?",
        "back": "Transcurrido un mes desde la interposición del recurso de alzada o potestativo de reposición sin que se notifique resolución, se entenderá desestimado y quedará expedita la vía judicial.",
        "tags": "silencio,recursos,desestimacion"
    },

    # REVISIÓN DE OFICIO
    {
        "article": "Art. 106",
        "front": "Art. 106 LPACAP - ¿Qué es la revisión de oficio?",
        "back": "Las Administraciones pueden declarar de oficio la nulidad de sus actos administrativos que hayan puesto fin a la vía administrativa o hayan sido recurridos, previa audiencia del interesado. Requiere dictamen favorable del Consejo de Estado u órgano consultivo de la Comunidad Autónoma.",
        "tags": "revision-oficio,nulidad,consejo-estado"
    },
    {
        "article": "Art. 109",
        "front": "Art. 109 LPACAP - ¿Qué es la revocación de actos?",
        "back": "Las Administraciones pueden revocar en cualquier momento sus actos de gravamen o desfavorables, siempre que tal revocación no constituya dispensa o exención no permitida por las leyes o sea contraria al principio de igualdad.",
        "tags": "revocacion,actos,gravamen"
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
            "law_name": "Ley 39/2015 PACAP",
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
    print("🚀 Creando flashcards Tema 5 - Procedimiento Administrativo Común")
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
