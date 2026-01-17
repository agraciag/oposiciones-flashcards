"""
Script para analizar y comparar temarios
Extrae los temas de cada PDF y calcula el % de coincidencia con Anexo V
"""

import fitz  # PyMuPDF
import re
from pathlib import Path
from difflib import SequenceMatcher

TEMARIOS_PATH = Path("/mnt/d/dev_projects/oposiciones-flashcards/Material de Estudio/temarios")

# Keywords distintivos del Anexo V para comparación de específicos
ANEXO_V_KEYWORDS_ESPECIFICOS = [
    "educación", "LOE", "centros docentes", "centros públicos", "sistema educativo",
    "urbanístico", "planeamiento", "suelo",
    "CTE", "Código Técnico", "edificación",
    "seguridad estructural", "cimentaciones", "estructuras",
    "incendio", "evacuación",
    "accesibilidad", "SUA",
    "salubridad", "humedad",
    "ruido", "acústic",
    "ahorro de energía", "HE", "eficiencia energética",
    "RITE", "instalaciones térmicas",
    "fontanería", "saneamiento", "electricidad", "climatización", "gas", "telecomunicaciones",
    "ascensores", "elevadores",
    "seguridad y salud", "prevención",
    "mediciones", "presupuestos",
    "programación de obras", "PERT", "GANTT",
    "control de calidad",
    "proyecto de obras", "dirección de obra",
    "mantenimiento", "ITE", "libro del edificio",
    "certificación energética",
    "patología", "rehabilitación",
    "patrimonio arquitectónico", "patrimonio cultural"
]

# Keywords para otros campos técnicos
KEYWORDS_INFORMATICA = [
    "informática", "software", "hardware", "programación", "base de datos",
    "redes", "internet", "seguridad informática", "sistemas operativos",
    "desarrollo", "aplicaciones", "web", "java", "python", "SQL",
    "telecomunicaciones", "protocolos", "servidores"
]

KEYWORDS_DELINEANTES = [
    "CAD", "BIM", "dibujo", "croquis", "escalas", "perspectiva",
    "cartografía", "SIG", "GIS", "topografía", "planos",
    "representación gráfica", "AutoCAD", "Revit"
]

KEYWORDS_PATRIMONIO = [
    "patrimonio", "conservación", "restauración", "bienes culturales",
    "museo", "archivo", "arqueología", "historia del arte",
    "protección", "catalogación", "inventario"
]


