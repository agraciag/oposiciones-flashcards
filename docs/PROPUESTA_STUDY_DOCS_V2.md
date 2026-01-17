# Propuesta de Evolución: Study-Docs V2

## 1. Mejoras de la Solución Actual

### 1.1 Problemas Identificados
- Panel lateral con ancho fijo (`w-96` = 384px)
- Contenido del documento sin capacidad de redimensionado
- Dificultad de lectura en sesiones prolongadas
- Sin modo de lectura/estudio enfocado

### 1.2 Mejoras Propuestas de UI

#### A) Panel Lateral Redimensionable
```
┌─────────────────────────────────────────────────────┐
│ Header                                              │
├─────────────────────────────┬───┬───────────────────┤
│                             │ ▐ │                   │
│     Documento               │ ▐ │   Panel Lateral   │
│     (flex-grow)             │ ▐ │   (resizable)     │
│                             │ ▐ │                   │
│                             │ ▐ │                   │
└─────────────────────────────┴───┴───────────────────┘
                              ↑
                        Divisor draggable
```

**Implementación**: Usar `react-resizable-panels` o CSS resize nativo.

#### B) Modos de Visualización
1. **Modo Estudio**: Panel lateral visible, selección habilitada
2. **Modo Lectura**: Sin panel, documento maximizado, tipografía optimizada
3. **Modo Inmersivo**: Pantalla completa, alto contraste opcional

#### C) Mejoras de Legibilidad
- Control de tamaño de fuente (persistido en localStorage)
- Interlineado ajustable
- Modo oscuro mejorado con contraste optimizado
- Fuentes con serifa para lectura prolongada

---

## 2. Nuevo Formato: Visualización Estructurada y Colapsable

### 2.1 Concepto
Transformar el temario en una estructura de árbol navegable donde cada nodo puede:
- Colapsarse/expandirse
- Mostrar contenido procesado desde normativa
- Indicar estado de completitud del contenido

### 2.2 Ejemplo Visual
```
📚 TEMARIO ARQUITECTOS TÉCNICOS (Anexo V)
├─ 📖 PARTE I - MATERIAS COMUNES (10 temas)
│   ├─ 📄 Tema 1: La Constitución Española de 1978
│   │   ├─ ▼ Estructura y contenido básico
│   │   │     └─ [Contenido extraído de BOE-A-1978-31229]
│   │   ├─ ▶ Título Preliminar
│   │   ├─ ▶ Derechos fundamentales
│   │   └─ ▶ La Corona
│   ├─ 📄 Tema 2: Legislación estatal en materia de régimen del suelo
│   │   ├─ ▼ Legislación urbanística en la Comunidad Autónoma de Aragón
│   │   │     ├─ Situaciones del suelo
│   │   │     ├─ Clases del suelo
│   │   │     └─ Categorías del suelo
│   │   └─ ▶ Real Decreto Legislativo 7/2015
│   └─ ...
└─ 📖 PARTE II - MATERIAS ESPECÍFICAS (45 temas)
    ├─ 📄 Tema 11: El Código Técnico de la Edificación
    │   ├─ ▼ Parte I - Disposiciones generales
    │   │     └─ [Contenido de Parte_I_jun2022.pdf]
    │   ├─ ▶ DB-SE Seguridad Estructural
    │   └─ ▶ DB-SI Seguridad en caso de incendio
    └─ ...
```

### 2.3 Modelo de Datos Extendido

```python
class StructuredTopic(Base):
    """Tema estructurado del temario"""
    __tablename__ = "structured_topics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    syllabus_id = Column(Integer, ForeignKey("syllabi.id"))  # Referencia al temario

    # Jerarquía
    parent_id = Column(Integer, ForeignKey("structured_topics.id"), nullable=True)
    order_index = Column(Integer, default=0)
    level = Column(Integer, default=0)  # 0=raíz, 1=parte, 2=tema, 3=subtema...

    # Contenido
    title = Column(String, nullable=False)
    code = Column(String, nullable=True)  # "1.2.3" o "Tema 1"
    content = Column(Text, nullable=True)  # Contenido procesado (markdown)

    # Fuente y trazabilidad
    source_type = Column(Enum("normativa", "manual", "ai_generated", "pending"))
    source_reference = Column(String, nullable=True)  # Ruta al archivo o URL
    source_excerpt = Column(Text, nullable=True)  # Texto original extraído

    # Estado
    content_status = Column(Enum("empty", "partial", "complete", "verified"))
    last_processed_at = Column(DateTime, nullable=True)

    # UI state (persistido por usuario)
    is_expanded = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Syllabus(Base):
    """Temario oficial (ej: Anexo V Arquitectos Técnicos)"""
    __tablename__ = "syllabi"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String, nullable=False)  # "Arquitectos Técnicos - Anexo V"
    description = Column(Text, nullable=True)
    source_file = Column(String, nullable=True)  # Ruta al PDF original

    # Metadatos
    total_topics = Column(Integer, default=0)
    processed_topics = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relaciones
    topics = relationship("StructuredTopic", back_populates="syllabus")


class NormativeSource(Base):
    """Fuente normativa indexada"""
    __tablename__ = "normative_sources"

    id = Column(Integer, primary_key=True)

    # Identificación
    name = Column(String, nullable=False)  # "Constitución Española"
    code = Column(String, nullable=True)  # "BOE-A-1978-31229"
    source_type = Column(Enum("boe", "cte", "boa", "custom"))

    # Ubicación
    file_path = Column(String, nullable=True)  # Ruta local
    url = Column(String, nullable=True)  # URL oficial

    # Contenido indexado
    full_text = Column(Text, nullable=True)  # Texto extraído
    is_indexed = Column(Boolean, default=False)
    indexed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
```

