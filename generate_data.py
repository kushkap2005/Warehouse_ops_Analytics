"""
generate_data.py
Creates realistic synthetic warehouse operations data and saves to CSV + SQLite.
"""

import sqlite3
import random
import csv
import os
from datetime import datetime, timedelta

random.seed(42)

def rnd(a, b, decimals=2):
    return round(random.uniform(a, b), decimals)

def weighted_choice(choices, weights):
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for c, w in zip(choices, weights):
        upto += w
        if r <= upto:
            return c
    return choices[-1]


CATEGORIES = {
    "Electronics":   ["USB Hub", "HDMI Cable", "Wireless Mouse", "Keyboard", "Webcam", "Power Bank", "Earbuds", "Smart Bulb"],
    "Home & Kitchen":["Blender", "Coffee Maker", "Non-stick Pan", "Cutting Board", "Water Bottle", "Tupperware Set", "Dish Rack"],
    "Apparel":       ["Polo Shirt", "Running Shorts", "Sports Socks", "Cap", "Hoodie", "Yoga Pants"],
    "Books":         ["Python Basics", "Data Science 101", "Supply Chain Mgmt", "Marketing Guide", "Finance Essentials"],
    "Health":        ["Vitamin C 500mg", "Protein Powder", "Hand Sanitizer", "Face Mask Pack", "Thermometer"],
    "Stationery":    ["Notebook", "Ball Pen Set", "Stapler", "File Folder", "Whiteboard Marker"],
}

ZONES = {"Electronics": "A", "Home & Kitchen": "B", "Apparel": "C",
         "Books": "D", "Health": "E", "Stationery": "F"}

skus = []
sku_id = 1
for cat, products in CATEGORIES.items():
    for product in products:
        skus.append({
            "sku_id":        f"SKU{sku_id:03d}",
            "product_name":  product,
            "category":      cat,
            "weight_kg":     rnd(0.1, 5.0),
            "price_inr":     rnd(99, 4999),
            "storage_zone":  ZONES[cat],
            "reorder_level": random.randint(20, 100),
            "current_stock": random.randint(0, 300),
            "unit_cost_inr": rnd(50, 2500),
        })
        sku_id += 1


PICKER_NAMES = ["Ravi Kumar", "Sunita Devi", "Amit Sharma", "Priya Singh",
                "Rahul Verma", "Neha Gupta", "Deepak Yadav", "Kavita Patel"]

SHIFTS = [
    ("Morning",   "06:00", "14:00"),
    ("Afternoon", "14:00", "22:00"),
    ("Night",     "22:00", "06:00"),
]

pickers = []
for i, name in enumerate(PICKER_NAMES):
    shift_name, shift_start, shift_end = SHIFTS[i % 3]
    pickers.append({
        "picker_id":    f"P{i+1:02d}",
        "name":         name,
        "shift":        shift_name,
        "shift_start":  shift_start,
        "shift_end":    shift_end,
        "experience_yr": random.randint(1, 8),
        "accuracy_pct": rnd(92, 99.5),
    })


START_DATE = datetime(2024, 3, 1)
DELIVERY_SLOTS = ["09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00"]
STATUS_OPTIONS = ["Delivered", "Delivered", "Delivered", "Returned", "Delayed"]

# SKU velocity: some sell much more than others
SKU_IDS   = [s["sku_id"] for s in skus]
SKU_WEIGHTS = [random.randint(1, 10) for _ in SKU_IDS]

PICKER_IDS = [p["picker_id"] for p in pickers]

# Hour-of-day weights (peak: 10-12 and 18-20)
HOUR_WEIGHTS = [1,1,1,1,1,1, 2,4,7,9,10,9, 7,5,5,6,8,10,10,8, 5,3,2,1]

orders = []
for order_num in range(1, 5001):
    day_offset = random.randint(0, 29)
    hour       = weighted_choice(range(24), HOUR_WEIGHTS)
    minute     = random.randint(0, 59)
    ts         = START_DATE + timedelta(days=day_offset, hours=hour, minutes=minute)

    sku        = weighted_choice(SKU_IDS, SKU_WEIGHTS)
    qty        = random.randint(1, 10)
    picker     = random.choice(PICKER_IDS)
    slot       = random.choice(DELIVERY_SLOTS)

    # fulfillment time varies by hour and picker experience
    base_ft    = random.randint(15, 90)
    if hour in range(10, 13) or hour in range(17, 21):
        base_ft += random.randint(5, 20)   # peak hours slower

    status     = weighted_choice(STATUS_OPTIONS, [60, 60, 60, 10, 10])

    orders.append({
        "order_id":           f"ORD{order_num:05d}",
        "timestamp":          ts.strftime("%Y-%m-%d %H:%M:%S"),
        "date":               ts.strftime("%Y-%m-%d"),
        "hour":               hour,
        "day_of_week":        ts.strftime("%A"),
        "sku_id":             sku,
        "quantity":           qty,
        "picker_id":          picker,
        "delivery_slot":      slot,
        "fulfillment_time_min": base_ft,
        "status":             status,
    })


deliveries = []
for o in orders:
    dist_km  = rnd(1, 45)
    base_cost = 30 + dist_km * 2.5
    slot_mult = {"09:00-12:00": 1.0, "12:00-15:00": 1.05,
                 "15:00-18:00": 1.1, "18:00-21:00": 1.2}
    cost = round(base_cost * slot_mult[o["delivery_slot"]] * random.uniform(0.9, 1.1), 2)
    time_taken = round(dist_km * random.uniform(2.5, 4.5), 1)
    deliveries.append({
        "delivery_id":     f"DEL{o['order_id'][3:]}",
        "order_id":        o["order_id"],
        "date":            o["date"],
        "delivery_slot":   o["delivery_slot"],
        "distance_km":     dist_km,
        "time_taken_min":  time_taken,
        "delivery_cost_inr": cost,
        "status":          o["status"],
    })


def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  ✓ {path}  ({len(rows)} rows)")

write_csv("data/orders.csv",     orders,     list(orders[0].keys()))
write_csv("data/skus.csv",       skus,       list(skus[0].keys()))
write_csv("data/pickers.csv",    pickers,    list(pickers[0].keys()))
write_csv("data/deliveries.csv", deliveries, list(deliveries[0].keys()))


import pandas as pd

conn = sqlite3.connect("warehouse_ops.db")

for tbl, path in [("orders","data/orders.csv"), ("skus","data/skus.csv"),
                  ("pickers","data/pickers.csv"), ("deliveries","data/deliveries.csv")]:
    df = pd.read_csv(path)
    df.to_sql(tbl, conn, if_exists="replace", index=False)
    print(f"  ✓ SQLite table [{tbl}]  ({len(df)} rows)")

conn.close()
print("\n Data generation complete.")
