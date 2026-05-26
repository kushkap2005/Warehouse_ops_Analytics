"""
analysis.py
Runs 10 business SQL queries against warehouse_ops.db and saves results to data/.
"""

import sqlite3
import pandas as pd
import os

conn = sqlite3.connect("warehouse_ops.db")
os.makedirs("data", exist_ok=True)

QUERIES = {

# 1)UPH per picker
"picker_uph": """
SELECT
    p.picker_id,
    p.name,
    p.shift,
    p.accuracy_pct,
    COUNT(o.order_id)                                   AS total_orders,
    SUM(o.quantity)                                     AS total_units,
    ROUND(SUM(o.quantity) * 60.0 / SUM(o.fulfillment_time_min), 2) AS uph,
    ROUND(AVG(o.fulfillment_time_min), 1)               AS avg_fulfillment_min
FROM orders o
JOIN pickers p ON o.picker_id = p.picker_id
GROUP BY p.picker_id
ORDER BY uph DESC
""",

# 2)SKU velocity ranking
"sku_velocity": """
SELECT
    s.sku_id,
    s.product_name,
    s.category,
    s.storage_zone,
    s.price_inr,
    s.current_stock,
    s.reorder_level,
    SUM(o.quantity)  AS units_sold,
    COUNT(o.order_id) AS order_count,
    CASE
        WHEN SUM(o.quantity) >= 200 THEN 'Fast Mover'
        WHEN SUM(o.quantity) >= 80  THEN 'Medium Mover'
        ELSE 'Slow Mover'
    END AS velocity_tag,
    CASE
        WHEN s.current_stock <= s.reorder_level THEN 'REORDER NOW'
        WHEN s.current_stock <= s.reorder_level * 1.5 THEN 'Low Stock'
        ELSE 'OK'
    END AS stock_status
FROM skus s
LEFT JOIN orders o ON s.sku_id = o.sku_id
GROUP BY s.sku_id
ORDER BY units_sold DESC
""",

# 3)Peak hour order volume
"peak_hours": """
SELECT
    hour,
    COUNT(order_id)       AS total_orders,
    SUM(quantity)         AS total_units,
    ROUND(AVG(fulfillment_time_min),1) AS avg_fulfillment_min,
    CASE
        WHEN hour BETWEEN 9  AND 12 THEN 'Morning Peak'
        WHEN hour BETWEEN 17 AND 20 THEN 'Evening Peak'
        WHEN hour BETWEEN 6  AND 8  THEN 'Off-Peak Morning'
        WHEN hour BETWEEN 13 AND 16 THEN 'Afternoon Lull'
        ELSE 'Night'
    END AS period_label
FROM orders
GROUP BY hour
ORDER BY hour
""",

# 4)Daily order trend
"daily_trend": """
SELECT
    date,
    day_of_week,
    COUNT(order_id)  AS total_orders,
    SUM(quantity)    AS total_units,
    ROUND(AVG(fulfillment_time_min),1) AS avg_tat_min
FROM orders
GROUP BY date
ORDER BY date
""",

# 5)Reorder alerts
"reorder_alerts": """
SELECT
    s.sku_id,
    s.product_name,
    s.category,
    s.storage_zone,
    s.current_stock,
    s.reorder_level,
    s.reorder_level - s.current_stock AS shortage_units,
    ROUND(s.unit_cost_inr * (s.reorder_level * 2 - s.current_stock), 2) AS estimated_reorder_cost_inr,
    CASE
        WHEN s.current_stock = 0 THEN '🔴 OUT OF STOCK'
        WHEN s.current_stock <= s.reorder_level THEN '🟠 REORDER NOW'
        ELSE '🟡 LOW STOCK'
    END AS alert_level
FROM skus s
WHERE s.current_stock <= s.reorder_level * 1.5
ORDER BY s.current_stock ASC
""",

# 6)Cost per order by delivery slot
"slot_cost_analysis": """
SELECT
    d.delivery_slot,
    COUNT(d.delivery_id)                       AS total_deliveries,
    ROUND(AVG(d.delivery_cost_inr), 2)         AS avg_cost_inr,
    ROUND(AVG(d.distance_km), 2)               AS avg_distance_km,
    ROUND(AVG(d.time_taken_min), 1)            AS avg_time_min,
    SUM(d.delivery_cost_inr)                   AS total_cost_inr,
    COUNT(CASE WHEN d.status = 'Delivered' THEN 1 END) * 100.0 /
        COUNT(d.delivery_id)                   AS delivery_success_pct
FROM deliveries d
GROUP BY d.delivery_slot
ORDER BY avg_cost_inr DESC
""",

# 7)Category-wise fulfillment TAT
"category_tat": """
SELECT
    s.category,
    COUNT(o.order_id)                        AS total_orders,
    SUM(o.quantity)                          AS total_units,
    ROUND(AVG(o.fulfillment_time_min), 1)    AS avg_tat_min,
    MIN(o.fulfillment_time_min)              AS min_tat_min,
    MAX(o.fulfillment_time_min)              AS max_tat_min,
    ROUND(AVG(s.price_inr), 2)              AS avg_selling_price,
    SUM(o.quantity * s.price_inr)           AS total_revenue_inr
FROM orders o
JOIN skus s ON o.sku_id = s.sku_id
GROUP BY s.category
ORDER BY total_revenue_inr DESC
""",

# 8)Delivery status summary
"delivery_status": """
SELECT
    status,
    COUNT(*)                                  AS count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM deliveries), 2) AS pct
FROM deliveries
GROUP BY status
ORDER BY count DESC
""",

# 9)Day-of-week performance
"dow_performance": """
SELECT
    day_of_week,
    COUNT(order_id)                         AS total_orders,
    SUM(quantity)                           AS total_units,
    ROUND(AVG(fulfillment_time_min),1)      AS avg_tat_min,
    ROUND(SUM(quantity)*60.0/SUM(fulfillment_time_min),2) AS overall_uph
FROM orders
GROUP BY day_of_week
ORDER BY
    CASE day_of_week
        WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6
        ELSE 7 END
""",

# 10 ─ KPI summary
"kpi_summary": """
SELECT
    COUNT(DISTINCT o.order_id)                                       AS total_orders,
    SUM(o.quantity)                                                  AS total_units_picked,
    ROUND(AVG(o.fulfillment_time_min),1)                            AS avg_fulfillment_min,
    ROUND(SUM(o.quantity)*60.0/SUM(o.fulfillment_time_min),2)       AS overall_uph,
    ROUND(SUM(o.quantity * s.price_inr),2)                         AS total_gmv_inr,
    ROUND(AVG(d.delivery_cost_inr),2)                              AS avg_delivery_cost_inr,
    ROUND(SUM(d.delivery_cost_inr),2)                              AS total_delivery_cost_inr,
    COUNT(CASE WHEN o.status='Delivered' THEN 1 END)*100.0/COUNT(o.order_id) AS fulfillment_rate_pct,
    COUNT(CASE WHEN o.status='Returned'  THEN 1 END)*100.0/COUNT(o.order_id) AS return_rate_pct
FROM orders o
JOIN skus s       ON o.sku_id  = s.sku_id
JOIN deliveries d ON o.order_id = d.order_id
""",
}

results = {}
for name, sql in QUERIES.items():
    df = pd.read_sql_query(sql, conn)
    df.to_csv(f"data/{name}.csv", index=False)
    results[name] = df
    print(f"  ✓ {name:<25s}  {len(df)} rows")

conn.close()
print("\n  Analysis complete — CSVs saved to data/")


def get_results():
    return results
