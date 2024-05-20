import tkinter as tk
from tkinter import ttk
import oracledb
from datetime import datetime

class OracleDBManager:
    def __init__(self):
        # Conexión a la base de datos de la tienda 1
        self.conn1 = oracledb.connect(user='system', password='123', dsn='localhost:1521/free')
        self.cursor1 = self.conn1.cursor()
        
        # Conexión a la base de datos de la tienda 2
        self.conn2 = oracledb.connect(user='system', password='123', dsn='localhost:1522/free')
        self.cursor2 = self.conn2.cursor()

    def get_region_by_customer(self, customer_id):
        # Buscar en la base de datos de la tienda 1
        self.cursor1.execute("SELECT REGION FROM CUSTOMERS WHERE CUSTOMER_ID = :1", (customer_id,))
        region = self.cursor1.fetchone()
        if region:
            return 'A', region[0]  # Indicar que es la tienda 1 y devolver la región

        # Buscar en la base de datos de la tienda 2
        self.cursor2.execute("SELECT REGION FROM CUSTOMERS WHERE CUSTOMER_ID = :1", (customer_id,))
        region = self.cursor2.fetchone()
        if region:
            return 'B', region[0]  # Indicar que es la tienda 2 y devolver la región

        return None, None  # No se encontró el cliente

    def add_customer(self, customer_id, cust_first_name, cust_last_name, credit_limit, cust_email, income_level, region):
        cursor = self.cursor1 if region in ['A', 'B'] else self.cursor2
        cursor.callproc("AddCustomer", [customer_id, cust_first_name, cust_last_name, credit_limit, cust_email, income_level, region])
        (self.conn1 if region in ['A', 'B'] else self.conn2).commit()

    def update_customer(self, customer_id, cust_first_name, cust_last_name, credit_limit, cust_email, income_level, region):
        cursor = self.cursor1 if region in ['A', 'B'] else self.cursor2
        cursor.callproc("UpdateCustomer", [customer_id, cust_first_name, cust_last_name, credit_limit, cust_email, income_level, region])
        (self.conn1 if region in ['A', 'B'] else self.conn2).commit()

    def delete_customer(self, customer_id, region):
        cursor = self.cursor1 if region in ['A', 'B'] else self.cursor2
        cursor.callproc("DeleteCustomer", [customer_id])
        (self.conn1 if region in ['A', 'B'] else self.conn2).commit()
        
    def show_customers(self):
        query = "SELECT * FROM all_customers"
        cursor1_results = self.cursor1.execute(query).fetchall()      
        return cursor1_results 

    def add_order(self, order_id, order_date, order_mode, customer_id, order_status, order_total, sales_rep_id, promotion_id):
        store, region = self.get_region_by_customer(customer_id)
        if store == 'A':
            cursor = self.cursor1
        elif store == 'B':
            cursor = self.cursor2
        else:
            raise ValueError("El cliente no se encuentra en ninguna tienda.")
        
        cursor.callproc("AddOrder", [order_id, order_date, order_mode, customer_id, order_status, order_total, sales_rep_id, promotion_id])
        (self.conn1 if store == 'A' else self.conn2).commit()

    def update_order(self, order_id, order_date, order_mode, customer_id, order_status, order_total, sales_rep_id, promotion_id):
        store, region = self.get_region_by_customer(customer_id)
        if store == 'A':
            cursor = self.cursor1
        elif store == 'B':
            cursor = self.cursor2
        else:
            raise ValueError("El cliente no se encuentra en ninguna tienda.")

        cursor.callproc("UpdateOrder", [order_id, order_date, order_mode, customer_id, order_status, order_total, sales_rep_id, promotion_id])
        (self.conn1 if store == 'A' else self.conn2).commit()

    def delete_order(self, order_id, customer_id):
        store, region = self.get_region_by_customer(customer_id)
        if store == 'A':
            cursor = self.cursor1
        elif store == 'B':
            cursor = self.cursor2
        else:
            raise ValueError("El cliente no se encuentra en ninguna tienda.")

        cursor.callproc("DeleteOrder", [order_id])
        (self.conn1 if store == 'A' else self.conn2).commit()
        
    def show_orders(self):
        query = "SELECT * FROM all_orders"
        cursor1_results = self.cursor1.execute(query).fetchall()    
        return cursor1_results 

    def add_order_item(self, order_id, line_item_id, product_id, unit_price, quantity):
        customer_id = self.get_customer_id_by_order(order_id)
        store, region = self.get_region_by_customer(customer_id)
        if store == 'A':
            cursor = self.cursor1
        elif store == 'B':
            cursor = self.cursor2
        else:
            raise ValueError("El cliente no se encuentra en ninguna tienda.")

        cursor.callproc("AddOrderItem", [order_id, line_item_id, product_id, unit_price, quantity])
        (self.conn1 if store == 'A' else self.conn2).commit()

    def update_order_item(self, order_id, line_item_id, product_id, unit_price, quantity):
        customer_id = self.get_customer_id_by_order(order_id)
        store, region = self.get_region_by_customer(customer_id)
        if store == 'A':
            cursor = self.cursor1
        elif store == 'B':
            cursor = self.cursor2
        else:
            raise ValueError("El cliente no se encuentra en ninguna tienda.")
        
        cursor.callproc("UpdateOrderItem", [order_id, line_item_id, product_id, unit_price, quantity])
        (self.conn1 if store == 'A' else self.conn2).commit()

    def delete_order_item(self, order_id, line_item_id):
        customer_id = self.get_customer_id_by_order(order_id)
        store, region = self.get_region_by_customer(customer_id)
        if store == 'A':
            cursor = self.cursor1
        elif store == 'B':
            cursor = self.cursor2
        else:
            raise ValueError("El cliente no se encuentra en ninguna tienda.")

        cursor.callproc("DeleteOrderItem", [order_id, line_item_id])
        (self.conn1 if store == 'A' else self.conn2).commit()
        
    def show_order_items(self):
        query = "SELECT * FROM all_order_items"
        cursor1_results = self.cursor1.execute(query).fetchall()    
        return cursor1_results 

    def add_product(self, product_id, product_name, product_description, category_id, weight_class, warranty_period, supplier_id, product_status, list_price, min_price, catalog_url):
        for cursor in [self.cursor1, self.cursor2]:
            cursor.callproc("AddProduct", [product_id, product_name, product_description, category_id, weight_class, warranty_period, supplier_id, product_status, list_price, min_price, catalog_url])
        self.conn1.commit()
        self.conn2.commit()

    def update_product(self, product_id, product_name, product_description, category_id, weight_class, warranty_period, supplier_id, product_status, list_price, min_price, catalog_url):
        for cursor in [self.cursor1, self.cursor2]:
            cursor.callproc("UpdateProduct", [product_id, product_name, product_description, category_id, weight_class, warranty_period, supplier_id, product_status, list_price, min_price, catalog_url])
        self.conn1.commit()
        self.conn2.commit()

    def delete_product(self, product_id):
        for cursor in [self.cursor1, self.cursor2]:
            cursor.callproc("DeleteProduct", [product_id])
        self.conn1.commit()
        self.conn2.commit()
        
    def show_products(self):
        query = "SELECT PRODUCT_ID, PRODUCT_NAME, PRODUCT_DESCRIPTION, CATEGORY_ID, WEIGHT_CLASS, SUPPLIER_ID, PRODUCT_STATUS, LIST_PRICE, MIN_PRICE, CATALOG_URL FROM PRODUCT_INFORMATION"
        cursor1_results = self.cursor1.execute(query).fetchall()    
        return cursor1_results 

    def get_customer_id_by_order(self, order_id):
        self.cursor1.execute("SELECT CUSTOMER_ID FROM ORDERS WHERE ORDER_ID = :1", (order_id,))
        result = self.cursor1.fetchone()
        if result:
            return result[0]

        self.cursor2.execute("SELECT CUSTOMER_ID FROM ORDERS WHERE ORDER_ID = :1", (order_id,))
        result = self.cursor2.fetchone()
        if result:
            return result[0]

        return None

