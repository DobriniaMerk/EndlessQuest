DROP TABLE IF EXISTS paragraphs;

CREATE TABLE paragraphs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    protected BOOLEAN CHECK (protected IN (TRUE, FALSE)) DEFAULT FALSE,
    title_ru TEXT,
    story_ru TEXT,
    title_en TEXT,
    story_en TEXT
);
