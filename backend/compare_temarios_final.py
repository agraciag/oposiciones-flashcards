"""
Script final para comparar temarios con Anexo V
Maneja diferentes formatos de PDF
"""

import fitz
import re
from pathlib import Path
import json

TEMARIOS_PATH = Path("/mnt/d/dev_projects/oposiciones-flashcards/Material de Estudio/temarios")


def extract_all_topics(pdf_path):
    """Extrae todos los temas de un PDF, manejando diferentes formatos"""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    doc.close()

    # Limpiar firmas
    full_text = re.sub(r'Firmado electrónicamente.*?(?=\n\d+\.|\n[A-Z]|\Z)', '', full_text, flags=re.DOTALL)
    full_text = re.sub(r'Documento verificado.*', '', full_text, flags=re.DOTALL)

    # Normalizar: "número.\n" -> "número. "
    full_text = re.sub(r'(\d+)\.\s*\n', r'\1. ', full_text)

    # Buscar secciones (con variaciones)
    # Variantes: "Programa de materias comunes", "Programa materias comunes"
    comunes_patterns = [
        r'Programa de materias comunes[.\s]*\n([\s\S]*?)(?=Programa\s+(?:de\s+)?materias\s+específicas)',
        r'Programa materias comunes[.\s]*\n([\s\S]*?)(?=Programa\s+(?:de\s+)?materias\s+específicas)',
    ]

    especificas_patterns = [
        r'Programa\s+(?:de\s+)?materias\s+específicas[.\s]*\n([\s\S]*)',
    ]

    comunes_text = ""
    especificas_text = ""

    for pattern in comunes_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            comunes_text = match.group(1)
            break

    for pattern in especificas_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            especificas_text = match.group(1)
            break

    # Si no hay secciones explícitas, extraer todos los temas del texto
    if not comunes_text and not especificas_text:
        # Buscar inicio del contenido después del título
        start_match = re.search(r'(?:Técnicos de Informática|Programa de materias)\.\s*\n', full_text, re.IGNORECASE)
        if start_match:
            especificas_text = full_text[start_match.end():]
        else:
            especificas_text = full_text

    def parse_topics(section_text):
        """Extrae temas numerados de una sección"""
        if not section_text:
            return []

        topics = []
        pattern = r'(\d+)\.\s+([\s\S]*?)(?=(?:\n|\s)\d+\.\s|$)'
        matches = re.findall(pattern, section_text)

        for num, content in matches:
            content = re.sub(r'\s+', ' ', content).strip()
            content = re.sub(r'\s*–\s*\d+\s*–\s*', '', content)
            if len(content) > 20:
                topics.append((int(num), content))

        return topics

    comunes = parse_topics(comunes_text)
    especificos = parse_topics(especificas_text)

    return comunes, especificos, full_text


def analyze_temario(pdf_path):
    """Analiza un temario"""
    name = pdf_path.stem
    comunes, especificos, _ = extract_all_topics(pdf_path)

    return {
        'name': name,
        'filename': pdf_path.name,
        'comunes': comunes,
        'especificos': especificos,
        'total_comunes': len(comunes),
        'total_especificos': len(especificos),
        'total': len(comunes) + len(especificos)
    }


def calculate_topic_overlap(topics_source, topics_target):
    """Calcula solapamiento entre dos listas de temas basado en keywords"""
    if not topics_source or not topics_target:
        return 0, []

    matches = []

    # Extraer keywords significativas de los temas objetivo
    target_keywords = {}
    for num, topic in topics_target:
        # Extraer palabras de más de 5 caracteres
        words = re.findall(r'\b[a-záéíóúñA-ZÁÉÍÓÚÑ]{5,}\b', topic.lower())
        for word in words:
            if word not in ['según', 'sobre', 'entre', 'desde', 'hasta', 'mediante', 'durante', 'antes', 'después']:
                if word not in target_keywords:
                    target_keywords[word] = []
                target_keywords[word].append(num)

    # Buscar coincidencias en los temas fuente
    matched_source = set()
    for num_s, topic_s in topics_source:
        topic_lower = topic_s.lower()
        for keyword in target_keywords:
            if keyword in topic_lower and num_s not in matched_source:
                matched_source.add(num_s)
                matches.append((num_s, topic_s[:60], keyword))
                break

    return len(matches), matches


