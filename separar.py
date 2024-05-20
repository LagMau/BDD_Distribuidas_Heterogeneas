customer_ids = []


archivo_sql1 = "BDD_SOE.sql"

with open(archivo_sql1, 'r') as archivo:
    for linea in archivo:
        if "Insert into CUSTOMERS" in linea and "'B'" in linea:
            customer_id = int(linea.split("'")[1])
            customer_ids.append(customer_id)




archivo_sql2 = "temp.sql"

with open(archivo_sql2, 'r') as archivo:
    valores_insert = []
    valores_temp = []
    order_ids = []
    cont= 0
    for linea in archivo:
        if "INSERT INTO orders" in linea:
            valores_temp = []
            cont+=1
            
        if cont > 0:
            valores_temp.append(linea.strip())

        if ";" in linea:
            insert_completo = " ".join(valores_temp)
            valores = insert_completo.split(",")
            order_id = valores[0].split("(")
            order_ids.append(int(order_id[1]))
            cont = 0

print(order_ids)
            
with open(archivo_sql1, 'r') as archivo:
    cont2 = 0
    for linea in archivo:
        if "Insert into ORDER_ITEMS" in linea:
            vals = linea.split("(")[2]
            key = int(vals.split(",")[0])
            if key in order_ids:
                print(linea)
                cont2+=1
            
print(len(order_ids))
print(cont2)
            