def date():
    # Obtener la fecha y hora actual
    ahora = datetime.now()

    # Formatear la fecha en el formato 'DD-MON-YY HH.MI.SS.FF AM/PM'
    fecha_formateada = ahora.strftime('%d-%b-%y %I.%M.%S.%f %p').upper()
    return fecha_formateada

# GUI
def create_customer_button_clicked():
    customer_id = int(customer_id_entry.get())
    cust_first_name = cust_first_name_entry.get()
    cust_last_name = cust_last_name_entry.get()
    credit_limit = float(credit_limit_entry.get())
    cust_email = cust_email_entry.get()
    income_level = income_level_entry.get()
    region = region_entry.get()
    db_manager.add_customer(customer_id, cust_first_name, cust_last_name, credit_limit, cust_email, income_level, region)

def update_customer_button_clicked():
    customer_id = int(customer_id_entry.get())
    cust_first_name = cust_first_name_entry.get()
    cust_last_name = cust_last_name_entry.get()
    credit_limit = float(credit_limit_entry.get())
    cust_email = cust_email_entry.get()
    income_level = income_level_entry.get()
    region = region_entry.get()
    db_manager.update_customer(customer_id, cust_first_name, cust_last_name, credit_limit, cust_email, income_level, region)

def delete_customer_button_clicked():
    customer_id = int(customer_id_entry.get())
    region = region_entry.get()
    db_manager.delete_customer(customer_id, region)
    
