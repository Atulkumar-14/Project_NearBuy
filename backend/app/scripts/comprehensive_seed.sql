PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

INSERT OR IGNORE INTO Product_Categories (category_id, category_name, category_description, created_at) VALUES
(randomblob(16),'Mobiles','Smartphones and accessories',CURRENT_TIMESTAMP),
(randomblob(16),'Laptops','Personal and business laptops',CURRENT_TIMESTAMP),
(randomblob(16),'Electronics','Consumer electronics',CURRENT_TIMESTAMP),
(randomblob(16),'Groceries','Daily essentials and packaged foods',CURRENT_TIMESTAMP),
(randomblob(16),'Home & Kitchen','Cookware, appliances, home goods',CURRENT_TIMESTAMP),
(randomblob(16),'Fashion','Clothing and apparel',CURRENT_TIMESTAMP),
(randomblob(16),'Footwear','Shoes and sandals',CURRENT_TIMESTAMP),
(randomblob(16),'Health & Personal Care','Healthcare and grooming',CURRENT_TIMESTAMP),
(randomblob(16),'Sports','Sporting goods and fitness',CURRENT_TIMESTAMP),
(randomblob(16),'Toys','Toys and games',CURRENT_TIMESTAMP),
(randomblob(16),'Automotive','Car accessories',CURRENT_TIMESTAMP),
(randomblob(16),'Books','Books and stationery',CURRENT_TIMESTAMP),
(randomblob(16),'Computer Accessories','Peripherals and accessories',CURRENT_TIMESTAMP),
(randomblob(16),'Gaming','Consoles and accessories',CURRENT_TIMESTAMP),
(randomblob(16),'Beauty','Cosmetics and skincare',CURRENT_TIMESTAMP),
(randomblob(16),'Watches','Wrist watches',CURRENT_TIMESTAMP),
(randomblob(16),'Bags','Bags and luggage',CURRENT_TIMESTAMP),
(randomblob(16),'Jewellery','Jewellery and ornaments',CURRENT_TIMESTAMP),
(randomblob(16),'Baby Care','Baby products',CURRENT_TIMESTAMP),
(randomblob(16),'Pet Supplies','Pet food and care',CURRENT_TIMESTAMP);

INSERT OR IGNORE INTO Users (user_id,name,email,password,phone,created_at) VALUES
(randomblob(16),'Aarav Sharma','aarav.sharma@nearbuy.local','$2b$12$seedAarav123','7000000101',CURRENT_TIMESTAMP),
 (randomblob(16),'Neha Verma','neha.verma@nearbuy.local','$2b$12$seedNeha123','7000000102',CURRENT_TIMESTAMP),
 (randomblob(16),'Rohit Gupta','rohit.gupta@nearbuy.local','$2b$12$seedRohit123','7000000103',CURRENT_TIMESTAMP),
 (randomblob(16),'Ananya Singh','ananya.singh@nearbuy.local','$2b$12$seedAnanya123','7000000104',CURRENT_TIMESTAMP),
 (randomblob(16),'Vivek Patel','vivek.patel@nearbuy.local','$2b$12$seedVivek123','7000000105',CURRENT_TIMESTAMP),
 (randomblob(16),'Priya Jain','priya.jain@nearbuy.local','$2b$12$seedPriya123','7000000106',CURRENT_TIMESTAMP),
 (randomblob(16),'Aditya Roy','aditya.roy@nearbuy.local','$2b$12$seedAditya123','7000000107',CURRENT_TIMESTAMP),
 (randomblob(16),'Sanya Tripathi','sanya.tripathi@nearbuy.local','$2b$12$seedSanya123','7000000108',CURRENT_TIMESTAMP),
 (randomblob(16),'Tanvi Tiwari','tanvi.tiwari@nearbuy.local','$2b$12$seedTanvi123','7000000109',CURRENT_TIMESTAMP),
 (randomblob(16),'Aman Kumar','aman.kumar@nearbuy.local','$2b$12$seedAman123','7000000110',CURRENT_TIMESTAMP),
 (randomblob(16),'Harsh Vardhan','harsh.vardhan@nearbuy.local','$2b$12$seedHarsh123','7000000111',CURRENT_TIMESTAMP),
 (randomblob(16),'Ishita Roy','ishita.roy@nearbuy.local','$2b$12$seedIshita123','7000000112',CURRENT_TIMESTAMP),
 (randomblob(16),'Deepak Yadav','deepak.yadav@nearbuy.local','$2b$12$seedDeepak123','7000000113',CURRENT_TIMESTAMP),
 (randomblob(16),'Kunal Mehta','kunal.mehta@nearbuy.local','$2b$12$seedKunal123','7000000114',CURRENT_TIMESTAMP),
 (randomblob(16),'Shruti Nair','shruti.nair@nearbuy.local','$2b$12$seedShruti123','7000000115',CURRENT_TIMESTAMP),
 (randomblob(16),'Riya Kapoor','riya.kapoor@nearbuy.local','$2b$12$seedRiya123','7000000116',CURRENT_TIMESTAMP),
 (randomblob(16),'Aakash Singh','aakash.singh@nearbuy.local','$2b$12$seedAakash123','7000000117',CURRENT_TIMESTAMP),
 (randomblob(16),'Meghna Das','meghna.das@nearbuy.local','$2b$12$seedMeghna123','7000000118',CURRENT_TIMESTAMP),
 (randomblob(16),'Nikhil Jain','nikhil.jain@nearbuy.local','$2b$12$seedNikhil123','7000000119',CURRENT_TIMESTAMP),
 (randomblob(16),'Pooja Sinha','pooja.sinha@nearbuy.local','$2b$12$seedPooja123','7000000120',CURRENT_TIMESTAMP);

