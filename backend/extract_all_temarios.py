"""
Script mejorado para extraer TODOS los temas de cada temario PDF
"""

import fitz  # PyMuPDF
import re
from pathlib import Path
import json

TEMARIOS_PATH = Path("/mnt/d/dev_projects/oposiciones-flashcards/Material de Estudio/temarios")


def extract_and_clean_text(pdf_path):
    """Extrae y limpia el texto de un PDF"""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        text = page.get_text()
        full_text += text + "\n"
    doc.close()

    # Eliminar firmas electrónicas y pies de página
    full_text = re.sub(r'Firmado electrónicamente.*?(?=\n\d+\.|\n[A-Z]|\Z)', '', full_text, flags=re.DOTALL)
    full_text = re.sub(r'Documento verificado.*?CSV\s+\w+\.?', '', full_text, flags=re.DOTALL)

    return full_text


def extract_topics_improved(text):
    """Extrae temas con patrón mejorado"""
    # Separar comunes y específicos
    comunes_section = ""
    especificos_section = ""

    # Buscar las secciones
    comunes_match = re.search(
        r'Programa de materias comunes[.\s]*\n([\s\S]*?)(?=Programa de materias específicas)',
        text, re.IGNORECASE
    )
    especificos_match = re.search(
        r'Programa de materias específicas[.\s]*\n([\s\S]*)',
        text, re.IGNORECASE
    )

    if comunes_match:
        comunes_section = comunes_match.group(1)
    if especificos_match:
        especificos_section = especificos_match.group(1)

    def parse_section(section_text):
        """Parsea una sección para extraer temas"""
        topics = []
        if not section_text:
            return topics

        # Normalizar: convertir "número.\n" en "número. "
        section_text = re.sub(r'(\d+)\.\s*\n', r'\1. ', section_text)

        # Patrón: número seguido de punto, luego contenido hasta el siguiente número o fin
        pattern = r'(\d+)\.\s+([\s\S]*?)(?=(?:\n|\s)\d+\.\s|$)'
        matches = re.findall(pattern, section_text)

        for num, content in matches:
            # Limpiar contenido
            content = re.sub(r'\s+', ' ', content).strip()
            content = re.sub(r'\s*–\s*\d+\s*–\s*', '', content)  # Eliminar numeración de página
            if len(content) > 20:
                topics.append((int(num), content))

        return topics

    comunes = parse_section(comunes_section)
    especificos = parse_section(especificos_section)

    return comunes, especificos


def analyze_all_temarios():
    """Analiza todos los temarios y extrae sus temas"""
    results = {}

    pdfs = sorted(TEMARIOS_PATH.glob("*.pdf"))
    print(f"Encontrados {len(pdfs)} archivos PDF\n")

    for pdf_path in pdfs:
        print(f"{'='*70}")
        print(f"📄 {pdf_path.name}")
        print('='*70)

        text = extract_and_clean_text(pdf_path)
        comunes, especificos = extract_topics_improved(text)

        # Determinar el nombre limpio
        name = pdf_path.stem
        clean_name = name.replace('_', ' ').replace('Anexo ', 'Anexo ')

        results[name] = {
            'filename': pdf_path.name,
            'display_name': clean_name,
            'comunes': comunes,
            'especificos': especificos,
            'total_comunes': len(comunes),
            'total_especificos': len(especificos)
        }

        print(f"  Materias comunes: {len(comunes)} temas")
        print(f"  Materias específicas: {len(especificos)} temas")
        print(f"  TOTAL: {len(comunes) + len(especificos)} temas")

        if comunes:
            print(f"\n  Primeros comunes:")
            for num, topic in comunes[:2]:
                print(f"    {num}. {topic[:70]}...")

        if especificos:
            print(f"\n  Primeros específicos:")
            for num, topic in especificos[:2]:
                print(f"    {num}. {topic[:70]}...")

        print()

    return results


