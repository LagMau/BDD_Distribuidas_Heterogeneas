create database link link_A
CONNECT TO system 
IDENTIFIED BY "123"
USING '
(DESCRIPTION=
(ADDRESS=
(PROTOCOL=TCP)
(HOST=172.17.0.2)
(PORT=1521)
)
(CONNECT_DATA=
(SID=free)
)
)';

create database link link_B
CONNECT TO system IDENTIFIED BY "123"
USING '
(DESCRIPTION=
(ADDRESS=
(PROTOCOL=TCP)
(HOST=172.17.0.3)
(PORT=1522)
)
(CONNECT_DATA=
(SID=free)
)
)';

CREATE VIEW all_customers AS
SELECT 
    'Tienda-1' AS source_db,
    CUSTOMER_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CREDIT_LIMIT,
    CUST_EMAIL,
    INCOME_LEVEL,
    REGION
FROM 
    CUSTOMERS

UNION ALL

SELECT 
    'Tienda-2' AS source_db,
    CUSTOMER_ID,
    CUST_FIRST_NAME,
    CUST_LAST_NAME,
    CREDIT_LIMIT,
    CUST_EMAIL,
    INCOME_LEVEL,
    REGION
FROM 
    CUSTOMERS@link_B;


CREATE VIEW all_orders AS
SELECT 
    'Tienda-1' AS source_db,
    ORDER_ID,
    ORDER_DATE,
    ORDER_MODE,
    CUSTOMER_ID,
    ORDER_STATUS,
    ORDER_TOTAL,
    SALES_REP_ID,
    PROMOTION_ID
FROM 
    ORDERS

UNION ALL

SELECT 
    'Tienda-2' AS source_db,
    ORDER_ID,
    ORDER_DATE,
    ORDER_MODE,
    CUSTOMER_ID,
    ORDER_STATUS,
    ORDER_TOTAL,
    SALES_REP_ID,
    PROMOTION_ID
FROM 
    ORDERS@link_B;


CREATE VIEW all_order_items AS
SELECT 
    'Tienda-1' AS source_db,
    ORDER_ID,
    LINE_ITEM_ID,
    PRODUCT_ID,
    UNIT_PRICE,
    QUANTITY
FROM 
    ORDER_ITEMS

UNION ALL

SELECT 
    'Tienda-2' AS source_db,
    ORDER_ID,
    LINE_ITEM_ID,
    PRODUCT_ID,
    UNIT_PRICE,
    QUANTITY
FROM 
    ORDER_ITEMS@link_B;


CREATE TABLE customers_backup (
    customer_id NUMBER(6),
    cust_first_name VARCHAR2(20),
    cust_last_name VARCHAR2(20),
    credit_limit NUMBER(9,2),
    cust_email VARCHAR2(30),
    income_level VARCHAR2(20),
    region VARCHAR2(1)
);

CREATE OR REPLACE TRIGGER replicar_customers
AFTER INSERT OR DELETE OR UPDATE ON customers
FOR EACH ROW
BEGIN
    IF INSERTING THEN 
        INSERT INTO customers_backup (customer_id, cust_first_name, cust_last_name, credit_limit, cust_email, income_level, region)
        VALUES (:NEW.customer_id, :NEW.cust_first_name, :NEW.cust_last_name, :NEW.credit_limit, :NEW.cust_email, :NEW.income_level, :NEW.region);
    ELSIF DELETING THEN
        DELETE FROM customers_backup
        WHERE customer_id = :OLD.customer_id;
    ELSE 
        UPDATE customers_backup
        SET cust_first_name = :NEW.cust_first_name,
            cust_last_name = :NEW.cust_last_name,
            credit_limit = :NEW.credit_limit,
            cust_email = :NEW.cust_email,
            income_level = :NEW.income_level,
            region = :NEW.region
        WHERE customer_id = :OLD.customer_id;
    END IF;
END;


CREATE TABLE orders_backup (
    order_id NUMBER(12),
    order_date TIMESTAMP (6) WITH LOCAL TIME ZONE,
    customer_id NUMBER(6),
    order_status NUMBER(2),
    order_total NUMBER(8)
);