---

## 3. Arquitectura de Agentes

### 3.1 Diagrama de Flujo
```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO                                  │
│  (Selecciona temario, solicita procesamiento)                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                 ORQUESTADOR PRINCIPAL                           │
│  - Recibe solicitud de procesar tema                            │
│  - Coordina agentes                                             │
│  - Mantiene trazabilidad                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ AGENTE        │  │ AGENTE        │  │ AGENTE        │
│ EXTRACTOR     │  │ BUSCADOR      │  │ SINTETIZADOR  │
│               │  │               │  │               │
│ - Lee PDFs    │  │ - Busca en    │  │ - Resume      │
│ - Extrae      │  │   normativa   │  │ - Estructura  │
│   estructura  │  │ - Busca en    │  │ - Genera      │
│   del temario │  │   internet    │  │   markdown    │
│               │  │   (con permiso│  │               │
└───────────────┘  └───────────────┘  └───────────────┘
```

### 3.2 Responsabilidades de Cada Agente

#### Agente Extractor (Parser)
```
Entrada: PDF del temario (Anexo V)
Salida: Estructura jerárquica de temas

Responsabilidades:
1. Extraer texto del PDF
2. Identificar estructura (partes, temas, subtemas)
3. Crear árbol de StructuredTopic
4. Identificar palabras clave para búsqueda
```

#### Agente Buscador (Searcher)
```
Entrada: Título/descripción del tema
Salida: Contenido relevante encontrado o "no encontrado"

Responsabilidades:
1. Buscar PRIMERO en /normativa local
   - Buscar en PDFs indexados (full-text search)
   - Priorizar fuentes oficiales (BOE, CTE)

2. Si no encuentra suficiente:
   - Informar al usuario
   - Solicitar permiso para buscar en Internet
   - O solicitar que el usuario aporte el material

3. NUNCA inventar contenido
```

#### Agente Sintetizador (Synthesizer)
```
Entrada: Contenido crudo de normativa
Salida: Contenido estructurado en markdown

Responsabilidades:
1. Resumir manteniendo precisión legal
2. Estructurar en secciones claras
3. Destacar artículos y referencias
4. Mantener trazabilidad (citar fuente)
```

### 3.3 Trazabilidad
Cada contenido generado incluirá:
```json
{
  "content": "...",
  "source": {
    "type": "normativa|internet|manual",
    "reference": "BOE-A-1978-31229",
    "excerpt": "Texto original...",
    "processed_at": "2026-01-16T10:30:00Z",
    "agent_version": "1.0"
  }
}
```

---

## 4. Estrategia de Preprocesado

### 4.1 Fase 1: Indexación de Normativa
```
1. Escanear /Material de Estudio/normativa/
2. Para cada PDF:
   - Extraer texto completo
   - Identificar estructura (artículos, secciones)
   - Almacenar en NormativeSource
   - Crear índice de búsqueda (full-text)
```

### 4.2 Fase 2: Parsing del Temario
```
1. Procesar Anexo_V_Arquitectos Técnicos.pdf
2. Extraer estructura jerárquica
3. Crear StructuredTopic para cada tema/subtema
4. Identificar keywords para matching
```

### 4.3 Fase 3: Matching y Generación
```
Para cada StructuredTopic sin contenido:
1. Buscar en índice de normativa
2. Si hay match:
   - Extraer contenido relevante
   - Sintetizar
   - Marcar como "complete" o "partial"
3. Si no hay match:
   - Marcar como "pending"
   - Registrar para revisión manual
```

### 4.4 Fase 4: Revisión y Validación
```
El usuario puede:
1. Revisar contenido generado
2. Editar/corregir
3. Marcar como "verified"
4. Añadir contenido manualmente
```

---

## 5. Propuesta de UI para Vista Estructurada

