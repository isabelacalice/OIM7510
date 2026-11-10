"""Writes fictional data for the Babson Bean Café database.

Run with: uv run python projects/db/make_data.py
Writes one CSV file per table into projects/db/data/.
"""

import csv
import random
from datetime import date, datetime, timedelta

random.seed(42)

AS_OF_DATE = date(2026, 11, 8)
START_DATE = AS_OF_DATE - timedelta(days=365)

MEMBER_COUNT = 50
MEMBERS_WITH_NO_ORDERS = 5  # last 5 member ids never place an order
PRODUCT_COUNT = 20
OPTION_COUNT = 8
ORDER_COUNT = 1000

DATA_FOLDER = "projects/db/data"


def random_date(start, end):
    days_between = (end - start).days
    offset = random.randint(0, days_between)
    return start + timedelta(days=offset)


# 1. Members
first_names = [
    "Olivia", "Liam", "Emma", "Noah", "Ava", "Ethan", "Sophia", "Mason",
    "Isabella", "Logan", "Mia", "Lucas", "Charlotte", "Jacob", "Amelia",
    "Aiden", "Harper", "James", "Evelyn", "Benjamin",
]

members = []
member_id = 1
while member_id <= MEMBER_COUNT:
    first_name = random.choice(first_names)
    mobile_number = "617-555-" + str(1000 + member_id)
    has_email = random.random() < 0.7
    if has_email:
        email = first_name.lower() + str(member_id) + "@example.com"
    else:
        email = ""
    join_date = random_date(START_DATE - timedelta(days=365), AS_OF_DATE)
    points_balance = random.randint(0, 500)
    members.append({
        "member_id": member_id,
        "first_name": first_name,
        "mobile_number": mobile_number,
        "email": email,
        "join_date": join_date.isoformat(),
        "points_balance": points_balance,
    })
    member_id = member_id + 1

members_who_can_order = []
for member in members:
    if member["member_id"] <= MEMBER_COUNT - MEMBERS_WITH_NO_ORDERS:
        members_who_can_order.append(member["member_id"])

# 2. Products (product_id 20 is held back from the last 60 days on purpose,
# so there is a product with no recent sales for a later business question)
product_names = [
    ("Drip Coffee", "coffee"),
    ("Latte", "coffee"),
    ("Cappuccino", "coffee"),
    ("Americano", "coffee"),
    ("Cold Brew", "coffee"),
    ("Green Tea", "tea"),
    ("Chai Latte", "tea"),
    ("Earl Grey", "tea"),
    ("Iced Tea", "tea"),
    ("Matcha Latte", "tea"),
    ("Blueberry Muffin", "food"),
    ("Croissant", "food"),
    ("Bagel with Cream Cheese", "food"),
    ("Avocado Toast", "food"),
    ("Breakfast Sandwich", "food"),
    ("Bottled Water", "other"),
    ("Orange Juice", "other"),
    ("Granola Bar", "other"),
    ("Fruit Cup", "other"),
    ("Seasonal Pumpkin Scone", "other"),
]

products = []
product_id = 1
no_recent_sales_product_id = PRODUCT_COUNT
while product_id <= PRODUCT_COUNT:
    name, category = product_names[product_id - 1]
    if category == "food":
        cost_cents = random.randint(100, 250)
    else:
        cost_cents = random.randint(40, 150)
    markup_cents = random.randint(100, 300)
    price_cents = cost_cents + markup_cents
    is_available = random.random() < 0.9
    products.append({
        "product_id": product_id,
        "name": name,
        "category": category,
        "price": price_cents / 100,
        "cost": cost_cents / 100,
        "is_available": is_available,
    })
    product_id = product_id + 1

# 3. Options (option_id 8 is free, on purpose, since a price can be zero)
option_names = [
    "Oat Milk", "Almond Milk", "Extra Shot", "Vanilla Syrup",
    "Caramel Syrup", "Whipped Cream", "Extra Espresso", "Decaf",
]

options = []
option_id = 1
while option_id <= OPTION_COUNT:
    name = option_names[option_id - 1]
    if name == "Decaf":
        price_cents = 0
    else:
        price_cents = random.randint(25, 100)
    cost_cents = random.randint(5, 40)
    options.append({
        "option_id": option_id,
        "name": name,
        "price": price_cents / 100,
        "cost": cost_cents / 100,
    })
    option_id = option_id + 1

# 4. Orders
channels = ["counter", "app"]

orders = []
order_id = 1
while order_id <= ORDER_COUNT:
    order_date = random_date(START_DATE, AS_OF_DATE)
    order_time = datetime(
        order_date.year, order_date.month, order_date.day,
        random.randint(7, 19), random.randint(0, 59), 0,
    )
    is_member_order = random.random() < 0.6
    if is_member_order:
        member_id = random.choice(members_who_can_order)
    else:
        member_id = ""
    channel = random.choice(channels)
    orders.append({
        "order_id": order_id,
        "member_id": member_id,
        "ordered_at": order_time.isoformat(sep=" "),
        "channel": channel,
        "_order_date": order_date,  # used below, not written to CSV
    })
    order_id = order_id + 1

# 5. Order lines, and which products each order may use
order_lines = []
order_line_id = 1
order_line_options = []