def main():
    print("\n" + "="*80)
    print("🔍 ANÁLISIS COMPARATIVO DE TEMARIOS - OPOSICIONES ARAGÓN")
    print("="*80)

    pdfs = sorted(TEMARIOS_PATH.glob("*.pdf"))
    results = {}

    print(f"\n📁 Procesando {len(pdfs)} temarios...\n")

    for pdf_path in pdfs:
        data = analyze_temario(pdf_path)
        results[data['name']] = data
        print(f"✅ {data['name']}: {data['total_comunes']} comunes + {data['total_especificos']} específicos = {data['total']} total")

    # Obtener Anexo V como referencia
    anexo_v = results.get('Anexo_V_Arquitectos Técnicos')
    if not anexo_v:
        print("❌ No se encontró Anexo V")
        return

    print("\n" + "="*80)
    print("📊 COMPARACIÓN CON ANEXO V (Arquitectos Técnicos)")
    print("="*80)
    print(f"\n🎯 REFERENCIA: {anexo_v['total_comunes']} comunes + {anexo_v['total_especificos']} específicos = {anexo_v['total']} temas\n")

    # Keywords específicos del Anexo V (Arquitectura/Construcción)
    anexo_v_specific_keywords = [
        'edificación', 'urbanístico', 'planeamiento', 'suelo', 'cte', 'código técnico',
        'estructural', 'cimentaciones', 'hormigón', 'acero', 'madera', 'fábrica',
        'incendio', 'evacuación', 'accesibilidad', 'salubridad', 'humedad',
        'ruido', 'acústico', 'ahorro energía', 'energética', 'rite', 'térmica',
        'fontanería', 'saneamiento', 'electricidad', 'climatización', 'gas',
        'telecomunicaciones', 'ascensores', 'elevadores',
        'seguridad salud', 'prevención', 'obra', 'construcción',
        'mediciones', 'presupuestos', 'programación',
        'calidad', 'proyecto', 'dirección obra',
        'mantenimiento', 'rehabilitación', 'patología',
        'patrimonio arquitectónico', 'vivienda', 'protección oficial'
    ]

    # Keywords comunes (todos los cuerpos)
    common_keywords = [
        'constitución', 'aragón', 'estatuto', 'autonomía',
        'administración', 'territorial', 'local', 'municipio',
        'funcionario', 'empleado público', 'incompatibilidades',
        'procedimiento', 'administrativo', 'contratos', 'patrimonio público',
        'igualdad', 'género', 'discapacidad', 'prevención riesgos'
    ]

    comparisons = []

    for name, data in results.items():
        if 'Anexo_V' in name:
            continue

        # Calcular coincidencias en materias comunes
        comunes_match = 0
        for num, topic in data['comunes']:
            topic_lower = topic.lower()
            for kw in common_keywords:
                if kw in topic_lower:
                    comunes_match += 1
                    break

        # Calcular coincidencias en materias específicas
        especificos_match = 0
        matched_topics = []
        for num, topic in data['especificos']:
            topic_lower = topic.lower()
            for kw in anexo_v_specific_keywords:
                if kw in topic_lower:
                    especificos_match += 1
                    matched_topics.append((num, topic[:50], kw))
                    break

        # Si no hay sección de comunes, considerar los primeros temas como comunes
        if data['total_comunes'] == 0 and data['total_especificos'] > 0:
            # Los primeros 5-10 temas suelen ser comunes
            for num, topic in data['especificos'][:10]:
                topic_lower = topic.lower()
                for kw in common_keywords:
                    if kw in topic_lower:
                        comunes_match += 1
                        break

        total = data['total'] if data['total'] > 0 else 1
        total_match = comunes_match + especificos_match
        pct = (total_match / total) * 100

        comparisons.append({
            'name': name,
            'total': data['total'],
            'comunes': data['total_comunes'],
            'especificos': data['total_especificos'],
            'comunes_match': comunes_match,
            'especificos_match': especificos_match,
            'pct': pct,
            'matched_topics': matched_topics,
            'topics_comunes': data['comunes'],
            'topics_especificos': data['especificos']
        })

    # Ordenar por % coincidencia
    comparisons.sort(key=lambda x: x['pct'], reverse=True)

    # Tabla de resultados
    print("-"*85)
    print(f"{'TEMARIO':<42} {'TOTAL':>6} {'COM':>5} {'ESP':>5} {'MATCH':>8} {'%':>8}")
    print("-"*85)

    for c in comparisons:
        match_str = f"{c['comunes_match']}+{c['especificos_match']}"
        display_name = c['name'].replace('_', ' ')[:41]
        print(f"{display_name:<42} {c['total']:>6} {c['comunes']:>5} {c['especificos']:>5} {match_str:>8} {c['pct']:>7.1f}%")

    # Ranking visual
    print("\n" + "="*80)
    print("📈 RANKING: COMPATIBILIDAD CON ANEXO V (Arquitectos Técnicos)")
    print("="*80 + "\n")

    icons = {'Informática': '💻', 'Delineantes': '📐', 'Patrimonio': '🏛️'}

    for i, c in enumerate(comparisons, 1):
        icon = next((ico for key, ico in icons.items() if key in c['name']), '📋')

        bar_len = min(50, int(c['pct'] / 2))
        bar = '█' * bar_len + '░' * (50 - bar_len)

        display_name = c['name'].replace('_', ' ')
        print(f"{i}. {icon} {display_name}")
        print(f"   [{bar}] {c['pct']:.1f}%")
        print(f"   {c['total']} temas | Coinciden: {c['comunes_match']} comunes + {c['especificos_match']} específicos")

        if c['matched_topics'][:3]:
            print(f"   Temas coincidentes con Anexo V:")
            for num, topic, kw in c['matched_topics'][:3]:
                print(f"     • {num}. {topic}... (→ {kw})")
        print()

    # Análisis detallado
    print("="*80)
    print("💡 ANÁLISIS DETALLADO")
    print("="*80)

    for c in comparisons:
        display_name = c['name'].replace('_', ' ')
        print(f"\n### {display_name} ###")
        print(f"Coincidencia: {c['pct']:.1f}%")

        if 'Delineantes' in c['name']:
            print("""
ALTA COMPATIBILIDAD (recomendado como 2ª opción)
- Comparten muchos temas de construcción y edificación
- Mismo perfil técnico (arquitectura/ingeniería)
- Temas específicos de Delineantes: CAD, BIM, cartografía, topografía
- Esfuerzo adicional moderado para preparar ambas oposiciones
""")
        elif 'Patrimonio' in c['name']:
            print("""
COMPATIBILIDAD MEDIA
- Comparten tema de patrimonio arquitectónico
- Las materias comunes son similares a todos los cuerpos
- Específicos muy diferentes: conservación, museos, bienes culturales
- Requiere estudio adicional significativo
""")
        elif 'Informática' in c['name']:
            print("""
BAJA COMPATIBILIDAD
- Solo comparten las materias comunes (Constitución, Aragón, etc.)
- Específicos completamente diferentes (programación, redes, bases de datos)
- No recomendado como combinación a menos que tengas formación en ambos campos
""")

    # Recomendación final
    print("\n" + "="*80)
    print("🎯 RECOMENDACIÓN FINAL")
    print("="*80)

    best = comparisons[0] if comparisons else None
    if best:
        display_name = best['name'].replace('_', ' ')
        print(f"""
Si estás preparando el Anexo V (Arquitectos Técnicos), tu mejor opción
complementaria es:

  ★ {display_name} ({best['pct']:.1f}% coincidencia)

Las MATERIAS COMUNES (Constitución, Estatuto de Aragón, procedimiento
administrativo, etc.) son prácticamente idénticas en todos los temarios.
Estudiándolas UNA vez, ya las tienes para TODAS las oposiciones.

La diferencia principal está en las MATERIAS ESPECÍFICAS:
- Arquitectos Técnicos: Edificación, CTE, urbanismo, instalaciones
- Delineantes: CAD, BIM, cartografía, representación gráfica
- Patrimonio: Conservación, museos, protección cultural
- Informática: Programación, redes, bases de datos
""")

    # Guardar para crear syllabi
    export = {
        'anexo_v': {
            'comunes': anexo_v['comunes'],
            'especificos': anexo_v['especificos']
        },
        'comparisons': [{
            'name': c['name'],
            'pct': c['pct'],
            'comunes': c['topics_comunes'],
            'especificos': c['topics_especificos']
        } for c in comparisons]
    }

    with open('temarios_comparison.json', 'w', encoding='utf-8') as f:
        json.dump(export, f, ensure_ascii=False, indent=2)

    print("\n📁 Datos guardados en temarios_comparison.json")

    return results, comparisons


if __name__ == "__main__":
    results, comparisons = main()
