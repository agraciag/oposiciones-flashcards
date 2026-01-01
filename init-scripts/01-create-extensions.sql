-- Extensiones útiles para PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUIDs
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Búsqueda de texto fuzzy
CREATE EXTENSION IF NOT EXISTS "unaccent";       -- Eliminar acentos para búsquedas

-- Función para timestamps automáticos
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