INSERT OR IGNORE INTO Shop_Owners (owner_id, owner_name,phone,email, created_at) VALUES
(randomblob(16),'Rohit Sharma','9000001001','rohit.bhopal@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Neha Verma','9000001002','neha.patna@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Aman Gupta','9000001003','aman.varanasi@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Priya Mehra','9000001004','priya.jaipur@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Vikram Singh','9000001005','vikram.bhopal@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Anita Yadav','9000001006','anita.patna@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Saurabh Jha','9000001007','saurabh.varanasi@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Kavita Sharma','9000001008','kavita.jaipur@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Rahul Mishra','9000001009','rahul.bhopal@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Sneha Kumari','9000001010','sneha.patna@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Ashish Tiwari','9000001011','ashish.varanasi@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Pankaj Jain','9000001012','pankaj.jaipur@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Simran Kaur','9000001013','simran.bhopal@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Arun Kumar','9000001014','arun.patna@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Shreya Gupta','9000001015','shreya.varanasi@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Karan Malhotra','9000001016','karan.jaipur@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Divya Rai','9000001017','divya.bhopal@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Manish Sinha','9000001018','manish.patna@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Alok Pandey','9000001019','alok.varanasi@nearbuy.local',CURRENT_TIMESTAMP),
 (randomblob(16),'Ritika Choudhary','9000001020','ritika.jaipur@nearbuy.local',CURRENT_TIMESTAMP);

INSERT OR IGNORE INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'DB Mall Electronics', owner_id, 'https://images.unsplash.com/photo-1515165562835-c3b8b4e0b1bb?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='rohit.bhopal@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'New Market Grocers', owner_id, 'https://images.unsplash.com/photo-1556741533-411cf82e4e2d?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='vikram.bhopal@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'MP Nagar Tech Hub', owner_id, 'https://images.unsplash.com/photo-1518779578993-ec3579fee39f?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='simran.bhopal@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Boring Road Bazaar', owner_id, 'https://images.unsplash.com/photo-1520962910036-3c66a9751650?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='neha.patna@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Kankarbagh SuperMart', owner_id, 'https://images.unsplash.com/photo-1585779034823-7e8062302234?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='anita.patna@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Patliputra Electronics', owner_id, 'https://images.unsplash.com/photo-1517059224940-d4af9eec41e5?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='arun.patna@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Godowlia Market', owner_id, 'https://images.unsplash.com/photo-1534531409543-069f0ee0d83c?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='aman.varanasi@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Assi Ghat Essentials', owner_id, 'https://images.unsplash.com/photo-1481571683436-1c568279dc4d?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='saurabh.varanasi@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Sigra Tech Square', owner_id, 'https://images.unsplash.com/photo-1549928616-06109b43b3b4?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='shreya.varanasi@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'MI Road Electronics', owner_id, 'https://images.unsplash.com/photo-1519223190983-8f7160a6f2b9?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='priya.jaipur@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Johari Bazaar Jewels', owner_id, 'https://images.unsplash.com/photo-1541264161754-016b1e2b0f55?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='pankaj.jaipur@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Vaishali Nagar Grocers', owner_id, 'https://images.unsplash.com/photo-1561715276-a2d083cf7b58?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='kavita.jaipur@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Shahpura Fresh', owner_id, 'https://images.unsplash.com/photo-1561715276-a2d083cf7b58?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='rahul.bhopal@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Frazer Road Electronics', owner_id, 'https://images.unsplash.com/photo-1519223190983-8f7160a6f2b9?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='sneha.patna@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Lanka Mobile Hub', owner_id, 'https://images.unsplash.com/photo-1517059224940-d4af9eec41e5?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='ashish.varanasi@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Bapu Bazaar Fashion', owner_id, 'https://images.unsplash.com/photo-1521334589026-2b0dddc4dd2b?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='karan.jaipur@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Kolar Road Mart', owner_id, 'https://images.unsplash.com/photo-1556741533-411cf82e4e2d?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='divya.bhopal@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Ashok Rajpath Books', owner_id, 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='manish.patna@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Dashashwamedh Bazaar', owner_id, 'https://images.unsplash.com/photo-1518779578993-ec3579fee39f?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='alok.varanasi@nearbuy.local';
INSERT INTO Shops (shop_id, shop_name, owner_id, shop_image, created_at)
SELECT randomblob(16), 'Malviya Nagar Home', owner_id, 'https://images.unsplash.com/photo-1515165562835-c3b8b4e0b1bb?q=80&w=1200&auto=format&fit=crop', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email='ritika.jaipur@nearbuy.local';

