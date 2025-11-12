-- SQLite DDL converted from your MSSQL schema in db.txt
-- Notes:
-- - NVARCHAR → TEXT
-- - INT IDENTITY → INTEGER PRIMARY KEY AUTOINCREMENT
-- - DECIMAL(p,s) → NUMERIC(p,s)
-- - DATETIME → DATETIME (stored as text/ISO8601 by convention)
-- - TIME → TEXT ('HH:MM:SS')
-- - CHECK/UNIQUE/FOREIGN KEY constraints preserved where supported
PRAGMA foreign_keys = ON;

-- admin
CREATE TABLE IF NOT EXISTS admin (
  userId TEXT PRIMARY KEY,
  password TEXT NOT NULL,
  created_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
);

-- Log
CREATE TABLE IF NOT EXISTS Log (
  log_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  action_type TEXT,
  description TEXT,
  timestamp DATETIME DEFAULT (CURRENT_TIMESTAMP),
  ip_address TEXT,
  status_code INTEGER DEFAULT 200,
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Product_Categories
CREATE TABLE IF NOT EXISTS Product_Categories (
  category_id INTEGER PRIMARY KEY AUTOINCREMENT,
  category_name TEXT UNIQUE,
  category_description TEXT,
  created_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
);

-- Products
CREATE TABLE IF NOT EXISTS Products (
  product_id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_name TEXT,
  category_id INTEGER,
  brand TEXT,
  description TEXT,
  color TEXT,
  created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
  FOREIGN KEY (category_id) REFERENCES Product_Categories(category_id) ON DELETE CASCADE
);

-- Product_Images
CREATE TABLE IF NOT EXISTS Product_Images (
  image_id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER,
  image_url TEXT,
  FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE
);

-- Product_Reviews
CREATE TABLE IF NOT EXISTS Product_Reviews (
  review_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  product_id INTEGER,
  rating NUMERIC(2,1),
  review_text TEXT,
  created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
  FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  CHECK (rating >= 1.0 AND rating <= 5.0)
);

-- Search_History
CREATE TABLE IF NOT EXISTS Search_History (
  history_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  search_item TEXT,
  timestamp DATETIME DEFAULT (CURRENT_TIMESTAMP),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Shops
CREATE TABLE IF NOT EXISTS Shops (
  shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
  shop_name TEXT,
  owner_id INTEGER,
  shop_image TEXT,
  created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
  FOREIGN KEY (owner_id) REFERENCES Shop_Owners(owner_id) ON DELETE CASCADE
);

-- Shop_Address
CREATE TABLE IF NOT EXISTS Shop_Address (
  address_id INTEGER PRIMARY KEY AUTOINCREMENT,
  shop_id INTEGER,
  city TEXT,
  country TEXT,
  pincode TEXT,
  landmark TEXT,
  area TEXT,
  latitude NUMERIC(10,6),
  longitude NUMERIC(10,6),
  FOREIGN KEY (shop_id) REFERENCES Shops(shop_id) ON DELETE CASCADE
);

-- Shop_Owners
CREATE TABLE IF NOT EXISTS Shop_Owners (
  owner_id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_name TEXT,
  phone TEXT UNIQUE,
  email TEXT UNIQUE
);

-- Shop_Product
CREATE TABLE IF NOT EXISTS Shop_Product (
  shop_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
  shop_id INTEGER,
  product_id INTEGER,
  price NUMERIC(10,2),
  stock INTEGER,
  FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE,
  FOREIGN KEY (shop_id) REFERENCES Shops(shop_id) ON DELETE CASCADE
);

-- Shop_Timings
CREATE TABLE IF NOT EXISTS Shop_Timings (
  timing_id INTEGER PRIMARY KEY AUTOINCREMENT,
  shop_id INTEGER,
  day TEXT,
  open_time TEXT,   -- store as 'HH:MM:SS'
  close_time TEXT,  -- store as 'HH:MM:SS'
  FOREIGN KEY (shop_id) REFERENCES Shops(shop_id) ON DELETE CASCADE
);

-- Users
CREATE TABLE IF NOT EXISTS Users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  email TEXT UNIQUE,
  password TEXT,
  phone TEXT UNIQUE,
  created_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
);

-- Helpful indexes mirroring intent of MSSQL script
CREATE INDEX IF NOT EXISTS ix_products_category ON Products(category_id);
CREATE INDEX IF NOT EXISTS ix_shop_address_city ON Shop_Address(city);
CREATE INDEX IF NOT EXISTS ix_shop_address_pincode ON Shop_Address(pincode);
CREATE INDEX IF NOT EXISTS ix_shop_product_shop ON Shop_Product(shop_id);
CREATE INDEX IF NOT EXISTS ix_shop_product_product ON Shop_Product(product_id);