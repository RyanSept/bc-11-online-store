CREATE TABLE shop (
    shop_id integer primary key autoincrement,
    shop_name varchar,
    shop_desc text,
    shop_location varchar,
    shop_url varchar,
);

CREATE TABLE product (
    product_id integer primary key autoincrement,
    product_title varchar,
    product_desc text,
    product_price float, 
    product_image varchar,
);

CREATE TABLE shopproduct (
    shop_id FOREIGN KEY (shop_ID) REFERENCES shop(shop_id),
    product_id FOREIGN KEY (product_id) REFERENCES product(product_id),
);