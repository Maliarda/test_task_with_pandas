import pandas as pd
import json

with open("data.json") as f:
    data = json.load(f)

# Task 1. Find the shipping cost rate for each warehouse

tariffs = pd.DataFrame(columns=["warehouse_name", "tariff"])
processed_warehouses = set()

for order in data:
    warehouse_name = order["warehouse_name"]

    if warehouse_name in processed_warehouses:
        continue

    products = order["products"]

    total_quantity = sum(product["quantity"] for product in products)
    total_highway_cost = abs(order["highway_cost"])

    per_item_cost = total_highway_cost / total_quantity

    warehouse_df = pd.DataFrame(
        {"warehouse_name": [warehouse_name], "tariff": [per_item_cost]}
    )

    tariffs = pd.concat([tariffs, warehouse_df], ignore_index=True)

    processed_warehouses.add(warehouse_name)

print(tariffs)

# Task 2. Find the total quantity, total income, total expense
# and total profit for each product.

results = pd.DataFrame(
    columns=["product", "quantity", "income", "expenses", "profit"]
)

for order in data:
    products = order["products"]
    for product in products:
        product_name = product["product"]
        quantity = product["quantity"]
        price = product["price"]
        income = price * quantity
        expenses = abs(order["highway_cost"]) * quantity
        profit = income - expenses

        row = {
            "product": product_name,
            "quantity": quantity,
            "income": income,
            "expenses": expenses,
            "profit": profit,
        }

        results = pd.concat([results, pd.DataFrame([row])], ignore_index=True)

results = (
    results.groupby("product")
    .agg(
        {
            "quantity": "sum",
            "income": "sum",
            "expenses": "sum",
            "profit": "sum",
        }
    )
    .reset_index()
)

print(results)

# Task 3. Create a table with columns 'order_id' (order id) and 'order_profit'
# (profit received from the order).
# And also display the average profit of orders

profit_from_orders = pd.DataFrame(columns=["order_id", "order_profit"])

for order in data:
    order_id = order["order_id"]
    products = order["products"]
    order_profit = sum(
        product["price"] * product["quantity"] for product in products
    ) - abs(order["highway_cost"])

    profit_from_orders.loc[len(profit_from_orders)] = [order_id, order_profit]

print(profit_from_orders)

average_profit = profit_from_orders["order_profit"].mean()

print("Средняя прибыль заказов:", average_profit)

# Task 4.
# Create a table like 'warehouse_name', 'product','quantity', 'profit',
# 'percent_profit_product_of_warehouse' (percentage of the profit of a
# product ordered from a certain warehouse to the profit of this warehouse)

warehouse_profit = pd.DataFrame(
    columns=["warehouse_name", "product", "quantity", "profit"]
)

for order in data:
    warehouse_name = order["warehouse_name"]
    products = order["products"]

    order_profit = 0
    rows = []
    for product in products:
        product_name = product["product"]
        quantity = product["quantity"]
        price = product["price"]
        product_profit = price * quantity
        order_profit += product_profit

        rows.append(
            {
                "warehouse_name": warehouse_name,
                "product": product_name,
                "quantity": quantity,
                "profit": product_profit,
            }
        )

    order_df = pd.DataFrame(rows)

    warehouse_profit = pd.merge(warehouse_profit, order_df, how="outer")

warehouse_profit["percent_profit_product_of_warehouse"] = (
    warehouse_profit["profit"]
    / warehouse_profit.groupby("warehouse_name")["profit"].transform("sum")
    * 100
)

warehouse_profit = warehouse_profit.sort_values(by="warehouse_name")

print(warehouse_profit)

# Task 5.
# Take the previous table and sort 'percent_profit_product_of_warehouse'
# in descending order, # then calculate the accumulated percentage.
# Accumulated interest is a new column in this table, which should be called
# 'accumulated_percent_profit_product_of_warehouse'. # At its core, this is
# an ever-increasing sum of the 'percent_profit_product_of_warehouse' column
# sorted in descending order.

warehouse_profit = warehouse_profit.sort_values(
    by=["warehouse_name", "percent_profit_product_of_warehouse"],
    ascending=[True, False],
)

warehouse_profit[
    "accumulated_percent_profit_product_of_warehouse"
] = warehouse_profit.groupby("warehouse_name")[
    "percent_profit_product_of_warehouse"
].cumsum()

print(warehouse_profit)

# Task 6.
# Assign A,B,C categories based on the value of the accumulated percentage.
# If the value of the accumulated interest is less than or equal to 70,
# then category A. # If from 70 to 90 (including 90), then category B.
# The rest - category C. Designate the new column in the table as 'category'.


def assign_category(accumulated_percent: float) -> str:
    if accumulated_percent <= 70:
        return "A"
    elif accumulated_percent <= 90:
        return "B"
    else:
        return "C"


warehouse_profit["category"] = warehouse_profit[
    "accumulated_percent_profit_product_of_warehouse"
].apply(assign_category)

print(warehouse_profit)
