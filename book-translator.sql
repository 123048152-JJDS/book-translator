-- ============================================================
--  Book Translator — Schema PostgreSQL
--  Ejecutar en psql o pgAdmin contra la base book_translator
-- ============================================================

-- Crear la base de datos (ejecutar como superusuario si no existe)
-- CREATE DATABASE book_translator;
-- \c book_translator

-- ── Tabla: books ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS books (
    id               SERIAL PRIMARY KEY,
    title            VARCHAR(200)  NOT NULL,
    author           VARCHAR(200),
    slug             VARCHAR(60)   NOT NULL,
    description      TEXT,
    source_language  VARCHAR(50)   DEFAULT 'English',
    target_language  VARCHAR(50)   DEFAULT 'Spanish',
    created_at       TIMESTAMP     DEFAULT NOW(),
    updated_at       TIMESTAMP     DEFAULT NOW()
);

-- ── Tabla: pages ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pages (
    id               SERIAL PRIMARY KEY,
    book_id          INTEGER       NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    page_number      INTEGER       NOT NULL,
    image_filename   VARCHAR(300)  NOT NULL,
    original_text    TEXT,
    translation      TEXT,
    notes            TEXT,
    status           VARCHAR(20)   DEFAULT 'pending'
                                   CHECK (status IN ('pending', 'in_progress', 'done')),
    created_at       TIMESTAMP     DEFAULT NOW(),
    updated_at       TIMESTAMP     DEFAULT NOW(),

    CONSTRAINT uq_book_page UNIQUE (book_id, page_number)
);

-- ── Índices ──────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_pages_book_id
    ON pages(book_id);

CREATE INDEX IF NOT EXISTS idx_pages_status
    ON pages(status);

CREATE INDEX IF NOT EXISTS idx_books_slug
    ON books(slug);

-- ── Trigger: updated_at automático ──────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_books_updated_at
    BEFORE UPDATE ON books
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER trg_pages_updated_at
    BEFORE UPDATE ON pages
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ── Datos de ejemplo (opcional) ──────────────────────────────
-- INSERT INTO books (title, author, slug, source_language, target_language)
-- VALUES ('English Grammar in Use', 'Raymond Murphy', 'english_grammar_in_use', 'English', 'Spanish');
