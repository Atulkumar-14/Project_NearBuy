import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nearbuy.db')

def main():
    print('Using DB:', DB_PATH)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    # Add column
    try:
        cur.execute('ALTER TABLE "Shops" ADD COLUMN gstin VARCHAR(15)')
        print('Added column: gstin')
    except Exception as e:
        print('Column add skipped:', e)
    # Create unique index (partial)
    try:
        cur.execute('CREATE UNIQUE INDEX shops_gstin_uq ON "Shops"(gstin) WHERE gstin IS NOT NULL')
        print('Created unique index: shops_gstin_uq')
    except Exception as e:
        print('Index create skipped:', e)
    con.commit()
    con.close()
    print('Migration completed')

if __name__ == '__main__':
    main()