INSERT OR IGNORE INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Bhopal','India','462011','DB City Mall','Arera Hills',23.2350,77.4330,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='DB Mall Electronics';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Bhopal','India','462003','TT Nagar Stadium','New Market',23.2430,77.4020,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='New Market Grocers';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Bhopal','India','462011','Jyoti Cineplex','MP Nagar Zone 1',23.2335,77.4340,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='MP Nagar Tech Hub';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Patna','India','800020','Boring Canal Road','Boring Road',25.6110,85.1380,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Boring Road Bazaar';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Patna','India','800026','Kankarbagh Colony','Kankarbagh',25.5940,85.1580,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Kankarbagh SuperMart';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Patna','India','800013','Patliputra Station','Patliputra',25.6240,85.0960,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Patliputra Electronics';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Varanasi','India','221001','Godowlia Chowk','Godowlia',25.3170,82.9730,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Godowlia Market';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Varanasi','India','221005','Assi Ghat','Assi Ghat',25.2810,82.9680,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Assi Ghat Essentials';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Varanasi','India','221010','Sigra Crossing','Sigra',25.3040,82.9790,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Sigra Tech Square';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Jaipur','India','302001','MI Road','MI Road',26.9157,75.8180,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='MI Road Electronics';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Jaipur','India','302003','Johari Bazaar','Johari Bazaar',26.9160,75.8200,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Johari Bazaar Jewels';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Jaipur','India','302021','Vaishali Nagar','Vaishali Nagar',26.9110,75.7390,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Vaishali Nagar Grocers';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Bhopal','India','462016','Shahpura Lake','Shahpura',23.2000,77.4300,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Shahpura Fresh';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Patna','India','800001','Frazer Road','Frazer Road',25.6150,85.1410,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Frazer Road Electronics';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Varanasi','India','221005','Lanka Gate','Lanka',25.2815,82.9920,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Lanka Mobile Hub';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Jaipur','India','302007','Bapu Bazaar','Bapu Bazaar',26.9120,75.8160,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Bapu Bazaar Fashion';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Bhopal','India','462042','Kolar Road','Kolar Road',23.1900,77.4300,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Kolar Road Mart';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Patna','India','800004','Ashok Rajpath','Ashok Rajpath',25.6200,85.1500,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Ashok Rajpath Books';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Varanasi','India','221001','Dashashwamedh Ghat','Dashashwamedh',25.2876,83.0089,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Dashashwamedh Bazaar';
INSERT INTO Shop_Address (address_id, shop_id, city, country, pincode, landmark, area, latitude, longitude, created_at)
SELECT randomblob(16), shop_id,'Jaipur','India','302017','Malviya Nagar','Malviya Nagar',26.8500,75.8120,CURRENT_TIMESTAMP FROM Shops WHERE shop_name='Malviya Nagar Home';

