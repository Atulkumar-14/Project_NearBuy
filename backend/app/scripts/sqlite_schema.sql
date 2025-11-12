-- NearBuy normalized SQLite schema
PRAGMA foreign_keys = ON;

-- Products
CREATE TABLE IF NOT EXISTS Products (
  product_id TEXT PRIMARY KEY,
  product_name VARCHAR(200) NOT NULL,
  category_id TEXT,
  brand VARCHAR(100),
  description VARCHAR(1000),
  color VARCHAR(50),
  price NUMERIC(10,2),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_products_category ON Products(category_id);

-- Shops
CREATE TABLE IF NOT EXISTS Shops (
  shop_id TEXT PRIMARY KEY,
  shop_name VARCHAR(200) NOT NULL,
  owner_id TEXT,
  shop_image VARCHAR(500),
  address VARCHAR(500),
  city VARCHAR(100),
  contact_number VARCHAR(15),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME
);
CREATE INDEX IF NOT EXISTS ix_shops_city ON Shops(city);
CREATE INDEX IF NOT EXISTS ix_shops_owner ON Shops(owner_id);

-- Product_Shop junction (using existing Shop_Product table name)
CREATE TABLE IF NOT EXISTS Shop_Product (
  shop_product_id TEXT PRIMARY KEY,
  shop_id TEXT NOT NULL,
  product_id TEXT NOT NULL,
  price NUMERIC(10,2),
  stock INTEGER,
  stock_quantity INTEGER,
  last_restocked DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME,
  FOREIGN KEY(shop_id) REFERENCES Shops(shop_id) ON DELETE CASCADE,
  FOREIGN KEY(product_id) REFERENCES Products(product_id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_shop_product_unique ON Shop_Product(shop_id, product_id);
CREATE INDEX IF NOT EXISTS ix_shop_product_shop ON Shop_Product(shop_id);
CREATE INDEX IF NOT EXISTS ix_shop_product_product ON Shop_Product(product_id);

-- Optional: Check constraints for city (emulated via trigger if needed)
-- SQLite lacks enum; application enforces allowed values: Bhopal, Indore, Jabalpur