"""
Análisis completo y comparación de temarios de oposiciones de Aragón
"""

import fitz
import re
from pathlib import Path
import json

TEMARIOS_PATH = Path("/mnt/d/dev_projects/oposiciones-flashcards/Material de Estudio/temarios")


def extract_all_topics_robust(pdf_path):
    """Extrae todos los temas de un PDF de forma robusta"""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    doc.close()

    # Limpiar firmas y pies de página
    full_text = re.sub(r'Firmado electrónicamente.*?(?=\n\d+\.|\Z)', '', full_text, flags=re.DOTALL)
    full_text = re.sub(r'Documento verificado.*', '', full_text)

    # Normalizar saltos de línea después de números
    full_text = re.sub(r'(\d+)\.\s*\n', r'\1. ', full_text)

    # Detectar secciones
    has_comunes = bool(re.search(r'materias comunes', full_text, re.IGNORECASE))
    has_especificas = bool(re.search(r'materias específicas', full_text, re.IGNORECASE))

    comunes = []
    especificos = []

    if has_comunes and has_especificas:
        # Separar secciones
        parts = re.split(r'Programa\s+(?:de\s+)?materias\s+específicas', full_text, flags=re.IGNORECASE)
        if len(parts) >= 2:
            comunes_text = parts[0]
            especificos_text = parts[1]

            # Extraer temas de cada sección
            comunes = extract_numbered_topics(comunes_text)
            especificos = extract_numbered_topics(especificos_text)
    else:
        # Sin secciones explícitas - todos son temas mezclados
        # Buscar el inicio del contenido
        match = re.search(r'(?:Programa de materias|Informática)\.\s*\n', full_text, re.IGNORECASE)
        if match:
            content = full_text[match.end():]
        else:
            content = full_text

        all_topics = extract_numbered_topics(content)

        # Los primeros temas que mencionan constitución, aragón, etc son comunes
        for num, topic in all_topics:
            topic_lower = topic.lower()
            is_common = any(kw in topic_lower for kw in [
                'constitución', 'aragón', 'estatuto', 'autonomía',
                'administración', 'territorial', 'funcionari', 'empleado público',
                'procedimiento', 'unión europea', 'igualdad', 'prevención riesgos'
            ])
            if is_common:
                comunes.append((num, topic))
            else:
                especificos.append((num, topic))

    return comunes, especificos


def extract_numbered_topics(text):
    """Extrae temas numerados de un texto"""
    topics = []
    # Patrón: número + punto + espacio + contenido hasta el siguiente número o fin
    pattern = r'(\d+)\.\s+([A-ZÁÉÍÓÚÑ][\s\S]*?)(?=\d+\.\s+[A-ZÁÉÍÓÚÑ]|\Z)'
    matches = re.findall(pattern, text)

    for num, content in matches:
        # Limpiar
        content = re.sub(r'\s+', ' ', content).strip()
        if len(content) > 20:
            topics.append((int(num), content))

    return topics


def analyze_overlap(topics_source, anexo_v_keywords):
    """Analiza solapamiento con keywords del Anexo V"""
    matches = 0
    matched_topics = []

    for num, topic in topics_source:
        topic_lower = topic.lower()
        for keyword in anexo_v_keywords:
            if keyword in topic_lower:
                matches += 1
                matched_topics.append((num, topic[:60], keyword))
                break

    return matches, matched_topics