INSERT OR IGNORE INTO Shop_Timings (timing_id, shop_id, day, open_time, close_time, created_at)
SELECT randomblob(16), shop_id,'Monday','10:00:00','21:00:00',CURRENT_TIMESTAMP FROM Shops WHERE shop_name IN ('DB Mall Electronics','New Market Grocers','MP Nagar Tech Hub','Boring Road Bazaar');
INSERT INTO Shop_Timings (timing_id, shop_id, day, open_time, close_time, created_at)
SELECT randomblob(16), shop_id,'Tuesday','10:00:00','21:00:00',CURRENT_TIMESTAMP FROM Shops WHERE shop_name IN ('DB Mall Electronics','New Market Grocers','MP Nagar Tech Hub','Boring Road Bazaar');
INSERT INTO Shop_Timings (timing_id, shop_id, day, open_time, close_time, created_at)
SELECT randomblob(16), shop_id,'Wednesday','10:00:00','21:00:00',CURRENT_TIMESTAMP FROM Shops WHERE shop_name IN ('DB Mall Electronics','New Market Grocers','MP Nagar Tech Hub','Boring Road Bazaar');
INSERT INTO Shop_Timings (timing_id, shop_id, day, open_time, close_time, created_at)
SELECT randomblob(16), shop_id,'Thursday','10:00:00','21:00:00',CURRENT_TIMESTAMP FROM Shops WHERE shop_name IN ('DB Mall Electronics','New Market Grocers','MP Nagar Tech Hub','Boring Road Bazaar');
INSERT INTO Shop_Timings (timing_id, shop_id, day, open_time, close_time, created_at)
SELECT randomblob(16), shop_id,'Friday','10:00:00','21:00:00',CURRENT_TIMESTAMP FROM Shops WHERE shop_name IN ('DB Mall Electronics','New Market Grocers','MP Nagar Tech Hub','Boring Road Bazaar');
INSERT INTO Shop_Timings (timing_id, shop_id, day, open_time, close_time, created_at)
SELECT randomblob(16), shop_id,'Saturday','10:00:00','21:30:00',CURRENT_TIMESTAMP FROM Shops WHERE shop_name IN ('DB Mall Electronics','New Market Grocers','MP Nagar Tech Hub','Boring Road Bazaar');
INSERT INTO Shop_Timings (timing_id, shop_id, day, open_time, close_time, created_at)
SELECT randomblob(16), shop_id,'Sunday',NULL,NULL,CURRENT_TIMESTAMP FROM Shops WHERE shop_name IN ('DB Mall Electronics','New Market Grocers','MP Nagar Tech Hub','Boring Road Bazaar');

INSERT OR IGNORE INTO Products (product_id, product_name, category_id, brand, description, color, created_at)
SELECT randomblob(16), 'iPhone 15', (SELECT category_id FROM Product_Categories WHERE category_name='Mobiles'), 'Apple', '128GB, Blue', 'Blue', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Samsung Galaxy S24', (SELECT category_id FROM Product_Categories WHERE category_name='Mobiles'), 'Samsung', '256GB, Black', 'Black', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Redmi Note 13', (SELECT category_id FROM Product_Categories WHERE category_name='Mobiles'), 'Xiaomi', '128GB, Green', 'Green', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Dell Inspiron 15', (SELECT category_id FROM Product_Categories WHERE category_name='Laptops'), 'Dell', 'i5, 16GB, 512GB', 'Silver', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'HP Pavilion 14', (SELECT category_id FROM Product_Categories WHERE category_name='Laptops'), 'HP', 'i7, 16GB, 1TB', 'Blue', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Lenovo IdeaPad 3', (SELECT category_id FROM Product_Categories WHERE category_name='Laptops'), 'Lenovo', 'Ryzen 5, 8GB, 512GB', 'Grey', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Amul Milk 1L', (SELECT category_id FROM Product_Categories WHERE category_name='Groceries'), 'Amul', 'Toned milk 1L', 'White', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Aashirvaad Atta 5kg', (SELECT category_id FROM Product_Categories WHERE category_name='Groceries'), 'ITC', 'Whole wheat 5kg', 'Brown', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Philips Mixer Grinder', (SELECT category_id FROM Product_Categories WHERE category_name='Home & Kitchen'), 'Philips', '750W, 3 jars', 'White', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Prestige Pressure Cooker 5L', (SELECT category_id FROM Product_Categories WHERE category_name='Home & Kitchen'), 'Prestige', 'Aluminium 5L', 'Silver', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Nike Running Shoes', (SELECT category_id FROM Product_Categories WHERE category_name='Footwear'), 'Nike', 'Air Zoom, UK 9', 'Black', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Adidas Sneakers', (SELECT category_id FROM Product_Categories WHERE category_name='Footwear'), 'Adidas', 'Daily wear, UK 8', 'White', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Boat Earbuds Airdopes', (SELECT category_id FROM Product_Categories WHERE category_name='Electronics'), 'Boat', 'Bluetooth earbuds', 'Black', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Sony Headphones WH-CH520', (SELECT category_id FROM Product_Categories WHERE category_name='Electronics'), 'Sony', 'Wireless on-ear', 'Blue', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'LG Smart TV 43"', (SELECT category_id FROM Product_Categories WHERE category_name='Electronics'), 'LG', '4K UHD, 43 inch', 'Black', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Colgate Toothpaste 200g', (SELECT category_id FROM Product_Categories WHERE category_name='Health & Personal Care'), 'Colgate', 'Mint 200g', 'Red', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Dove Shampoo 650ml', (SELECT category_id FROM Product_Categories WHERE category_name='Health & Personal Care'), 'Dove', 'Moisture 650ml', 'White', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Puma Sports T-Shirt', (SELECT category_id FROM Product_Categories WHERE category_name='Fashion'), 'Puma', 'Dryfit M', 'Blue', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Levis Denim Jeans', (SELECT category_id FROM Product_Categories WHERE category_name='Fashion'), 'Levis', 'Slim fit 32', 'Indigo', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Bajaj Auto Light', (SELECT category_id FROM Product_Categories WHERE category_name='Automotive'), 'Bajaj', 'Headlight accessory', 'Black', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Casio Watch MTP', (SELECT category_id FROM Product_Categories WHERE category_name='Watches'), 'Casio', 'Analog, Leather', 'Brown', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'American Tourister Backpack', (SELECT category_id FROM Product_Categories WHERE category_name='Bags'), 'American Tourister', '32L backpack', 'Black', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Necklace Set', (SELECT category_id FROM Product_Categories WHERE category_name='Jewellery'), 'Tanishq', 'Gold-plated set', 'Gold', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), 'Himalaya Baby Cream', (SELECT category_id FROM Product_Categories WHERE category_name='Baby Care'), 'Himalaya', '100ml', 'White', CURRENT_TIMESTAMP;