def show_customers_button_clicked():
    for item in customer_tree.get_children():
        customer_tree.delete(item)
    for row in db_manager.show_customers():
        customer_tree.insert('', tk.END, values=row)

def create_order_button_clicked():
    order_id = int(order_id_entry.get())
    order_date = date()
    order_mode = order_mode_entry.get()
    customer_id = int(order_customer_id_entry.get())
    order_status = int(order_status_entry.get())
    order_total = float(order_total_entry.get())
    sales_rep_id = int(sales_rep_id_entry.get())
    promotion_id = int(promotion_id_entry.get())
    db_manager.add_order(order_id, order_date, order_mode, customer_id, order_status, order_total, sales_rep_id, promotion_id)

def update_order_button_clicked():
    order_id = int(order_id_entry.get())
    order_date = date()
    order_mode = order_mode_entry.get()
    customer_id = int(order_customer_id_entry.get())
    order_status = int(order_status_entry.get())
    order_total = float(order_total_entry.get())
    sales_rep_id = int(sales_rep_id_entry.get())
    promotion_id = int(promotion_id_entry.get())
    db_manager.update_order(order_id, order_date, order_mode, customer_id, order_status, order_total, sales_rep_id, promotion_id)

def delete_order_button_clicked():
    order_id = int(order_id_entry.get())
    customer_id = int(order_customer_id_entry.get())
    db_manager.delete_order(order_id, customer_id)
    
def show_orders_button_clicked():
    for item in order_tree.get_children():
        order_tree.delete(item)
    for row in db_manager.show_orders():
        order_tree.insert('', tk.END, values=row)

def create_order_item_button_clicked():
    order_id = int(order_item_order_id_entry.get())
    line_item_id = int(line_item_id_entry.get())
    product_id = int(order_item_product_id_entry.get())
    unit_price = float(unit_price_entry.get())
    quantity = int(quantity_entry.get())
    db_manager.add_order_item(order_id, line_item_id, product_id, unit_price, quantity)

