# Sistema de Apuntes - Documentación

## 📖 Índice

1. [Descripción General](#descripción-general)
2. [Arquitectura](#arquitectura)
3. [Modelos de Datos](#modelos-de-datos)
4. [API Backend](#api-backend)
5. [Frontend](#frontend)
6. [Guía de Uso](#guía-de-uso)
7. [Casos de Uso](#casos-de-uso)
8. [Migración y Seed](#migración-y-seed)

---

## Descripción General

El sistema de apuntes permite organizar contenido de estudio en estructuras jerárquicas reutilizables. El contenido puede aparecer en múltiples colecciones sin duplicación, ideal para oposiciones donde el mismo material (ej: un artículo de la Constitución) aparece tanto en el temario como en la normativa completa.

### Características Principales

- ✅ **Contenido Reutilizable**: Una nota puede aparecer en múltiples colecciones
- ✅ **Estructura Jerárquica**: Árbol anidado con secciones y contenido
- ✅ **Tipos de Colecciones**: Temario, Normativa, Personalizado
- ✅ **Notas Destacadas**: Marcar contenido importante con `is_featured`
- ✅ **Referencias desde Flashcards**: Vincular tarjetas con apuntes
- ✅ **Metadatos Legislativos**: Artículos, referencias BOE
- ✅ **Markdown**: Soporte básico para formato
- ✅ **Público/Privado**: Compartir colecciones

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     SISTEMA DE APUNTES                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────┐      ┌─────────────────┐      ┌──────────┐  │
│  │   Note    │◄─────┤ NoteHierarchy   ├─────►│ Collection│ │
│  │           │      │                 │      │           │  │
│  │ - title   │      │ - parent_id     │      │ - name    │  │
│  │ - content │      │ - order_index   │      │ - type    │  │
│  │ - type    │      │ - is_featured   │      │ - public  │  │
│  └─────┬─────┘      └─────────────────┘      └──────────┘  │
│        │                                                     │
│        │ (1:N)                                               │
│        │                                                     │
│  ┌─────▼─────┐                                              │
│  │ Flashcard │                                              │
│  │           │                                              │
│  │ - note_id │  (Referencia opcional)                       │
│  └───────────┘                                              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Datos

1. **Crear Nota**: El usuario crea una nota con contenido
2. **Crear Colección**: El usuario crea una colección (Temario/Normativa/Custom)
3. **Añadir a Colección**: Se crea una jerarquía que conecta la nota con la colección
4. **Reutilizar**: La misma nota puede añadirse a múltiples colecciones con diferentes jerarquías
5. **Referenciar desde Flashcard**: Opcionalmente se vincula una flashcard con una nota

---

## Modelos de Datos

### Note

Contenido individual reutilizable.

```python
class Note:
    id: int
    user_id: int
    title: str                    # "Art. 15 - Derecho a la vida"
    content: str | None           # Markdown o texto plano
    note_type: NoteType           # SECTION | CONTENT
    tags: str | None              # "importante,examen,básico"
    legal_reference: str | None   # "BOE-A-1978-31229"
    article_number: str | None    # "Art. 15 CE"
    created_at: datetime
    updated_at: datetime
```

**Tipos de Nota**:
- `SECTION`: Encabezado/sección sin contenido propio (ej: "Título I")
- `CONTENT`: Contenido real con texto (ej: "Artículo 15")

### NoteCollection

Colección/vista que agrupa notas.

```python
class NoteCollection:
    id: int
    user_id: int
    name: str                     # "Tema 1 - Constitución"
    description: str | None
    collection_type: CollectionType  # TEMARIO | NORMATIVA | CUSTOM
    is_public: bool
    created_at: datetime
    updated_at: datetime
```

**Tipos de Colección**:
- `TEMARIO`: Temario de oposición
- `NORMATIVA`: Normativa/legislación completa
- `CUSTOM`: Colección personalizada

### NoteHierarchy

Estructura de árbol que conecta notas con colecciones.

```python
class NoteHierarchy:
    id: int
    collection_id: int            # A qué colección pertenece
    note_id: int                  # Qué nota mostrar
    parent_id: int | None         # Padre en el árbol (self-ref)
    order_index: int              # Orden entre hermanos
    is_featured: bool             # Destacar (⭐)
    created_at: datetime
```

### Flashcard (actualizado)

```python
class Flashcard:
    # ... campos existentes ...
    note_id: int | None           # 🆕 Referencia a nota (opcional)
```

---

## API Backend

Base URL: `http://localhost:7999/api/notes`

### Notas

#### `POST /notes`
Crear nueva nota.

**Request**:
```json
{
  "title": "Art. 15 - Derecho a la vida",
  "content": "# Artículo 15\n\nTodos tienen derecho...",
  "note_type": "content",
  "tags": "importante,examen",
  "legal_reference": "BOE-A-1978-31229",
  "article_number": "Art. 15 CE"
}
```

**Response**: `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Art. 15 - Derecho a la vida",
  "content": "# Artículo 15...",
  "note_type": "content",
  "tags": "importante,examen",
  "legal_reference": "BOE-A-1978-31229",
  "article_number": "Art. 15 CE",
  "created_at": "2026-01-14T10:00:00Z",
  "updated_at": null
}
```

#### `GET /notes`
Listar mis notas con filtros opcionales.

**Query Params**:
- `skip`: Offset (default: 0)
- `limit`: Límite (default: 100)
- `tags`: Filtrar por tags (ej: "importante")

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "title": "Art. 15 - Derecho a la vida",
    ...
  }
]
```

#### `GET /notes/{note_id}`
Obtener nota por ID.

#### `PUT /notes/{note_id}`
Actualizar nota.

#### `DELETE /notes/{note_id}`
Eliminar nota.

### Colecciones

#### `POST /collections`
Crear nueva colección.

**Request**:
```json
{
  "name": "Tema 1 - Constitución",
  "description": "Temario completo del primer tema",
  "collection_type": "temario",
  "is_public": false
}
```

#### `GET /collections`
Listar mis colecciones.

**Query Params**:
- `collection_type`: Filtrar por tipo (temario/normativa/custom)

#### `GET /collections/public`
Listar colecciones públicas (excluyendo las mías).

#### `GET /collections/{collection_id}`
Obtener colección por ID.

#### `PUT /collections/{collection_id}`
Actualizar colección.

#### `DELETE /collections/{collection_id}`
Eliminar colección.

#### `GET /collections/{collection_id}/tree` ⭐
Obtener árbol completo de notas de la colección.

**Response**: `200 OK`
```json
[
  {
    "hierarchy_id": 1,
    "note_id": 1,
    "title": "1. La Constitución",
    "note_type": "section",
    "is_featured": false,
    "order_index": 0,
    "children": [
      {
        "hierarchy_id": 2,
        "note_id": 2,
        "title": "1.1 Antecedentes",
        "note_type": "content",
        "is_featured": true,
        "order_index": 0,
        "children": []
      }
    ]
  }
]
```

### Jerarquías

#### `POST /hierarchies`
Añadir nota a colección (crear jerarquía).

**Request**:
```json
{
  "collection_id": 1,
  "note_id": 5,
  "parent_id": null,
  "order_index": 0,
  "is_featured": true
}
```

#### `GET /hierarchies/{hierarchy_id}`
Obtener jerarquía por ID.

#### `PUT /hierarchies/{hierarchy_id}`
Actualizar jerarquía (mover nodo, cambiar orden).

#### `DELETE /hierarchies/{hierarchy_id}`
Eliminar jerarquía (quitar nota de colección).

---

## Frontend

### Rutas

- `/notes` - Lista de colecciones con filtros
- `/notes/new` - Crear nueva colección
- `/notes/[collectionId]` - Vista de colección con árbol y editor

### Componentes

#### `<NotesTree>`
Árbol colapsable/desplegable de notas.

**Props**:
```typescript
interface NotesTreeProps {
  tree: NoteTreeNode[];           // Árbol de notas
  onSelectNote: (noteId: number) => void;
  selectedNoteId: number | null;
  className?: string;
}
```

**Características**:
- Expandir/colapsar secciones
- Iconos diferenciados (sección vs contenido)
- Destacados con estrella ⭐
- Selección visual

#### `<NoteViewer>`
Visualizador de notas con renderizado markdown.

**Props**:
```typescript
interface NoteViewerProps {
  note: Note | null;
  onEdit?: (note: Note) => void;
  onDelete?: (noteId: number) => void;
  className?: string;
}
```

**Características**:
- Renderizado markdown básico (headers, bold, listas)
- Mostrar metadatos (artículo, BOE)
- Mostrar etiquetas
- Acciones: editar, eliminar

#### `<NoteEditor>`
Editor de notas con vista previa.

**Props**:
```typescript
interface NoteEditorProps {
  initialData?: Partial<NoteFormData>;
  onSave: (data: NoteFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
  className?: string;
}
```

**Características**:
- Formulario completo
- Toggle vista previa
- Validación
- Soporte markdown

---

## Guía de Uso

### 1. Crear una Colección

1. Ir a `/notes`
2. Clic en "Nueva Colección"
3. Rellenar formulario:
   - Nombre: "Tema 1 - Constitución"
   - Descripción: Opcional
   - Tipo: Temario/Normativa/Personalizado
   - Público: ✓ (opcional)
4. Guardar

### 2. Añadir Notas a la Colección

1. Entrar en la colección (`/notes/{id}`)
2. Clic en "Nueva Nota"
3. Rellenar formulario:
   - Título: "Art. 15 - Derecho a la vida"
   - Tipo: Contenido (o Sección)
   - Contenido: Markdown
   - Artículo: "Art. 15 CE"
   - BOE: "BOE-A-1978-31229"
   - Etiquetas: "importante,examen"
4. Guardar

### 3. Organizar el Árbol

Las notas se organizan automáticamente en el árbol. Puedes:
- Ver el árbol en el panel lateral
- Expandir/colapsar secciones
- Seleccionar notas para verlas

### 4. Reutilizar Contenido

Para añadir una nota existente a otra colección:

**Via API**:
```bash
curl -X POST http://localhost:7999/api/notes/hierarchies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_id": 2,
    "note_id": 5,
    "parent_id": null,
    "order_index": 0,
    "is_featured": true
  }'
```

### 5. Vincular Flashcard con Nota

Al crear/editar una flashcard:
```json
{
  "deck_id": 1,
  "front": "¿Qué dice el Art. 15?",
  "back": "Derecho a la vida...",
  "note_id": 5
}
```

---

## Casos de Uso

### Caso 1: Temario de Oposición

**Objetivo**: Organizar el temario por temas con contenido destacado.

**Estructura**:
```
Colección: "Tema 1 - Constitución" (tipo: temario)
├─ 1. La Constitución (sección)
│  ├─ 1.1 Antecedentes ⭐ (contenido)
│  └─ 1.2 Estructura (contenido)
├─ 2. Derechos Fundamentales (sección)
│  ├─ 2.1 Art. 15 ⭐ (contenido)
│  └─ 2.2 Art. 14 (contenido)
```

### Caso 2: Normativa Completa

**Objetivo**: Almacenar la Constitución completa para consulta.

**Estructura**:
```
Colección: "Constitución Española - Texto Completo" (tipo: normativa)
├─ Título Preliminar (sección)
│  ├─ Art. 1 ⭐ (contenido)
│  ├─ Art. 2 (contenido)
│  └─ Art. 3 (contenido)
├─ Título I - Derechos (sección)
│  ├─ Art. 14 ⭐ (contenido)
│  └─ Art. 15 ⭐ (contenido)
```

### Caso 3: Contenido Compartido

**Objetivo**: Reutilizar el Art. 15 en temario y normativa.

1. Crear nota "Art. 15" una sola vez
2. Añadirla al Temario Tema 1:
   ```
   POST /hierarchies { collection_id: 1, note_id: 5, is_featured: true }
   ```
3. Añadirla a la Constitución Completa:
   ```
   POST /hierarchies { collection_id: 2, note_id: 5, is_featured: true }
   ```

**Resultado**: Una sola nota, dos ubicaciones, sin duplicación.

### Caso 4: Flashcards con Contexto

**Objetivo**: Vincular flashcard con su nota de referencia.

1. Crear flashcard sobre Art. 15
2. Añadir `note_id: 5` al crearla
3. En el frontend, mostrar enlace 📝 a la nota
4. Usuario puede ir de la flashcard a la nota para más contexto

---

## Migración y Seed

### Migrar Base de Datos

```bash
cd backend
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

Esto creará las tablas:
- `notes`
- `note_collections`
- `note_hierarchies`

Y actualizará:
- `flashcards` (añade columna `note_id`)

### Cargar Datos de Ejemplo

```bash
cd backend
python seed_notes.py
```

Esto creará:
- 2 colecciones (Temario y Normativa)
- 7 notas de ejemplo
- Demuestra reutilización de contenido

**Requisito**: Debe existir el usuario `demo@example.com`. Si no existe, ejecuta primero:
```bash
python seed_data.py
```

---

## Markdown Soportado

El sistema soporta markdown básico en el contenido de las notas:

```markdown
# Título 1
## Título 2
### Título 3

**Texto en negrita**

- Lista
- De
- Items

Párrafo normal.
```

Para renderizado completo (imágenes, enlaces, tablas), se recomienda integrar `react-markdown` en el futuro.

---

## Permisos y Acceso

### Notas y Colecciones
- Solo el propietario puede editar/eliminar
- Colecciones públicas son visibles para todos (solo lectura)

### Control de Acceso
```
┌─────────────────────────────────────────────────┐
│ Acción              │ Propietario │ Otros       │
├─────────────────────────────────────────────────┤
│ Ver privada         │     ✓       │     ✗       │
│ Ver pública         │     ✓       │     ✓       │
│ Editar              │     ✓       │     ✗       │
│ Eliminar            │     ✓       │     ✗       │
│ Clonar (futuro)     │     ✓       │     ✓       │
└─────────────────────────────────────────────────┘
```

---

## Mejoras Futuras

1. **Renderizado Markdown Completo**
   - Integrar `react-markdown`
   - Soporte para imágenes, enlaces, tablas

2. **Búsqueda Avanzada**
   - Búsqueda full-text en contenido
   - Filtros por etiquetas múltiples
   - Búsqueda por metadatos legislativos

3. **Drag & Drop**
   - Reorganizar árbol arrastrando nodos
   - Mover notas entre colecciones

4. **Exportación**
   - Exportar colecciones a PDF
   - Exportar a Markdown
   - Imprimir vista de estudio

5. **Importación**
   - Importar desde PDF (con OCR)
   - Importar desde Markdown
   - Importar desde HTML (BOE)

6. **Colaboración**
   - Clonar colecciones públicas
   - Contribuir mejoras
   - Sistema de versiones

7. **Editor Rico**
   - Integrar TinyMCE o Quill
   - WYSIWYG para formato visual
   - Insertar imágenes

8. **Generación IA**
   - Generar resúmenes automáticos
   - Sugerir flashcards desde notas
   - Análisis de contenido

---

## Solución de Problemas

### Error: "Colección no encontrada"
- Verificar que la colección existe
- Verificar permisos (solo propietario o pública)
- Revisar token de autenticación

### Error: "Nota no encontrada"
- Verificar que la nota existe
- Verificar que pertenece al usuario actual

### Árbol no se muestra correctamente
- Verificar que las jerarquías tienen `order_index` correcto
- Revisar relaciones parent-child
- Comprobar que `parent_id` apunta a jerarquías válidas

### Contenido markdown no se renderiza
- Verificar que el contenido tiene formato markdown válido
- Recordar que solo se soporta markdown básico
- Considerar integrar `react-markdown` para más funcionalidades

---

## Contacto y Soporte

Para preguntas, sugerencias o reportar bugs:
- Crear issue en el repositorio
- Documentación: `/docs/NOTES_SYSTEM.md`
- API Docs: `http://localhost:7999/docs` (FastAPI Swagger)

---

**Versión**: 1.0.0
**Fecha**: Enero 2026
**Autor**: OpositApp Team