INSERT OR IGNORE INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=iPhone+15', CURRENT_TIMESTAMP FROM Products WHERE product_name='iPhone 15';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Samsung+S24', CURRENT_TIMESTAMP FROM Products WHERE product_name='Samsung Galaxy S24';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Redmi+Note+13', CURRENT_TIMESTAMP FROM Products WHERE product_name='Redmi Note 13';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Dell+Inspiron+15', CURRENT_TIMESTAMP FROM Products WHERE product_name='Dell Inspiron 15';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=HP+Pavilion+14', CURRENT_TIMESTAMP FROM Products WHERE product_name='HP Pavilion 14';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Lenovo+IdeaPad+3', CURRENT_TIMESTAMP FROM Products WHERE product_name='Lenovo IdeaPad 3';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Amul+Milk+1L', CURRENT_TIMESTAMP FROM Products WHERE product_name='Amul Milk 1L';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Aashirvaad+Atta+5kg', CURRENT_TIMESTAMP FROM Products WHERE product_name='Aashirvaad Atta 5kg';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Philips+Mixer', CURRENT_TIMESTAMP FROM Products WHERE product_name='Philips Mixer Grinder';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Prestige+Pressure+Cooker', CURRENT_TIMESTAMP FROM Products WHERE product_name='Prestige Pressure Cooker 5L';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Nike+Running+Shoes', CURRENT_TIMESTAMP FROM Products WHERE product_name='Nike Running Shoes';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Adidas+Sneakers', CURRENT_TIMESTAMP FROM Products WHERE product_name='Adidas Sneakers';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Boat+Earbuds', CURRENT_TIMESTAMP FROM Products WHERE product_name='Boat Earbuds Airdopes';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Sony+Headphones', CURRENT_TIMESTAMP FROM Products WHERE product_name='Sony Headphones WH-CH520';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=LG+Smart+TV', CURRENT_TIMESTAMP FROM Products WHERE product_name='LG Smart TV 43"';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Colgate+200g', CURRENT_TIMESTAMP FROM Products WHERE product_name='Colgate Toothpaste 200g';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Dove+Shampoo+650ml', CURRENT_TIMESTAMP FROM Products WHERE product_name='Dove Shampoo 650ml';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Puma+Tee', CURRENT_TIMESTAMP FROM Products WHERE product_name='Puma Sports T-Shirt';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Levis+Jeans', CURRENT_TIMESTAMP FROM Products WHERE product_name='Levis Denim Jeans';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Bajaj+Auto+Light', CURRENT_TIMESTAMP FROM Products WHERE product_name='Bajaj Auto Light';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Casio+MTP', CURRENT_TIMESTAMP FROM Products WHERE product_name='Casio Watch MTP';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=AT+Backpack', CURRENT_TIMESTAMP FROM Products WHERE product_name='American Tourister Backpack';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Tanishq+Necklace', CURRENT_TIMESTAMP FROM Products WHERE product_name='Necklace Set';
INSERT INTO Product_Images (image_id, product_id, image_url, created_at)
SELECT randomblob(16), product_id, 'https://via.placeholder.com/600x400?text=Himalaya+Baby+Cream', CURRENT_TIMESTAMP FROM Products WHERE product_name='Himalaya Baby Cream';