def main():
    print("\n" + "="*85)
    print("🔍 ANÁLISIS COMPARATIVO DE TEMARIOS - OPOSICIONES GOBIERNO DE ARAGÓN")
    print("="*85)

    # Keywords específicos de Arquitectos Técnicos (Anexo V)
    ANEXO_V_ESPECIFICOS_KEYWORDS = [
        'edificación', 'urbanístic', 'planeamiento', 'clasificación del suelo',
        'cte', 'código técnico', 'estructural', 'cimentacion',
        'hormigón', 'acero', 'madera', 'fábrica', 'metálica',
        'incendio', 'evacuación', 'si-', 'db-si',
        'accesibilidad', 'sua', 'db-sua',
        'salubridad', 'humedad', 'hs', 'db-hs',
        'ruido', 'acústic', 'hr', 'db-hr',
        'ahorro de energía', 'eficiencia energética', 'he', 'db-he', 'rite',
        'fontanería', 'saneamiento', 'electricidad', 'climatización',
        'instalaciones de gas', 'telecomunicaciones', 'ascensor', 'elevador',
        'seguridad y salud', 'coordinador', 'estudio de seguridad',
        'mediciones', 'presupuestos', 'programación de obras', 'pert', 'gantt',
        'control de calidad', 'recepción de productos',
        'proyecto de obras', 'dirección de obra', 'certificaciones',
        'mantenimiento', 'ite', 'libro del edificio',
        'rehabilitación', 'patología', 'patrimonio arquitectónico',
        'vivienda protegida', 'vpo', 'valoraciones',
        'sig', 'información geográfica', 'cartografía catastral'
    ]

    COMUNES_KEYWORDS = [
        'constitución', 'aragón', 'estatuto', 'autonomía',
        'administración', 'territorial', 'local', 'provincias', 'municipios',
        'funcionari', 'empleado público', 'incompatibilidades', 'retributivo',
        'procedimiento administrativo', 'sancionador',
        'contratos del sector público', 'patrimoni', 'dominio público',
        'responsabilidad', 'cortes generales', 'poder judicial',
        'igualdad', 'género', 'violencia', 'discapacidad',
        'prevención de riesgos', 'unión europea'
    ]

    # Procesar todos los PDFs
    results = {}

    for pdf_path in sorted(TEMARIOS_PATH.glob("*.pdf")):
        name = pdf_path.stem
        comunes, especificos = extract_all_topics_robust(pdf_path)

        results[name] = {
            'comunes': comunes,
            'especificos': especificos,
            'total_comunes': len(comunes),
            'total_especificos': len(especificos),
            'total': len(comunes) + len(especificos)
        }

        print(f"\n📄 {name}")
        print(f"   Comunes: {len(comunes)} | Específicos: {len(especificos)} | Total: {len(comunes) + len(especificos)}")

    # Comparar con Anexo V
    anexo_v = results.get('Anexo_V_Arquitectos Técnicos')
    if not anexo_v:
        print("❌ Anexo V no encontrado")
        return

    print("\n" + "="*85)
    print("📊 COMPARACIÓN: % DE MATERIAL COMPARTIDO CON ANEXO V (Arquitectos Técnicos)")
    print("="*85)
    print(f"\n🎯 REFERENCIA: Anexo V tiene {anexo_v['total']} temas ({anexo_v['total_comunes']} comunes + {anexo_v['total_especificos']} específicos)\n")

    comparisons = []

    for name, data in results.items():
        if 'Anexo_V' in name:
            continue

        # Calcular coincidencias en comunes
        comunes_match, _ = analyze_overlap(data['comunes'], COMUNES_KEYWORDS)

        # Para temarios sin sección explícita de comunes, buscar en todos
        if data['total_comunes'] == 0:
            comunes_match, _ = analyze_overlap(data['especificos'][:15], COMUNES_KEYWORDS)

        # Calcular coincidencias en específicos con keywords de Anexo V
        especificos_match, matched = analyze_overlap(data['especificos'], ANEXO_V_ESPECIFICOS_KEYWORDS)

        # Calcular porcentajes
        total_este = data['total'] if data['total'] > 0 else 1
        pct_material_compartido = ((comunes_match + especificos_match) / total_este) * 100

        comparisons.append({
            'name': name,
            'display_name': name.replace('_', ' '),
            'total': data['total'],
            'total_comunes': data['total_comunes'],
            'total_especificos': data['total_especificos'],
            'comunes_match': comunes_match,
            'especificos_match': especificos_match,
            'pct': pct_material_compartido,
            'matched': matched,
            'raw_comunes': data['comunes'],
            'raw_especificos': data['especificos']
        })

    # Ordenar por coincidencia
    comparisons.sort(key=lambda x: x['pct'], reverse=True)

    # Tabla de resultados
    print("-"*85)
    print(f"{'TEMARIO':<45} {'TEMAS':>7} {'COM':>6} {'ESP':>6} {'%COINC':>10}")
    print("-"*85)

    for c in comparisons:
        match_info = f"({c['comunes_match']}+{c['especificos_match']})"
        print(f"{c['display_name'][:44]:<45} {c['total']:>7} {c['total_comunes']:>6} {c['total_especificos']:>6} {c['pct']:>8.1f}%")

    # Ranking visual detallado
    print("\n" + "="*85)
    print("📈 RANKING: COMPATIBILIDAD CON ANEXO V (de mayor a menor)")
    print("="*85)

    icons = {'Informática': '💻', 'Delineantes': '📐', 'Patrimonio': '🏛️'}

    for i, c in enumerate(comparisons, 1):
        icon = next((ico for key, ico in icons.items() if key in c['name']), '📋')

        # Barra de progreso
        bar_len = min(40, int(c['pct'] * 0.4))
        bar = '█' * bar_len + '░' * (40 - bar_len)

        print(f"\n{i}. {icon} {c['display_name']}")
        print(f"   Material compartido: [{bar}] {c['pct']:.1f}%")
        print(f"   Temas totales: {c['total']} ({c['total_comunes']} comunes + {c['total_especificos']} específicos)")
        print(f"   Coinciden con Anexo V: {c['comunes_match']} comunes + {c['especificos_match']} específicos")

        if c['matched'][:4]:
            print(f"   Temas específicos que coinciden:")
            for num, topic, kw in c['matched'][:4]:
                print(f"     • Tema {num}: {topic}... (→{kw})")

    # Análisis y recomendaciones
    print("\n" + "="*85)
    print("💡 ANÁLISIS Y RECOMENDACIONES")
    print("="*85)

    print("""
┌─────────────────────────────────────────────────────────────────────────────────┐
│ MATERIAS COMUNES (aprox. 5-10 temas por temario)                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│ • Constitución Española                                                          │
│ • Estatuto de Autonomía de Aragón                                                │
│ • Organización territorial del Estado                                            │
│ • Administración Local                                                           │
│ • Empleado Público / Funcionarios                                                │
│ • Procedimiento Administrativo                                                   │
│ • Contratos del Sector Público                                                   │
│ • Igualdad de género / Discapacidad                                              │
│                                                                                  │
│ ✅ ESTOS TEMAS SON PRÁCTICAMENTE IDÉNTICOS EN TODOS LOS TEMARIOS                 │
│ ✅ Estudiándolos UNA vez, los tienes para TODAS las oposiciones de Aragón        │
└─────────────────────────────────────────────────────────────────────────────────┘
""")

    # Recomendación específica por temario
    for c in comparisons:
        print(f"\n### {c['display_name']} ###")

        if 'Delineantes' in c['name']:
            print(f"""
📐 ALTA COMPATIBILIDAD CON ARQUITECTOS TÉCNICOS ({c['pct']:.1f}%)

TEMAS COMPARTIDOS:
• Código Técnico de la Edificación (CTE)
• Estructuras y cimentaciones
• Seguridad y salud en obras
• Mediciones y presupuestos
• Proyectos de obras

TEMAS PROPIOS DE DELINEANTES:
• CAD y BIM (AutoCAD, Revit)
• Cartografía y SIG
• Topografía
• Representación gráfica

✅ RECOMENDADO como 2ª opción si preparas Arquitectos Técnicos
   Aprovechas gran parte del estudio.
""")
        elif 'Patrimonio' in c['name']:
            print(f"""
🏛️ COMPATIBILIDAD MEDIA ({c['pct']:.1f}%)

TEMAS COMPARTIDOS:
• Patrimonio arquitectónico (también en Anexo V)
• Rehabilitación de edificios
• Materias comunes

TEMAS PROPIOS DE PATRIMONIO:
• Ley de Patrimonio Cultural Aragonés
• Conservación y restauración
• Museos y archivos
• Bienes de interés cultural

⚠️ Solo recomendado si tienes interés específico en patrimonio cultural
""")
        elif 'Informática' in c['name']:
            print(f"""
💻 BAJA COMPATIBILIDAD ({c['pct']:.1f}%)

TEMAS COMPARTIDOS:
• Solo las materias comunes (Constitución, Aragón, etc.)

TEMAS PROPIOS DE INFORMÁTICA:
• Programación y desarrollo
• Bases de datos
• Redes y telecomunicaciones
• Sistemas operativos
• Seguridad informática

❌ No recomendado como combinación con Arquitectos Técnicos
   Las materias específicas son completamente diferentes.
""")

    # Conclusión final
    best = comparisons[0]
    print("\n" + "="*85)
    print("🎯 CONCLUSIÓN")
    print("="*85)
    print(f"""
Si estás preparando el ANEXO V (Arquitectos Técnicos), la mejor combinación es:

   ★ {best['display_name']} ({best['pct']:.1f}% material compartido)

Estrategia recomendada:
1. Estudia las MATERIAS COMUNES una sola vez (sirven para ambas)
2. Estudia las MATERIAS ESPECÍFICAS de Arq. Técnicos (base principal)
3. Complementa con los temas propios de Delineantes (CAD, BIM, cartografía)

Así maximizas el aprovechamiento de tu tiempo de estudio.
""")

    # Guardar datos para crear syllabi
    export_data = {
        'anexo_v_total': anexo_v['total'],
        'comparisons': []
    }

    for c in comparisons:
        export_data['comparisons'].append({
            'name': c['name'],
            'display_name': c['display_name'],
            'total': c['total'],
            'pct_match': c['pct'],
            'comunes': [(n, t) for n, t in c['raw_comunes']],
            'especificos': [(n, t) for n, t in c['raw_especificos']]
        })

    with open('temarios_analisis_final.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print("\n📁 Datos exportados a temarios_analisis_final.json")

    return results, comparisons


if __name__ == "__main__":
    results, comparisons = main()
