BEGIN TRANSACTION;
ALTER TABLE Product_Categories ADD COLUMN category_key TEXT;
UPDATE Product_Categories SET category_key = CAST(category_id AS TEXT) WHERE category_id IS NOT NULL AND category_key IS NULL;
CREATE INDEX IF NOT EXISTS ix_product_categories_category_key ON Product_Categories(category_key);

ALTER TABLE Products ADD COLUMN category_key TEXT;
UPDATE Products SET category_key = CAST(category_id AS TEXT) WHERE category_id IS NOT NULL AND category_key IS NULL;
CREATE INDEX IF NOT EXISTS ix_products_category_key ON Products(category_key);
COMMIT;