def update_order_item_button_clicked():
    order_id = int(order_item_order_id_entry.get())
    line_item_id = int(line_item_id_entry.get())
    product_id = int(order_item_product_id_entry.get())
    unit_price = float(unit_price_entry.get())
    quantity = int(quantity_entry.get())
    db_manager.update_order_item(order_id, line_item_id, product_id, unit_price, quantity)

def delete_order_item_button_clicked():
    order_id = int(order_item_order_id_entry.get())
    line_item_id = int(line_item_id_entry.get())
    db_manager.delete_order_item(order_id, line_item_id)
    
def show_order_items_button_clicked():
    for item in order_item_tree.get_children():
        order_item_tree.delete(item)
    for row in db_manager.show_order_items():
        order_item_tree.insert('', tk.END, values=row)

def create_product_button_clicked():
    product_id = int(product_id_entry.get())
    product_name = product_name_entry.get()
    product_description = product_description_entry.get()
    category_id = int(category_id_entry.get())
    weight_class = weight_class_entry.get()
    warranty_period = warranty_period_entry.get()
    supplier_id = int(supplier_id_entry.get())
    product_status = product_status_entry.get()
    list_price = float(list_price_entry.get())
    min_price = float(min_price_entry.get())
    catalog_url = catalog_url_entry.get()
    db_manager.add_product(product_id, product_name, product_description, category_id, weight_class, warranty_period, supplier_id, product_status, list_price, min_price, catalog_url)

def update_product_button_clicked():
    product_id = int(product_id_entry.get())
    product_name = product_name_entry.get()
    product_description = product_description_entry.get()
    category_id = int(category_id_entry.get())
    weight_class = weight_class_entry.get()
    warranty_period = warranty_period_entry.get()
    supplier_id = int(supplier_id_entry.get())
    product_status = product_status_entry.get()
    list_price = float(list_price_entry.get())
    min_price = float(min_price_entry.get())
    catalog_url = catalog_url_entry.get()
    db_manager.update_product(product_id, product_name, product_description, category_id, weight_class, warranty_period, supplier_id, product_status, list_price, min_price, catalog_url)

def delete_product_button_clicked():
    product_id = int(product_id_entry.get())
    db_manager.delete_product(product_id)
    

def show_product_information_button_clicked():
    for item in product_info_tree.get_children():
        product_info_tree.delete(item)
    for row in db_manager.show_products():
        product_info_tree.insert('', tk.END, values=row)

root = tk.Tk()
root.title("Gestión de Tiendas")

db_manager = OracleDBManager()

notebook = ttk.Notebook(root)

# Pestaña Clientes
customer_frame = ttk.Frame(notebook)
notebook.add(customer_frame, text="Clientes")

customer_id_label = tk.Label(customer_frame, text="ID del Cliente:")
cust_first_name_label = tk.Label(customer_frame, text="Nombre:")
cust_last_name_label = tk.Label(customer_frame, text="Apellido:")
credit_limit_label = tk.Label(customer_frame, text="Límite de Crédito:")
cust_email_label = tk.Label(customer_frame, text="Email:")
income_level_label = tk.Label(customer_frame, text="Nivel de Ingresos:")
region_label = tk.Label(customer_frame, text="Región:")

customer_id_entry = tk.Entry(customer_frame)
cust_first_name_entry = tk.Entry(customer_frame)
cust_last_name_entry = tk.Entry(customer_frame)
credit_limit_entry = tk.Entry(customer_frame)
cust_email_entry = tk.Entry(customer_frame)
income_level_entry = tk.Entry(customer_frame)
region_entry = tk.Entry(customer_frame)

create_customer_button = tk.Button(customer_frame, text="Crear Cliente", command=create_customer_button_clicked)
update_customer_button = tk.Button(customer_frame, text="Actualizar Cliente", command=update_customer_button_clicked)
delete_customer_button = tk.Button(customer_frame, text="Eliminar Cliente", command=delete_customer_button_clicked)
show_customers_button = tk.Button(customer_frame, text="Mostrar Clientes", command=show_customers_button_clicked)