create or replace trigger replicar_orders
after insert or delete or update on orders
for each row
begin
    if inserting then 
        insert into orders_backup(order_id, order_date, customer_id, order_status, order_total)
        VALUES (:NEW.order_id, :NEW.order_date, :NEW.customer_id, :NEW.order_status, :NEW.order_total);
    elsif deleting then
        delete from orders_backup
        where order_id = :OLD.order_id;
    else 
        update orders_backup
        SET order_date = :NEW.order_date,
            customer_id = :NEW.customer_id,
            order_status = :NEW.order_status,
            order_total = :NEW.order_total
        WHERE order_id = :OLD.order_id;
    end if;
end;

CREATE TABLE order_items_backup (
    order_id NUMBER(12),
    line_item_id NUMBER(3),
    product_id NUMBER(6),
    unit_price NUMBER(8),
    quantity NUMBER(8)
);

CREATE OR REPLACE TRIGGER replicar_order_items
AFTER INSERT OR DELETE OR UPDATE ON order_items
FOR EACH ROW
BEGIN
    IF INSERTING THEN 
        INSERT INTO order_items_backup (order_id, line_item_id, product_id, unit_price, quantity)
        VALUES (:NEW.order_id, :NEW.line_item_id, :NEW.product_id, :NEW.unit_price, :NEW.quantity);
    ELSIF DELETING THEN
        DELETE FROM order_items_backup
        WHERE order_id = :OLD.order_id
        AND line_item_id = :OLD.line_item_id;
    ELSE 
        UPDATE order_items_backup
        SET unit_price = :NEW.unit_price,
            quantity = :NEW.quantity
        WHERE order_id = :OLD.order_id
        AND line_item_id = :OLD.line_item_id;
    END IF;
END;

CREATE TABLE product_information_backup (
    product_id NUMBER(6),
    product_name VARCHAR2(50),
    product_description VARCHAR2(2000),
    category_id NUMBER(2),
    weight_class NUMBER(1),
    warranty_period INTERVAL YEAR (2) TO MONTH,
    supplier_id NUMBER(6),
    product_status VARCHAR2(20),
    list_price NUMBER(8),
    min_price NUMBER(8,2),
    catalog_url VARCHAR2(50)
);

CREATE OR REPLACE TRIGGER replicar_product_information
AFTER INSERT OR DELETE OR UPDATE ON product_information
FOR EACH ROW
BEGIN
    IF INSERTING THEN 
        INSERT INTO product_information_backup (
            product_id, product_name, product_description, category_id, 
            weight_class, warranty_period, supplier_id, product_status, 
            list_price, min_price, catalog_url)
        VALUES (
            :NEW.product_id, :NEW.product_name, :NEW.product_description, 
            :NEW.category_id, :NEW.weight_class, :NEW.warranty_period, 
            :NEW.supplier_id, :NEW.product_status, 
            :NEW.list_price, :NEW.min_price, :NEW.catalog_url);
    ELSIF DELETING THEN
        DELETE FROM product_information_backup
        WHERE product_id = :OLD.product_id;
    ELSE 
        UPDATE product_information_backup
        SET product_name = :NEW.product_name,
            product_description = :NEW.product_description,
            category_id = :NEW.category_id,
            weight_class = :NEW.weight_class,
            warranty_period = :NEW.warranty_period,
            supplier_id = :NEW.supplier_id,
            product_status = :NEW.product_status,
            list_price = :NEW.list_price,
            min_price = :NEW.min_price,
            catalog_url = :NEW.catalog_url
        WHERE product_id = :OLD.product_id;
    END IF;
END;

CREATE PUBLIC SYNONYM customers_a FOR customers;
CREATE PUBLIC SYNONYM orders_a FOR orders;
CREATE PUBLIC SYNONYM order_items_a FOR order_items;
CREATE PUBLIC SYNONYM products FOR product_information;

CREATE PUBLIC SYNONYM customers_b FOR customers@link_b;
CREATE PUBLIC SYNONYM orders_b FOR orders@link_b;
CREATE PUBLIC SYNONYM order_items_b FOR order_items@link_b;