for order in orders:
    days_before_as_of = (AS_OF_DATE - order["_order_date"]).days
    available_product_ids = []
    for product in products:
        if product["product_id"] == no_recent_sales_product_id and days_before_as_of < 60:
            continue
        available_product_ids.append(product["product_id"])

    line_count = random.randint(1, 3)
    line_number = 1
    while line_number <= line_count:
        product_id = random.choice(available_product_ids)
        product = products[product_id - 1]
        quantity = random.randint(1, 3)
        order_lines.append({
            "order_line_id": order_line_id,
            "order_id": order["order_id"],
            "product_id": product_id,
            "quantity": quantity,
            "price_charged": product["price"],
        })

        option_count_on_line = random.randint(0, 2)
        if option_count_on_line > 0:
            chosen_options = random.sample(options, option_count_on_line)
            for option in chosen_options:
                order_line_options.append({
                    "order_line_id": order_line_id,
                    "option_id": option["option_id"],
                    "price_charged": option["price"],
                })

        order_line_id = order_line_id + 1
        line_number = line_number + 1

# 6. Each order's true total, in cents, from its lines and their options
order_total_cents = {}
for order in orders:
    order_total_cents[order["order_id"]] = 0

for line in order_lines:
    cents = round(line["price_charged"] * 100) * line["quantity"]
    order_total_cents[line["order_id"]] = order_total_cents[line["order_id"]] + cents

order_line_quantity = {}
for line in order_lines:
    order_line_quantity[line["order_line_id"]] = line["quantity"]
    order_line_to_order = {}

order_line_to_order = {}
for line in order_lines:
    order_line_to_order[line["order_line_id"]] = line["order_id"]

for line_option in order_line_options:
    order_line_id = line_option["order_line_id"]
    quantity = order_line_quantity[order_line_id]
    cents = round(line_option["price_charged"] * 100) * quantity
    this_order_id = order_line_to_order[order_line_id]
    order_total_cents[this_order_id] = order_total_cents[this_order_id] + cents

# 7. Payments, matching each order's total, except two orders on purpose.
# Pick two orders whose true total is at least $10.00, so taking $5.00 off
# still leaves a positive, realistic payment amount.
payment_methods = ["cash", "card", "app", "points"]
mismatched_order_ids = []
for order in orders:
    if order_total_cents[order["order_id"]] >= 1000:
        mismatched_order_ids.append(order["order_id"])
    if len(mismatched_order_ids) == 2:
        break

mismatch_amount_cents = {
    mismatched_order_ids[0]: -500,  # $5.00 short
    mismatched_order_ids[1]: 350,   # $3.50 over
}

payments = []
payment_id = 1
for order in orders:
    this_order_id = order["order_id"]
    true_total_cents = order_total_cents[this_order_id]

    if this_order_id in mismatched_order_ids:
        recorded_total_cents = true_total_cents + mismatch_amount_cents[this_order_id]
    else:
        recorded_total_cents = true_total_cents

    split_into_two = this_order_id not in mismatched_order_ids and random.random() < 0.3 and recorded_total_cents > 100
    if split_into_two:
        first_amount_cents = round(recorded_total_cents / 2)
        second_amount_cents = recorded_total_cents - first_amount_cents
        payments.append({
            "payment_id": payment_id,
            "order_id": this_order_id,
            "method": random.choice(payment_methods),
            "amount": first_amount_cents / 100,
        })
        payment_id = payment_id + 1
        payments.append({
            "payment_id": payment_id,
            "order_id": this_order_id,
            "method": random.choice(payment_methods),
            "amount": second_amount_cents / 100,
        })
        payment_id = payment_id + 1
    else:
        payments.append({
            "payment_id": payment_id,
            "order_id": this_order_id,
            "method": random.choice(payment_methods),
            "amount": recorded_total_cents / 100,
        })
        payment_id = payment_id + 1

# 8. Write every table to its own CSV file
for order in orders:
    del order["_order_date"]

tables_to_write = {
    "members.csv": (members, ["member_id", "first_name", "mobile_number", "email", "join_date", "points_balance"]),
    "products.csv": (products, ["product_id", "name", "category", "price", "cost", "is_available"]),
    "options.csv": (options, ["option_id", "name", "price", "cost"]),
    "orders.csv": (orders, ["order_id", "member_id", "ordered_at", "channel"]),
    "order_lines.csv": (order_lines, ["order_line_id", "order_id", "product_id", "quantity", "price_charged"]),
    "order_line_options.csv": (order_line_options, ["order_line_id", "option_id", "price_charged"]),
    "payments.csv": (payments, ["payment_id", "order_id", "method", "amount"]),
}

for file_name in tables_to_write:
    rows, fieldnames = tables_to_write[file_name]
    with open(DATA_FOLDER + "/" + file_name, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

print("Wrote", len(members), "members")
print("Wrote", len(products), "products")
print("Wrote", len(options), "options")
print("Wrote", len(orders), "orders")
print("Wrote", len(order_lines), "order lines")
print("Wrote", len(order_line_options), "order line options")
print("Wrote", len(payments), "payments")
print("Orders with a payment total that does not match the order total, on purpose:", mismatched_order_ids)
print("Order", mismatched_order_ids[0], "is paid $5.00 short; order", mismatched_order_ids[1], "is paid $3.50 over.")
print("Members with no orders, on purpose: member_id", MEMBER_COUNT - MEMBERS_WITH_NO_ORDERS + 1, "through", MEMBER_COUNT)
print("Product with no sales in the last 60 days, on purpose: product_id", no_recent_sales_product_id)