customer_tree = ttk.Treeview(customer_frame, columns=("source_db", "customer_id", "cust_first_name", "cust_last_name", "credit_limit", "cust_email", "income_level", "region"), show='headings')
customer_tree.heading("source_db", text="Source DB")
customer_tree.heading("customer_id", text="Customer ID")
customer_tree.heading("cust_first_name", text="First Name")
customer_tree.heading("cust_last_name", text="Last Name")
customer_tree.heading("credit_limit", text="Credit Limit")
customer_tree.heading("cust_email", text="Email")
customer_tree.heading("income_level", text="Income Level")
customer_tree.heading("region", text="Region")

customer_id_label.grid(row=0, column=0)
cust_first_name_label.grid(row=1, column=0)
cust_last_name_label.grid(row=2, column=0)
credit_limit_label.grid(row=3, column=0)
cust_email_label.grid(row=4, column=0)
income_level_label.grid(row=5, column=0)
region_label.grid(row=6, column=0)

customer_id_entry.grid(row=0, column=1)
cust_first_name_entry.grid(row=1, column=1)
cust_last_name_entry.grid(row=2, column=1)
credit_limit_entry.grid(row=3, column=1)
cust_email_entry.grid(row=4, column=1)
income_level_entry.grid(row=5, column=1)
region_entry.grid(row=6, column=1)

create_customer_button.grid(row=7, column=0)
update_customer_button.grid(row=7, column=1)
delete_customer_button.grid(row=8, column=0)

show_customers_button.grid(row=8, column=1)
customer_tree.grid(row=9, column=0, columnspan=2, sticky='nsew')


# Pestaña Pedidos
order_frame = ttk.Frame(notebook)
notebook.add(order_frame, text="Pedidos")

order_id_label = tk.Label(order_frame, text="ID del Pedido:")
order_mode_label = tk.Label(order_frame, text="Modo del Pedido:")
order_customer_id_label = tk.Label(order_frame, text="ID del Cliente:")
order_status_label = tk.Label(order_frame, text="Estado del Pedido:")
order_total_label = tk.Label(order_frame, text="Total del Pedido:")
sales_rep_id_label = tk.Label(order_frame, text="ID del Representante:")
promotion_id_label = tk.Label(order_frame, text="ID de Promocion:")

order_id_entry = tk.Entry(order_frame)
order_mode_entry = tk.Entry(order_frame)
order_customer_id_entry = tk.Entry(order_frame)
order_status_entry = tk.Entry(order_frame)
order_total_entry = tk.Entry(order_frame)
sales_rep_id_entry = tk.Entry(order_frame)
promotion_id_entry = tk.Entry(order_frame)


create_order_button = tk.Button(order_frame, text="Crear Pedido", command=create_order_button_clicked)
update_order_button = tk.Button(order_frame, text="Actualizar Pedido", command=update_order_button_clicked)
delete_order_button = tk.Button(order_frame, text="Eliminar Pedido", command=delete_order_button_clicked)
show_orders_button = tk.Button(order_frame, text="Mostrar Pedidos", command=show_orders_button_clicked)

order_tree = ttk.Treeview(order_frame, columns=("order_id", "order_date", "order_mode", "customer_id", "order_status", "order_total", "sales_rep_id", "promotion_id"), show='headings')
order_tree.heading("order_id", text="Order ID")
order_tree.heading("order_date", text="Order Date")
order_tree.heading("order_mode", text="Order Mode")
order_tree.heading("customer_id", text="Customer ID")
order_tree.heading("order_status", text="Order Status")
order_tree.heading("order_total", text="Order Total")
order_tree.heading("sales_rep_id", text="Sales Rep ID")
order_tree.heading("promotion_id", text="Promotion ID")

