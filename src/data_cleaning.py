
from pathlib import Path
import pandas as pd

# Rutas del proyecto
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

# Cargar archivos
orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")

# Convertir fechas a formato de fecha
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(orders[column], errors="coerce")

# Revisar calidad de los datos
print("\n===== CALIDAD DE LOS DATOS =====")

print("\nPEDIDOS")
print("Total de pedidos:", len(orders))
print("Pedidos duplicados:", orders["order_id"].duplicated().sum())
print("Valores faltantes por columna:")
print(orders.isnull().sum())

print("\nARTÍCULOS")
print("Total de artículos:", len(items))
print("Filas duplicadas:", items.duplicated().sum())
print("Valores faltantes por columna:")
print(items.isnull().sum())

# Revisar estados de los pedidos
print("\nESTADOS DE LOS PEDIDOS")
print(orders["order_status"].value_counts(dropna=False))

print("\n===== ANÁLISIS COMPLETADO =====")
