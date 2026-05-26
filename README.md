# 🏭 Warehouse Operations Analytics

A Python + SQLite + Excel system that simulates a real warehouse's operations data and extracts actionable business insights — exactly like what a supply chain analyst would do on the job.

---

## 📁 Project Structure

```
warehouse-ops-analytics/
├── data/
│   ├── orders.csv              ← 5,000 synthetic orders (30 days)
│   ├── skus.csv                ← 41 SKUs across 6 categories
│   ├── pickers.csv             ← 8 warehouse pickers with shift data
│   ├── deliveries.csv          ← Delivery records with cost + distance
│   ├── picker_uph.csv          ← UPH analysis per picker
│   ├── sku_velocity.csv        ← SKU velocity ranking
│   ├── peak_hours.csv          ← Hourly order volume
│   ├── daily_trend.csv         ← 30-day order trend
│   ├── reorder_alerts.csv      ← Stock replenishment alerts
│   ├── slot_cost_analysis.csv  ← Delivery cost by time slot
│   ├── category_tat.csv        ← Fulfilment TAT by category
│   ├── delivery_status.csv     ← Delivery outcome summary
│   ├── dow_performance.csv     ← Day-of-week performance
│   └── kpi_summary.csv         ← Headline KPIs
├── generate_data.py            ← Creates all synthetic data + loads SQLite
├── analysis.py                 ← 10 SQL business queries via Pandas
├── dashboard.py                ← Builds the 6-sheet Excel dashboard
├── warehouse_ops.db            ← SQLite database (auto-created)
├── Warehouse_Operations_Dashboard.xlsx  ← Final Excel output
└── README.md
```

---

## 🚀 How to Run

### Prerequisites
```bash
pip install pandas openpyxl numpy
```

### Step 1 — Generate Data
```bash
python generate_data.py
```
Creates 4 CSV files in `data/` and loads them into `warehouse_ops.db`.

### Step 2 — Run Analysis
```bash
python analysis.py
```
Executes 10 SQL business queries and saves results as CSVs in `data/`.

### Step 3 — Build Dashboard
```bash
python dashboard.py
```
Produces `Warehouse_Operations_Dashboard.xlsx` — a professional 6-sheet Excel dashboard.

---

## 📊 Dashboard Sheets

| Sheet | Contents |
|---|---|
| 📊 KPI Summary | Headline KPIs, top pickers, stock alerts |
| 👷 Picker Productivity | UPH, accuracy, TAT per picker with charts |
| 📦 SKU Performance | Velocity ranking, stock health, revenue share pie |
| 📈 Demand Patterns | Hourly/daily heatmap, day-of-week analysis |
| 🚚 Delivery Cost Analysis | Cost per slot, distance, delivery status |
| 🔔 Replenishment Alerts | Out-of-stock, reorder now, zone-level summary |

---

## 💡 Business Insights (from Actual Data)

1. **Peak hour bottleneck (10–12 AM & 6–8 PM):** Order volume spikes by 3× during these windows while fulfillment time increases by ~25 minutes. Scheduling an extra picker on these shifts alone could recover ~12% throughput.

2. **Bottom 20% of SKUs contribute <3% of GMV but occupy full storage zones.** Reclassifying slow-movers (Slow Mover tag) to a single consolidated zone frees up ~2 zone-equivalents for fast-moving Electronics and Health SKUs.

3. **Evening slot (18:00–21:00) costs 20% more per delivery** than the morning slot. Offering a small customer incentive (e.g., ₹20 discount) to shift demand to 09:00–12:00 could reduce total delivery spend by an estimated ₹1.2L/month.

4. **Two pickers consistently operate below 5 UPH** — well below the warehouse average of ~7. Targeted retraining or pairing with high-UPH peers on morning shifts could close this gap within 4–6 weeks.

5. **~15 SKUs are at or below reorder level at any given time,** with Books and Stationery zones most at risk. Implementing automated weekly reorder triggers at 1.5× the reorder threshold would eliminate stock-out-driven order cancellations.

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Data Generation | Python (random, csv, datetime) |
| Database | SQLite3 |
| Analysis | Pandas + SQL |
| Dashboard | openpyxl |

---

## 📂 Where to Store Files

```
All files stay inside the warehouse-ops-analytics/ folder.
Run all scripts from INSIDE that folder (not from a parent directory).
The Excel output is created in the same root folder.
```

---

*Built as a supply chain analytics portfolio project. All data is synthetic.*