order_id_label.grid(row=0, column=0)
order_mode_label.grid(row=1, column=0)
order_customer_id_label.grid(row=2, column=0)
order_status_label.grid(row=3, column=0)
order_total_label.grid(row=4, column=0)
sales_rep_id_label.grid(row=5, column=0)
promotion_id_label.grid(row=6, column=0)

order_id_entry.grid(row=0, column=1)
order_mode_entry.grid(row=1, column=1)
order_customer_id_entry.grid(row=2, column=1)
order_status_entry.grid(row=3, column=1)
order_total_entry.grid(row=4, column=1)
sales_rep_id_entry.grid(row=5, column=1)
promotion_id_entry.grid(row=6, column=1)


create_order_button.grid(row=7, column=0)
update_order_button.grid(row=7, column=1)
delete_order_button.grid(row=8, column=0)

show_orders_button.grid(row=8, column=1)
order_tree.grid(row=9, column=0, columnspan=2, sticky='nsew')

# Pestaña Items de Pedido
order_item_frame = ttk.Frame(notebook)
notebook.add(order_item_frame, text="Items de Pedido")

order_item_order_id_label = tk.Label(order_item_frame, text="ID del Pedido:")
line_item_id_label = tk.Label(order_item_frame, text="ID del Item:")
order_item_product_id_label = tk.Label(order_item_frame, text="ID del Producto:")
unit_price_label = tk.Label(order_item_frame, text="Precio Unitario:")
quantity_label = tk.Label(order_item_frame, text="Cantidad:")

order_item_order_id_entry = tk.Entry(order_item_frame)
line_item_id_entry = tk.Entry(order_item_frame)
order_item_product_id_entry = tk.Entry(order_item_frame)
unit_price_entry = tk.Entry(order_item_frame)
quantity_entry = tk.Entry(order_item_frame)

create_order_item_button = tk.Button(order_item_frame, text="Crear Item de Pedido", command=create_order_item_button_clicked)
update_order_item_button = tk.Button(order_item_frame, text="Actualizar Item de Pedido", command=update_order_item_button_clicked)
delete_order_item_button = tk.Button(order_item_frame, text="Eliminar Item de Pedido", command=delete_order_item_button_clicked)
show_order_items_button = tk.Button(order_item_frame, text="Mostrar Ítems de Pedido", command=show_order_items_button_clicked)

order_item_tree = ttk.Treeview(order_item_frame, columns=("order_id", "line_item_id", "product_id", "unit_price", "quantity"), show='headings')
order_item_tree.heading("order_id", text="Order ID")
order_item_tree.heading("line_item_id", text="Line Item ID")
order_item_tree.heading("product_id", text="Product ID")
order_item_tree.heading("unit_price", text="Unit Price")
order_item_tree.heading("quantity", text="Quantity")

order_item_order_id_label.grid(row=0, column=0)
line_item_id_label.grid(row=1, column=0)
order_item_product_id_label.grid(row=2, column=0)
unit_price_label.grid(row=3, column=0)
quantity_label.grid(row=4, column=0)

order_item_order_id_entry.grid(row=0, column=1)
line_item_id_entry.grid(row=1, column=1)
order_item_product_id_entry.grid(row=2, column=1)
unit_price_entry.grid(row=3, column=1)
quantity_entry.grid(row=4, column=1)

create_order_item_button.grid(row=5, column=0)
update_order_item_button.grid(row=5, column=1)
delete_order_item_button.grid(row=6, column=0)

show_order_items_button.grid(row=6, column=1)
order_item_tree.grid(row=7, column=0, columnspan=2, sticky='nsew')

# Pestaña Productos
product_frame = ttk.Frame(notebook)
notebook.add(product_frame, text="Productos")