INSERT OR IGNORE INTO Shop_Product (shop_product_id, shop_id, product_id, price, stock, created_at)
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='DB Mall Electronics'), (SELECT product_id FROM Products WHERE product_name='iPhone 15'), 79999.00, 10, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='MI Road Electronics'), (SELECT product_id FROM Products WHERE product_name='iPhone 15'), 87999.00, 8, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Godowlia Market'), (SELECT product_id FROM Products WHERE product_name='iPhone 15'), 82999.00, 9, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Boring Road Bazaar'), (SELECT product_id FROM Products WHERE product_name='iPhone 15'), 76999.00, 11, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='DB Mall Electronics'), (SELECT product_id FROM Products WHERE product_name='Samsung Galaxy S24'), 74999.00, 12, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='MI Road Electronics'), (SELECT product_id FROM Products WHERE product_name='Samsung Galaxy S24'), 79999.00, 10, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Godowlia Market'), (SELECT product_id FROM Products WHERE product_name='Samsung Galaxy S24'), 76999.00, 9, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Boring Road Bazaar'), (SELECT product_id FROM Products WHERE product_name='Samsung Galaxy S24'), 72999.00, 13, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='New Market Grocers'), (SELECT product_id FROM Products WHERE product_name='Amul Milk 1L'), 65.00, 120, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Vaishali Nagar Grocers'), (SELECT product_id FROM Products WHERE product_name='Amul Milk 1L'), 62.00, 140, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Assi Ghat Essentials'), (SELECT product_id FROM Products WHERE product_name='Amul Milk 1L'), 64.00, 130, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Kankarbagh SuperMart'), (SELECT product_id FROM Products WHERE product_name='Amul Milk 1L'), 63.00, 115, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='New Market Grocers'), (SELECT product_id FROM Products WHERE product_name='Aashirvaad Atta 5kg'), 295.00, 60, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Vaishali Nagar Grocers'), (SELECT product_id FROM Products WHERE product_name='Aashirvaad Atta 5kg'), 285.00, 55, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Assi Ghat Essentials'), (SELECT product_id FROM Products WHERE product_name='Aashirvaad Atta 5kg'), 305.00, 52, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Kankarbagh SuperMart'), (SELECT product_id FROM Products WHERE product_name='Aashirvaad Atta 5kg'), 279.00, 58, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='MP Nagar Tech Hub'), (SELECT product_id FROM Products WHERE product_name='Dell Inspiron 15'), 59999.00, 5, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Sigra Tech Square'), (SELECT product_id FROM Products WHERE product_name='Dell Inspiron 15'), 61999.00, 4, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Patliputra Electronics'), (SELECT product_id FROM Products WHERE product_name='Dell Inspiron 15'), 57999.00, 6, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='MP Nagar Tech Hub'), (SELECT product_id FROM Products WHERE product_name='HP Pavilion 14'), 67999.00, 4, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Sigra Tech Square'), (SELECT product_id FROM Products WHERE product_name='HP Pavilion 14'), 69999.00, 3, CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT shop_id FROM Shops WHERE shop_name='Patliputra Electronics'), (SELECT product_id FROM Products WHERE product_name='HP Pavilion 14'), 65999.00, 5, CURRENT_TIMESTAMP;

INSERT OR IGNORE INTO Product_Reviews (review_id, user_id, product_id, rating, review_text, created_at)
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='aarav.sharma@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='iPhone 15'), 4.5, 'Great performance', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='neha.verma@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Samsung Galaxy S24'), 4.2, 'Excellent camera', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='rohit.gupta@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Dell Inspiron 15'), 4.0, 'Good value', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='ananya.singh@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Amul Milk 1L'), 5.0, 'Always fresh', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='vivek.patel@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Aashirvaad Atta 5kg'), 4.3, 'Quality flour', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='priya.jain@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Boat Earbuds Airdopes'), 4.1, 'Solid sound', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='aditya.roy@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Sony Headphones WH-CH520'), 4.4, 'Comfortable fit', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='sanya.tripathi@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='LG Smart TV 43"'), 4.6, 'Sharp picture', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='tanvi.tiwari@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Nike Running Shoes'), 4.3, 'Very comfy', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='aman.kumar@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Adidas Sneakers'), 4.0, 'Good everyday shoes', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='harsh.vardhan@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Philips Mixer Grinder'), 4.2, 'Strong motor', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='ishita.roy@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Prestige Pressure Cooker 5L'), 4.5, 'Useful size', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='deepak.yadav@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Colgate Toothpaste 200g'), 4.0, 'Fresh breath', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='kunal.mehta@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Dove Shampoo 650ml'), 4.1, 'Soft hair', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='shruti.nair@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Puma Sports T-Shirt'), 4.3, 'Great fit', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='riya.kapoor@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Levis Denim Jeans'), 4.4, 'Quality denim', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='aakash.singh@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Casio Watch MTP'), 4.2, 'Classic look', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='meghna.das@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='American Tourister Backpack'), 4.3, 'Durable', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='nikhil.jain@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Necklace Set'), 4.1, 'Elegant', CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='pooja.sinha@nearbuy.local'), (SELECT product_id FROM Products WHERE product_name='Himalaya Baby Cream'), 4.5, 'Gentle on skin', CURRENT_TIMESTAMP;