def compare_with_anexo_v(results):
    """Compara todos los temarios con Anexo V"""
    anexo_v = results.get('Anexo_V_Arquitectos Técnicos')
    if not anexo_v:
        print("No se encontró Anexo V como referencia")
        return

    # Keywords de los temas específicos de Anexo V
    anexo_v_keywords = []
    for num, topic in anexo_v['especificos']:
        # Extraer palabras clave del tema
        words = re.findall(r'\b[A-ZÁÉÍÓÚ][a-záéíóúñ]+(?:\s+[a-záéíóúñ]+)*\b', topic)
        keywords = [w.lower() for w in words if len(w) > 4]
        anexo_v_keywords.extend(keywords[:5])  # Tomar las primeras 5 palabras clave de cada tema

    # Keywords distintivas del Anexo V
    distintive_keywords = [
        'edificación', 'cte', 'código técnico', 'urbanístico', 'planeamiento',
        'estructuras', 'cimentaciones', 'incendio', 'accesibilidad',
        'instalaciones', 'fontanería', 'saneamiento', 'electricidad',
        'climatización', 'gas', 'telecomunicaciones', 'ascensores',
        'seguridad y salud', 'mediciones', 'presupuestos', 'obra',
        'mantenimiento', 'rehabilitación', 'patrimonio', 'eficiencia energética',
        'certificación energética', 'ruido', 'salubridad', 'ahorro de energía',
        'educación', 'centros docentes', 'sistema educativo'
    ]

    print("\n" + "="*80)
    print("📊 COMPARACIÓN CON ANEXO V (Arquitectos Técnicos)")
    print("="*80)
    print(f"\nReferencia: Anexo V tiene {anexo_v['total_comunes']} comunes + {anexo_v['total_especificos']} específicos")

    comparisons = []

    for name, data in results.items():
        if 'Anexo_V' in name:
            continue

        # Contar coincidencias en materias comunes (por similitud de keywords)
        comunes_match = 0
        for num, topic in data['comunes']:
            topic_lower = topic.lower()
            # Buscar keywords comunes como constitución, aragón, etc
            common_keywords = ['constitución', 'aragón', 'administración', 'territorio', 'igualdad', 'prevención']
            for kw in common_keywords:
                if kw in topic_lower:
                    comunes_match += 1
                    break

        # Contar coincidencias en materias específicas
        especificos_match = 0
        matched_topics = []
        for num, topic in data['especificos']:
            topic_lower = topic.lower()
            for kw in distintive_keywords:
                if kw in topic_lower:
                    especificos_match += 1
                    matched_topics.append((num, topic[:50], kw))
                    break

        total = data['total_comunes'] + data['total_especificos']
        total_match = comunes_match + especificos_match
        pct = (total_match / total * 100) if total > 0 else 0

        comparisons.append({
            'name': name,
            'display_name': data['display_name'],
            'total': total,
            'comunes': data['total_comunes'],
            'especificos': data['total_especificos'],
            'comunes_match': comunes_match,
            'especificos_match': especificos_match,
            'pct': pct,
            'matched_topics': matched_topics
        })

    # Ordenar por coincidencia
    comparisons.sort(key=lambda x: x['pct'], reverse=True)

    print("\n" + "-"*80)
    print(f"{'Temario':<45} {'Total':>6} {'Com.':>6} {'Esp.':>6} {'Match':>8} {'%':>8}")
    print("-"*80)

    for c in comparisons:
        match_str = f"{c['comunes_match']}+{c['especificos_match']}"
        print(f"{c['display_name'][:44]:<45} {c['total']:>6} {c['comunes']:>6} {c['especificos']:>6} {match_str:>8} {c['pct']:>7.1f}%")

    # Mostrar ranking visual
    print("\n" + "="*80)
    print("📈 RANKING DE COINCIDENCIA CON ANEXO V")
    print("="*80 + "\n")

    icons = {
        'Informática': '💻',
        'Delineantes': '📐',
        'Patrimonio': '🏛️',
        'Ejecutivos': '💻'
    }

    for i, c in enumerate(comparisons, 1):
        icon = '📋'
        for key, ico in icons.items():
            if key in c['name']:
                icon = ico
                break

        bar_len = int(c['pct'] / 2)
        bar = '█' * bar_len + '░' * (50 - bar_len)

        print(f"{i}. {icon} {c['display_name']}")
        print(f"   [{bar}] {c['pct']:.1f}%")
        print(f"   Total: {c['total']} temas | Comunes: {c['comunes_match']}/{c['comunes']} | Específicos: {c['especificos_match']}/{c['especificos']}")

        if c['matched_topics']:
            print(f"   Temas coincidentes:")
            for num, topic, kw in c['matched_topics'][:3]:
                print(f"     • Tema {num}: {topic}... (keyword: {kw})")
        print()

    return comparisons


def main():
    results = analyze_all_temarios()
    comparisons = compare_with_anexo_v(results)

    # Guardar resultados para crear syllabi
    print("\n" + "="*80)
    print("💾 GUARDANDO DATOS PARA CREAR SYLLABI")
    print("="*80)

    # Exportar a JSON para usar en seed
    export_data = {}
    for name, data in results.items():
        export_data[name] = {
            'display_name': data['display_name'],
            'comunes': [(num, topic) for num, topic in data['comunes']],
            'especificos': [(num, topic) for num, topic in data['especificos']]
        }

    with open('temarios_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print("Datos guardados en temarios_extracted.json")

    return results, comparisons


if __name__ == "__main__":
    results, comparisons = main()