product_id_label = tk.Label(product_frame, text="ID del Producto:")
product_name_label = tk.Label(product_frame, text="Nombre del Producto:")
product_description_label = tk.Label(product_frame, text="Descripción del Producto:")
category_id_label = tk.Label(product_frame, text="ID de Categoría:")
weight_class_label = tk.Label(product_frame, text="Clase de Peso:")
warranty_period_label = tk.Label(product_frame, text="Periodo de Garantía:")
supplier_id_label = tk.Label(product_frame, text="ID del Proveedor:")
product_status_label = tk.Label(product_frame, text="Estado del Producto:")
list_price_label = tk.Label(product_frame, text="Precio de Lista:")
min_price_label = tk.Label(product_frame, text="Precio Mínimo:")
catalog_url_label = tk.Label(product_frame, text="URL del Catálogo:")

product_id_entry = tk.Entry(product_frame)
product_name_entry = tk.Entry(product_frame)
product_description_entry = tk.Entry(product_frame)
category_id_entry = tk.Entry(product_frame)
weight_class_entry = tk.Entry(product_frame)
warranty_period_entry = tk.Entry(product_frame)
supplier_id_entry = tk.Entry(product_frame)
product_status_entry = tk.Entry(product_frame)
list_price_entry = tk.Entry(product_frame)
min_price_entry = tk.Entry(product_frame)
catalog_url_entry = tk.Entry(product_frame)

create_product_button = tk.Button(product_frame, text="Crear Producto", command=create_product_button_clicked)
update_product_button = tk.Button(product_frame, text="Actualizar Producto", command=update_product_button_clicked)
delete_product_button = tk.Button(product_frame, text="Eliminar Producto", command=delete_product_button_clicked)
show_product_information_button = tk.Button(product_frame, text="Mostrar Productos", command=show_product_information_button_clicked)

product_info_tree = ttk.Treeview(product_frame, columns=("product_id", "product_name", "product_description", "category_id", "weight_class", "supplier_id", "product_status", "list_price", "min_price", "catalog_url"), show='headings')
product_info_tree.heading("product_id", text="Product ID")
product_info_tree.heading("product_name", text="Product Name")
product_info_tree.heading("product_description", text="Product Description")
product_info_tree.heading("category_id", text="Category ID")
product_info_tree.heading("weight_class", text="Weight Class")
product_info_tree.heading("supplier_id", text="Supplier ID")
product_info_tree.heading("product_status", text="Product Status")
product_info_tree.heading("list_price", text="List Price")
product_info_tree.heading("min_price", text="Min Price")
product_info_tree.heading("catalog_url", text="Catalog URL")

product_id_label.grid(row=0, column=0)
product_name_label.grid(row=1, column=0)
product_description_label.grid(row=2, column=0)
category_id_label.grid(row=3, column=0)
weight_class_label.grid(row=4, column=0)
warranty_period_label.grid(row=5, column=0)
supplier_id_label.grid(row=6, column=0)
product_status_label.grid(row=7, column=0)
list_price_label.grid(row=8, column=0)
min_price_label.grid(row=9, column=0)
catalog_url_label.grid(row=10, column=0)

product_id_entry.grid(row=0, column=1)
product_name_entry.grid(row=1, column=1)
product_description_entry.grid(row=2, column=1)
category_id_entry.grid(row=3, column=1)
weight_class_entry.grid(row=4, column=1)
warranty_period_entry.grid(row=5, column=1)
supplier_id_entry.grid(row=6, column=1)
product_status_entry.grid(row=7, column=1)
list_price_entry.grid(row=8, column=1)
min_price_entry.grid(row=9, column=1)
catalog_url_entry.grid(row=10, column=1)

create_product_button.grid(row=11, column=0)
update_product_button.grid(row=11, column=1)
delete_product_button.grid(row=12, column=0)

show_product_information_button.grid(row=12, column=1)
product_info_tree.grid(row=13, column=0, columnspan=2, sticky='nsew')

notebook.pack(expand=1, fill="both")

root.mainloop()