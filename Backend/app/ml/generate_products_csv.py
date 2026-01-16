import csv
import random

CATEGORIES = {
    "Smartwatch": {
        "price": (1500, 45000),
        "desc": [
            "AMOLED display smartwatch with heart rate and SpO2 tracking",
            "GPS enabled smartwatch designed for outdoor fitness activities",
            "Premium smartwatch with stainless steel body and long battery life",
            "Lightweight smartwatch for daily activity and sleep tracking"
        ]
    },
    "Laptop Backpack": {
        "price": (1200, 9000),
        "desc": [
            "15.6 inch laptop backpack with padded compartments and water resistance",
            "Anti theft laptop backpack with USB charging port for office commute",
            "Large capacity laptop backpack suitable for travel and business trips",
            "Minimalist laptop backpack made of durable polyester fabric"
        ]
    },
    "Wireless Mouse": {
        "price": (400, 4500),
        "desc": [
            "Ergonomic wireless mouse with adjustable DPI for office work",
            "Gaming wireless mouse with RGB lighting and high precision sensor",
            "Compact wireless mouse designed for travel and portability",
            "Rechargeable wireless mouse with silent click buttons"
        ]
    },
    "Keyboard": {
        "price": (800, 12000),
        "desc": [
            "Mechanical keyboard with blue switches and RGB lighting",
            "Wireless keyboard with low profile keys for productivity",
            "Compact keyboard suitable for programmers and developers",
            "Gaming keyboard with anti ghosting keys"
        ]
    }
}

TOTAL = 12000

with open("products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "name", "desp", "price", "quantity"])

    pid = 1
    for _ in range(TOTAL):
        category = random.choice(list(CATEGORIES.keys()))
        meta = CATEGORIES[category]

        price = random.randint(*meta["price"])
        quantity = random.randint(5, 200)

        writer.writerow([
            pid,
            f"{category} Model {pid}",
            random.choice(meta["desc"]),
            price,
            quantity
        ])
        pid += 1

print("products.csv generated with 12,000 DB-compatible products")
