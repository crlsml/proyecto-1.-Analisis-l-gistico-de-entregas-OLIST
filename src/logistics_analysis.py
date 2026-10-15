
from pathlib import Path
import pandas as pd

# Rutas del proyecto
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

# Cargar pedidos
orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")

# Convertir fechas
date_columns = [
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )

# Filtrar pedidos entregados
delivered = orders[
    (orders["order_status"] == "delivered")
    & (orders["order_delivered_customer_date"].notna())
    & (orders["order_estimated_delivery_date"].notna())
].copy()

# Calcular diferencia entre entrega real y estimada
delivered["delay_days"] = (
    delivered["order_delivered_customer_date"]
    - delivered["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

# Clasificar las entregas
delivered["delivery_result"] = delivered["delay_days"].apply(
    lambda days: "Retrasado" if days > 0 else "A tiempo"
)

# Calcular indicadores
total_delivered = len(delivered)
on_time = (delivered["delay_days"] <= 0).sum()
late = (delivered["delay_days"] > 0).sum()

on_time_pct = on_time / total_delivered * 100
late_pct = late / total_delivered * 100

delivery_days = (
    delivered["order_delivered_customer_date"]
    - delivered["order_purchase_timestamp"]
).dt.total_seconds() / 86400

avg_delivery_days = delivery_days.mean()
avg_delay_days = delivered.loc[
    delivered["delay_days"] > 0, "delay_days"
].mean()

# Mostrar resultados
print("\n===== INDICADORES LOGÍSTICOS =====")
print(f"Pedidos entregados analizados: {total_delivered:,}")
print(f"Entregas a tiempo: {on_time:,} ({on_time_pct:.2f}%)")
print(f"Entregas retrasadas: {late:,} ({late_pct:.2f}%)")
print(f"Tiempo promedio de entrega: {avg_delivery_days:.2f} días")
print(f"Retraso promedio entre entregas tardías: {avg_delay_days:.2f} días")

print("\n===== ANÁLISIS COMPLETADO =====")



# ===== ANALISIS MENSUAL =====

# Crear columna con el mes de compra
delivered["purchase_month"] = (
    delivered["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype(str)
)

# Agrupar por mes
monthly = delivered.groupby("purchase_month").agg(
    total_orders=("order_id", "count"),
    late_orders=("delay_days", lambda x: (x > 0).sum()),
    avg_delivery_days=(
        "order_delivered_customer_date",
        lambda x: (
            x - delivered.loc[x.index, "order_purchase_timestamp"]
        ).dt.total_seconds().div(86400).mean()
    )
).reset_index()

# Calcular porcentaje de retrasos
monthly["late_percentage"] = (
    monthly["late_orders"] / monthly["total_orders"] * 100
)

# Ordenar por porcentaje de retrasos
monthly = monthly.sort_values(
    "late_percentage", ascending=False
)

print("\n===== RETRASOS POR MES =====")
print(
    monthly.to_string(
        index=False,
        formatters={
            "avg_delivery_days": "{:.2f}".format,
            "late_percentage": "{:.2f}%".format
        }
    )
)

# Exportar resultados
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

monthly.to_csv(
    OUTPUT_DIR / "monthly_logistics_analysis.csv",
    index=False
)

print("\nArchivo guardado en outputs/monthly_logistics_analysis.csv")


# ===== GRAFICA DE RETRASOS MENSUALES =====

import matplotlib.pyplot as plt

# Orden cronologico para la grafica
monthly_chart = monthly.sort_values("purchase_month")

plt.figure(figsize=(12, 6))

plt.plot(
    monthly_chart["purchase_month"],
    monthly_chart["late_percentage"],
    marker="o",
    linewidth=2
)

plt.title("Porcentaje de pedidos retrasados por mes")
plt.xlabel("Mes de compra")
plt.ylabel("Pedidos retrasados (%)")

plt.xticks(rotation=60)
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Guardar grafica en outputs
plt.savefig(
    OUTPUT_DIR / "monthly_delivery_delays.png",
    dpi=150
)

plt.show()

print("Grafica guardada en outputs/monthly_delivery_delays.png")

