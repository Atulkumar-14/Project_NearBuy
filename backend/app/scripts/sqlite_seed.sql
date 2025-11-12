-- Seed data: 50 products, 15 shops, 200+ product-shop entries
PRAGMA foreign_keys = ON;

-- Products
WITH RECURSIVE seq(n) AS (
  SELECT 1 UNION ALL SELECT n+1 FROM seq WHERE n < 50
)
INSERT INTO Products(product_id, product_name, brand, description, color, price, created_at)
SELECT lower(hex(randomblob(16))),
       'Sample Product ' || n,
       'Brand' || (n % 10),
       'Description for product ' || n,
       CASE (n % 5) WHEN 0 THEN 'Red' WHEN 1 THEN 'Blue' WHEN 2 THEN 'Green' WHEN 3 THEN 'Black' ELSE 'White' END,
       ROUND((n * 3.5) % 999, 2),
       CURRENT_TIMESTAMP
FROM seq;

-- Shops in Bhopal, Indore, Jabalpur
WITH RECURSIVE s(n) AS (
  SELECT 1 UNION ALL SELECT n+1 FROM s WHERE n < 15
)
INSERT INTO Shops(shop_id, shop_name, address, city, contact_number, created_at)
SELECT lower(hex(randomblob(16))),
       'Shop #' || n,
       'Address line ' || n,
       CASE (n % 3) WHEN 0 THEN 'Bhopal' WHEN 1 THEN 'Indore' ELSE 'Jabalpur' END,
       '9000000' || printf('%03d', n),
       CURRENT_TIMESTAMP
FROM s;

-- Product-Shop associations: ~225 rows
INSERT INTO Shop_Product(shop_product_id, shop_id, product_id, price, stock, stock_quantity, last_restocked, created_at)
SELECT lower(hex(randomblob(16))),
       (SELECT shop_id FROM Shops ORDER BY shop_id LIMIT 1 OFFSET (abs(random()) % (SELECT COUNT(*) FROM Shops))),
       (SELECT product_id FROM Products ORDER BY product_id LIMIT 1 OFFSET (abs(random()) % (SELECT COUNT(*) FROM Products))),
       ROUND((abs(random()) % 1000) + 10, 2),
       abs(random()) % 100,
       abs(random()) % 100,
       CURRENT_TIMESTAMP,
       CURRENT_TIMESTAMP
FROM (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5),
     (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5),
     (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3);