INSERT OR IGNORE INTO Search_History (history_id, user_id, search_item, timestamp)
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='aarav.sharma@nearbuy.local'),'iPhone',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='neha.verma@nearbuy.local'),'Samsung',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='rohit.gupta@nearbuy.local'),'Dell laptop',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='ananya.singh@nearbuy.local'),'Milk',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='vivek.patel@nearbuy.local'),'Atta',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='priya.jain@nearbuy.local'),'Earbuds',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='aditya.roy@nearbuy.local'),'Headphones',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='sanya.tripathi@nearbuy.local'),'Smart TV',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='tanvi.tiwari@nearbuy.local'),'Running Shoes',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='aman.kumar@nearbuy.local'),'Sneakers',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='harsh.vardhan@nearbuy.local'),'Mixer',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='ishita.roy@nearbuy.local'),'Pressure Cooker',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='deepak.yadav@nearbuy.local'),'Toothpaste',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='kunal.mehta@nearbuy.local'),'Shampoo',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='shruti.nair@nearbuy.local'),'T-Shirt',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='riya.kapoor@nearbuy.local'),'Jeans',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='aakash.singh@nearbuy.local'),'Watch',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='meghna.das@nearbuy.local'),'Backpack',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='nikhil.jain@nearbuy.local'),'Necklace',CURRENT_TIMESTAMP UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='pooja.sinha@nearbuy.local'),'Baby Cream',CURRENT_TIMESTAMP;

INSERT OR IGNORE INTO admin (admin_id,userId,password,created_at) VALUES
(randomblob(16),'nearbuy-admin','Admin@123',CURRENT_TIMESTAMP),
(randomblob(16),'ops-admin','Ops@123',CURRENT_TIMESTAMP),
(randomblob(16),'sales-admin','Sales@123',CURRENT_TIMESTAMP),
(randomblob(16),'bh-admin','Bh@123',CURRENT_TIMESTAMP),
(randomblob(16),'pt-admin','Pt@123',CURRENT_TIMESTAMP),
(randomblob(16),'vn-admin','Vn@123',CURRENT_TIMESTAMP),
(randomblob(16),'jp-admin','Jp@123',CURRENT_TIMESTAMP),
(randomblob(16),'it-admin','It@123',CURRENT_TIMESTAMP),
(randomblob(16),'sec-admin','Sec@123',CURRENT_TIMESTAMP),
(randomblob(16),'data-admin','Data@123',CURRENT_TIMESTAMP),
(randomblob(16),'qa-admin','Qa@123',CURRENT_TIMESTAMP),
(randomblob(16),'finance-admin','Fin@123',CURRENT_TIMESTAMP),
(randomblob(16),'support-admin','Sup@123',CURRENT_TIMESTAMP),
(randomblob(16),'owner-admin','Own@123',CURRENT_TIMESTAMP),
(randomblob(16),'city-admin','City@123',CURRENT_TIMESTAMP),
(randomblob(16),'store-admin','Store@123',CURRENT_TIMESTAMP),
(randomblob(16),'product-admin','Prod@123',CURRENT_TIMESTAMP),
(randomblob(16),'category-admin','Cat@123',CURRENT_TIMESTAMP),
(randomblob(16),'review-admin','Rev@123',CURRENT_TIMESTAMP),
(randomblob(16),'log-admin','Log@123',CURRENT_TIMESTAMP);

INSERT INTO Log (user_id, action_type, description, timestamp, ip_address, status_code)
SELECT (SELECT user_id FROM Users WHERE email='aarav.sharma@nearbuy.local'),'login','User login success',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='neha.verma@nearbuy.local'),'search','Searched Samsung',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='rohit.gupta@nearbuy.local'),'purchase','Purchased Dell Inspiron',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='ananya.singh@nearbuy.local'),'logout','User logout',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='vivek.patel@nearbuy.local'),'review','Posted review',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='priya.jain@nearbuy.local'),'login','User login success',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='aditya.roy@nearbuy.local'),'search','Searched headphones',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='sanya.tripathi@nearbuy.local'),'purchase','Purchased LG TV',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='tanvi.tiwari@nearbuy.local'),'logout','User logout',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='aman.kumar@nearbuy.local'),'review','Posted review',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='harsh.vardhan@nearbuy.local'),'login','User login success',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='ishita.roy@nearbuy.local'),'search','Searched cooker',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='deepak.yadav@nearbuy.local'),'purchase','Purchased Colgate',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='kunal.mehta@nearbuy.local'),'logout','User logout',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='shruti.nair@nearbuy.local'),'review','Posted review',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='riya.kapoor@nearbuy.local'),'login','User login success',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='aakash.singh@nearbuy.local'),'search','Searched watch',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='meghna.das@nearbuy.local'),'purchase','Purchased backpack',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='nikhil.jain@nearbuy.local'),'logout','User logout',CURRENT_TIMESTAMP,'127.0.0.1',200 UNION ALL
SELECT (SELECT user_id FROM Users WHERE email='pooja.sinha@nearbuy.local'),'review','Posted review',CURRENT_TIMESTAMP,'127.0.0.1',200;