def extract_text_from_pdf(pdf_path):
    """Extrae texto completo de un PDF"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def extract_topics_from_text(text):
    """Extrae los temas de un texto de temario"""
    # Buscar "Programa de materias comunes" y "Programa de materias específicas"
    comunes_match = re.search(r'Programa de materias comunes[.\s]*\n([\s\S]*?)(?=Programa de materias específicas|$)', text, re.IGNORECASE)
    especificas_match = re.search(r'Programa de materias específicas[.\s]*\n([\s\S]*?)(?=Firmado electrónicamente|$)', text, re.IGNORECASE)

    comunes = []
    especificos = []

    def parse_topics(section_text):
        topics = []
        if not section_text:
            return topics

        # Patrón: número seguido de punto y espacio, luego el contenido
        # El contenido puede continuar en varias líneas hasta el siguiente número
        pattern = r'(\d+)\.\s+([^\d][\s\S]*?)(?=\n\d+\.\s|\Z)'
        matches = re.findall(pattern, section_text)

        for num, content in matches:
            # Limpiar el contenido
            content = re.sub(r'\s+', ' ', content).strip()
            # Eliminar firmas y pies de página
            content = re.sub(r'Firmado electrónicamente.*$', '', content, flags=re.IGNORECASE)
            content = re.sub(r'Documento verificado.*$', '', content, flags=re.IGNORECASE)
            if len(content) > 15:  # Solo temas con contenido sustancial
                topics.append((int(num), content))

        return topics

    if comunes_match:
        comunes = parse_topics(comunes_match.group(1))

    if especificas_match:
        especificos = parse_topics(especificas_match.group(1))

    return comunes, especificos


def calculate_keyword_overlap(topics, keywords):
    """Calcula cuántos temas contienen al menos una keyword"""
    matches = 0
    matched_topics = []
    for num, topic in topics:
        topic_lower = topic.lower()
        for kw in keywords:
            if kw.lower() in topic_lower:
                matches += 1
                matched_topics.append((num, topic, kw))
                break
    return matches, matched_topics


def calculate_topic_similarity(topic1, topic2):
    """Calcula similitud entre dos temas"""
    t1 = topic1.lower()
    t2 = topic2.lower()
    return SequenceMatcher(None, t1, t2).ratio()


def compare_common_topics(topics_a, topics_b):
    """Compara temas comunes entre dos temarios"""
    matches = 0
    for num_a, topic_a in topics_a:
        for num_b, topic_b in topics_b:
            similarity = calculate_topic_similarity(topic_a, topic_b)
            if similarity > 0.5:  # 50% de similitud
                matches += 1
                break
    return matches


# Temas comunes del Anexo V (resumidos para comparación)
ANEXO_V_COMUNES_KEYWORDS = [
    "constitución española",
    "corona", "cortes generales", "poder judicial",
    "organización territorial", "comunidades autónomas",
    "administración local", "provincias", "municipios",
    "estatuto de autonomía de aragón",
    "igualdad de género", "violencia de género", "discapacidad",
    "empleado público", "funcionarios",
    "procedimiento administrativo",
    "contratos del sector público", "patrimonio",
    "responsabilidad"
]


def analyze_temario(pdf_path):
    """Analiza un temario completo"""
    print(f"\n{'='*70}")
    print(f"📄 {pdf_path.name}")
    print('='*70)

    text = extract_text_from_pdf(pdf_path)
    comunes, especificos = extract_topics_from_text(text)

    print(f"\n📋 Temas encontrados:")
    print(f"   - Materias comunes: {len(comunes)}")
    print(f"   - Materias específicas: {len(especificos)}")

    # Mostrar algunos temas de ejemplo
    if comunes:
        print(f"\n   Ejemplo comunes:")
        for num, topic in comunes[:2]:
            print(f"      {num}. {topic[:80]}...")

    if especificos:
        print(f"\n   Ejemplo específicos:")
        for num, topic in especificos[:2]:
            print(f"      {num}. {topic[:80]}...")

    # Comparar comunes con Anexo V
    comunes_matches = 0
    for num, topic in comunes:
        topic_lower = topic.lower()
        for kw in ANEXO_V_COMUNES_KEYWORDS:
            if kw in topic_lower:
                comunes_matches += 1
                break

    # Comparar específicos con keywords del Anexo V
    especificos_matches, matched = calculate_keyword_overlap(especificos, ANEXO_V_KEYWORDS_ESPECIFICOS)

    return {
        'name': pdf_path.stem,
        'filename': pdf_path.name,
        'comunes': comunes,
        'especificos': especificos,
        'total_topics': len(comunes) + len(especificos),
        'comunes_count': len(comunes),
        'especificos_count': len(especificos),
        'comunes_matches': comunes_matches,
        'especificos_matches': especificos_matches,
        'matched_specific_topics': matched
    }


def main():
    print("\n" + "="*70)
    print("🔍 ANÁLISIS COMPARATIVO DE TEMARIOS vs ANEXO V")
    print("   (Arquitectos Técnicos - Gobierno de Aragón)")
    print("="*70)

    # Listar PDFs
    pdfs = list(TEMARIOS_PATH.glob("*.pdf"))
    print(f"\n📁 Temarios encontrados: {len(pdfs)}")

    results = []

    for pdf_path in sorted(pdfs):
        result = analyze_temario(pdf_path)
        results.append(result)

    # Tabla de resultados
    print("\n\n" + "="*90)
    print("📊 TABLA COMPARATIVA: COINCIDENCIA CON ANEXO V")
    print("="*90)

    # Referencia: Anexo V
    anexo_v = next((r for r in results if 'Anexo_V' in r['name']), None)

    print(f"\n🎯 REFERENCIA: Anexo V - Arquitectos Técnicos")
    if anexo_v:
        print(f"   Total: {anexo_v['comunes_count']} comunes + {anexo_v['especificos_count']} específicos = {anexo_v['total_topics']} temas")

    print("\n" + "-"*90)
    print(f"{'Temario':<40} {'Total':>6} {'Comunes':>10} {'Específ.':>10} {'% Coinc.':>12}")
    print("-"*90)

    comparison_results = []

    for r in results:
        if 'Anexo_V' in r['name']:
            continue  # Skip reference

        # Calcular % de coincidencia
        # Comunes: casi siempre iguales, contar matches
        # Específicos: contar matches con keywords
        total_possible = r['comunes_count'] + r['especificos_count']
        total_matches = r['comunes_matches'] + r['especificos_matches']
        pct = (total_matches / total_possible * 100) if total_possible > 0 else 0

        comparison_results.append({
            **r,
            'pct_match': pct
        })

        # Mostrar desglose
        comunes_str = f"{r['comunes_matches']}/{r['comunes_count']}"
        especificos_str = f"{r['especificos_matches']}/{r['especificos_count']}"

        print(f"{r['name'][:39]:<40} {r['total_topics']:>6} {comunes_str:>10} {especificos_str:>10} {pct:>10.1f}%")

    # Ordenar por coincidencia
    comparison_results.sort(key=lambda x: x['pct_match'], reverse=True)

    print("\n" + "="*90)
    print("📈 RANKING DE COINCIDENCIA CON ANEXO V")
    print("="*90)
    print()

    for i, r in enumerate(comparison_results, 1):
        # Determinar el tipo de temario
        tipo = ""
        if "Informática" in r['name']:
            tipo = "💻"
        elif "Delineantes" in r['name']:
            tipo = "📐"
        elif "Patrimonio" in r['name']:
            tipo = "🏛️"
        else:
            tipo = "📋"

        bar_len = int(r['pct_match'] / 2)  # Escala para mostrar barra
        bar = "█" * bar_len + "░" * (50 - bar_len)

        print(f"{i}. {tipo} {r['name']}")
        print(f"   [{bar}] {r['pct_match']:.1f}%")
        print(f"   Comunes: {r['comunes_matches']}/{r['comunes_count']} | Específicos: {r['especificos_matches']}/{r['especificos_count']}")
        print()

    # Recomendaciones
    print("="*90)
    print("💡 ANÁLISIS Y RECOMENDACIONES")
    print("="*90)

    print("""
Las materias COMUNES son prácticamente idénticas en todos los temarios de la
Administración de Aragón. Esto significa que estudiando las 5-10 materias comunes
de cualquier temario, ya tienes preparada esa parte para TODAS las oposiciones.

Las materias ESPECÍFICAS varían según el cuerpo:

• DELINEANTES (Anexo XXVII): Alto solapamiento con Arquitectos Técnicos
  - Comparten: CTE, estructuras, instalaciones, seguridad y salud, mediciones
  - Diferente: Mayor énfasis en CAD/BIM, cartografía y SIG

• PATRIMONIO (Anexo XXXIV): Solapamiento medio-bajo
  - Comparten: Patrimonio arquitectónico, rehabilitación
  - Diferente: Enfoque en conservación, museos, bienes culturales

• INFORMÁTICA (Anexos III y XXVI): Solapamiento muy bajo
  - Solo comparten materias comunes
  - Materias específicas completamente diferentes (software, redes, programación)
""")

    return results, comparison_results


if __name__ == "__main__":
    results, comparison = main()
