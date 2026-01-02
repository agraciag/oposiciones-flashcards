from database import engine
from sqlalchemy import text

def update_schema():
    print("🔄 Updating schema...")
    with engine.connect() as conn:
        try:
            # Add is_public column
            conn.execute(text("ALTER TABLE decks ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE"))
            
            # Add original_deck_id column
            conn.execute(text("ALTER TABLE decks ADD COLUMN IF NOT EXISTS original_deck_id INTEGER REFERENCES decks(id)"))
            
            conn.commit()
            print("✅ Schema updated successfully")
        except Exception as e:
            print(f"❌ Error updating schema: {e}")
            conn.rollback()

if __name__ == "__main__":
    update_schema()