INSERT OR IGNORE INTO User_Verification (ver_id, user_id, registration_started_at, registration_completed_at, email_verified_at, phone_verified_at, status)
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='aarav.sharma@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='neha.verma@nearbuy.local'), CURRENT_TIMESTAMP, NULL, NULL, NULL, 'pending' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='rohit.gupta@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='ananya.singh@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, CURRENT_TIMESTAMP, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='vivek.patel@nearbuy.local'), CURRENT_TIMESTAMP, NULL, NULL, NULL, 'pending' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='priya.jain@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='aditya.roy@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='sanya.tripathi@nearbuy.local'), CURRENT_TIMESTAMP, NULL, NULL, NULL, 'pending' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='tanvi.tiwari@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='aman.kumar@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='harsh.vardhan@nearbuy.local'), CURRENT_TIMESTAMP, NULL, NULL, NULL, 'pending' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='ishita.roy@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='deepak.yadav@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='kunal.mehta@nearbuy.local'), CURRENT_TIMESTAMP, NULL, NULL, NULL, 'pending' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='shruti.nair@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='riya.kapoor@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='aakash.singh@nearbuy.local'), CURRENT_TIMESTAMP, NULL, NULL, NULL, 'pending' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='meghna.das@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='nikhil.jain@nearbuy.local'), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'verified' UNION ALL
SELECT randomblob(16), (SELECT user_id FROM Users WHERE email='pooja.sinha@nearbuy.local'), CURRENT_TIMESTAMP, NULL, NULL, NULL, 'pending';

INSERT OR IGNORE INTO Owner_Security (sec_id, owner_id, email_verified_at, phone_verified_at, two_factor_enabled, two_factor_secret, last_2fa_verified_at)
SELECT randomblob(16), owner_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, 'ABCDEF123456', CURRENT_TIMESTAMP FROM Shop_Owners WHERE email IN ('rohit.bhopal@nearbuy.local','neha.patna@nearbuy.local','aman.varanasi@nearbuy.local','priya.jaipur@nearbuy.local','vikram.bhopal@nearbuy.local','anita.patna@nearbuy.local','saurabh.varanasi@nearbuy.local','kavita.jaipur@nearbuy.local','rahul.bhopal@nearbuy.local','sneha.patna@nearbuy.local');
INSERT INTO Owner_Security (sec_id, owner_id, email_verified_at, phone_verified_at, two_factor_enabled, two_factor_secret, last_2fa_verified_at)
SELECT randomblob(16), owner_id, CURRENT_TIMESTAMP, NULL, 0, NULL, NULL FROM Shop_Owners WHERE email IN ('ashish.varanasi@nearbuy.local','pankaj.jaipur@nearbuy.local','simran.bhopal@nearbuy.local','arun.patna@nearbuy.local','shreya.varanasi@nearbuy.local','karan.jaipur@nearbuy.local','divya.bhopal@nearbuy.local','manish.patna@nearbuy.local','alok.varanasi@nearbuy.local','ritika.jaipur@nearbuy.local');

INSERT OR IGNORE INTO Auth_Log (log_id, principal_type, principal_id, event_type, success, reason, ip, user_agent, occurred_at) VALUES
(randomblob(16),'user','aarav.sharma@nearbuy.local','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(randomblob(16),'user','neha.verma@nearbuy.local','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(randomblob(16),'user','rohit.gupta@nearbuy.local','refresh',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(randomblob(16),'user','ananya.singh@nearbuy.local','logout',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(randomblob(16),'owner','rohit.bhopal@nearbuy.local','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(randomblob(16),'owner','neha.patna@nearbuy.local','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(randomblob(16),'owner','aman.varanasi@nearbuy.local','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(randomblob(16),'owner','priya.jaipur@nearbuy.local','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(randomblob(16),'admin','nearbuy-admin','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(randomblob(16),'admin','ops-admin','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(hex(randomblob(16)),'user','vivek.patel@nearbuy.local','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(hex(randomblob(16)),'user','priya.jain@nearbuy.local','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(hex(randomblob(16)),'user','aditya.roy@nearbuy.local','refresh',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(hex(randomblob(16)),'user','sanya.tripathi@nearbuy.local','logout',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(hex(randomblob(16)),'owner','vikram.bhopal@nearbuy.local','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(hex(randomblob(16)),'owner','anita.patna@nearbuy.local','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(hex(randomblob(16)),'owner','saurabh.varanasi@nearbuy.local','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(hex(randomblob(16)),'owner','kavita.jaipur@nearbuy.local','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(hex(randomblob(16)),'admin','data-admin','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP),
(hex(randomblob(16)),'admin','qa-admin','login',1,NULL,'127.0.0.1','Mozilla/5.0',CURRENT_TIMESTAMP);

COMMIT;