### 5.1 Layout Principal
```
┌─────────────────────────────────────────────────────────────────┐
│ [←] Temarios > Arquitectos Técnicos        [⚙️] [🔍] [📥Export] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📚 ANEXO V - ARQUITECTOS TÉCNICOS                             │
│  ═══════════════════════════════════                           │
│                                                                 │
│  Progreso: ████████░░░░ 45% (25/55 temas con contenido)        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 📖 PARTE I - MATERIAS COMUNES                    [▼]    │   │
│  │   │                                                     │   │
│  │   ├─ 📄 Tema 1: La Constitución Española        [✓]    │   │
│  │   │   │                                                 │   │
│  │   │   ├─ ▼ Estructura y contenido básico               │   │
│  │   │   │   ┌──────────────────────────────────────────┐ │   │
│  │   │   │   │ La Constitución Española de 1978 es la   │ │   │
│  │   │   │   │ norma suprema del ordenamiento jurídico. │ │   │
│  │   │   │   │                                          │ │   │
│  │   │   │   │ **Estructura:**                          │ │   │
│  │   │   │   │ - Preámbulo                              │ │   │
│  │   │   │   │ - Título Preliminar (arts. 1-9)         │ │   │
│  │   │   │   │ - Título I: Derechos (arts. 10-55)      │ │   │
│  │   │   │   │ ...                                      │ │   │
│  │   │   │   │                                          │ │   │
│  │   │   │   │ 📎 Fuente: BOE-A-1978-31229             │ │   │
│  │   │   │   └──────────────────────────────────────────┘ │   │
│  │   │   │                                                 │   │
│  │   │   ├─ ▶ Título Preliminar                           │   │
│  │   │   └─ ▶ Derechos y libertades                       │   │
│  │   │                                                     │   │
│  │   ├─ 📄 Tema 2: Régimen del suelo              [⚠️]    │   │
│  │   │   └─ ⚠️ Contenido pendiente de procesar            │   │
│  │   │       [🔄 Procesar ahora] [📝 Añadir manual]       │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

Leyenda: [✓] Completo  [⚠️] Pendiente  [◐] Parcial
```

### 5.2 Interacciones
- **Click en ▶/▼**: Expandir/colapsar sección
- **Click en "Procesar ahora"**: Lanza el agente de procesamiento
- **Click en "Añadir manual"**: Abre editor markdown
- **Hover en 📎**: Muestra tooltip con referencia completa
- **Drag & drop**: Reordenar temas (opcional)

### 5.3 Panel de Procesamiento (Modal/Sidebar)
```
┌─────────────────────────────────────────────┐
│ 🔄 Procesando: Tema 2 - Régimen del suelo   │
├─────────────────────────────────────────────┤
│                                             │
│ Estado: Buscando en normativa local...      │
│ ████████████░░░░░░░░ 60%                    │
│                                             │
│ ✓ Búsqueda en BOE completada                │
│ ✓ Encontrado: RDL 7/2015                    │
│ ○ Procesando: Ley 3/2009 de Aragón          │
│ ○ Pendiente: Sintetizar contenido           │
│                                             │
│ [Cancelar]                     [Ver log]    │
└─────────────────────────────────────────────┘
```

---

## 6. Enfoque Incremental de Implementación

### Sprint 1: Mejoras UI Actuales
- [ ] Panel lateral redimensionable
- [ ] Control de tamaño de fuente
- [ ] Modo lectura (sin panel)
- [ ] Persistencia de preferencias

### Sprint 2: Modelo de Datos
- [ ] Crear modelos: Syllabus, StructuredTopic, NormativeSource
- [ ] Migraciones de BD
- [ ] API CRUD básica

### Sprint 3: Indexación de Normativa
- [ ] Extracción de texto de PDFs
- [ ] Almacenamiento en NormativeSource
- [ ] Búsqueda full-text básica

### Sprint 4: Parser de Temario
- [ ] Extracción de estructura del Anexo V
- [ ] Creación automática de StructuredTopic
- [ ] UI de visualización de árbol

### Sprint 5: Agentes de Procesamiento
- [ ] Agente Buscador (búsqueda en normativa)
- [ ] Agente Sintetizador
- [ ] UI de procesamiento con feedback

### Sprint 6: Integración y Pulido
- [ ] Exportación a HTML/PDF del árbol
- [ ] Búsqueda global
- [ ] Estadísticas de progreso

---

## 7. Tecnologías Sugeridas

### Backend
- **FastAPI** (actual) - Mantener
- **SQLAlchemy** (actual) - Mantener
- **PyMuPDF** o **pdfplumber** - Extracción de PDFs
- **Whoosh** o **SQLite FTS5** - Búsqueda full-text
- **LangChain** (opcional) - Orquestación de agentes IA

### Frontend
- **Next.js** (actual) - Mantener
- **react-resizable-panels** - Paneles redimensionables
- **react-arborist** o custom - Árbol colapsable
- **react-markdown** (actual) - Renderizado markdown

---

## 8. Consideraciones Adicionales

### Seguridad
- Los agentes NUNCA deben ejecutar código externo
- Validar todas las entradas de usuario
- Limitar tamaño de archivos procesados

### Rendimiento
- Indexación de normativa como job en background
- Caché de contenido procesado
- Paginación para temarios grandes

### UX
- Feedback claro durante procesamiento
- Posibilidad de cancelar operaciones largas
- Guardar estado de expansión por usuario
