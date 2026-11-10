# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo[sql]",
#     "duckdb",
#     "polars",
#     "altair",
# ]
# ///
"""Builds the Babson Bean Café database.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import altair as alt
    import duckdb
    import polars as pl

    return alt, duckdb, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Babson Bean Café Database — Part A: The Build

    This notebook builds `database.duckdb` from nothing every time it runs, from the CSV files in `data/` that `make_data.py` wrote.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Tables

    Seven tables, one `CREATE TABLE` each, with every key and rule from the README's ERD declared.
    """)
    return


@app.cell
def _(mo, pl):
    _data_folder = mo.notebook_dir() / "data"
    members_rows = pl.read_csv(_data_folder / "members.csv", null_values=[""])
    products_rows = pl.read_csv(_data_folder / "products.csv")
    options_rows = pl.read_csv(_data_folder / "options.csv")
    orders_rows = pl.read_csv(_data_folder / "orders.csv", null_values=[""])
    order_lines_rows = pl.read_csv(_data_folder / "order_lines.csv")
    order_line_options_rows = pl.read_csv(_data_folder / "order_line_options.csv")
    payments_rows = pl.read_csv(_data_folder / "payments.csv")
    return (
        members_rows,
        options_rows,
        order_line_options_rows,
        order_lines_rows,
        orders_rows,
        payments_rows,
        products_rows,
    )


@app.cell
def _(
    duckdb,
    members_rows,
    mo,
    options_rows,
    order_line_options_rows,
    order_lines_rows,
    orders_rows,
    payments_rows,
    products_rows,
):
    _file = mo.notebook_dir() / "database.duckdb"
    _file.unlink(missing_ok=True)

    with duckdb.connect(_file) as _con:
        _con.execute("""
            CREATE TABLE members (
                member_id      INTEGER PRIMARY KEY,
                first_name     VARCHAR NOT NULL,
                mobile_number  VARCHAR NOT NULL,
                email          VARCHAR,
                join_date      DATE NOT NULL,
                points_balance INTEGER NOT NULL CHECK (points_balance >= 0)
            )
        """)
        _con.execute("""
            CREATE TABLE products (
                product_id   INTEGER PRIMARY KEY,
                name         VARCHAR NOT NULL,
                category     VARCHAR NOT NULL CHECK (category IN ('coffee', 'tea', 'food', 'other')),
                price        DECIMAL(10,2) NOT NULL CHECK (price > 0),
                cost         DECIMAL(10,2) NOT NULL CHECK (cost >= 0),
                is_available BOOLEAN NOT NULL,
                CHECK (price >= cost)
            )
        """)
        _con.execute("""
            CREATE TABLE options (
                option_id INTEGER PRIMARY KEY,
                name      VARCHAR NOT NULL,
                price     DECIMAL(10,2) NOT NULL CHECK (price >= 0),
                cost      DECIMAL(10,2) NOT NULL CHECK (cost >= 0)
            )
        """)
        _con.execute("""
            CREATE TABLE orders (
                order_id   INTEGER PRIMARY KEY,
                member_id  INTEGER REFERENCES members(member_id),
                ordered_at TIMESTAMP NOT NULL,
                channel    VARCHAR NOT NULL CHECK (channel IN ('counter', 'app'))
            )
        """)
        _con.execute("""
            CREATE TABLE order_lines (
                order_line_id INTEGER PRIMARY KEY,
                order_id      INTEGER NOT NULL REFERENCES orders(order_id),
                product_id    INTEGER NOT NULL REFERENCES products(product_id),
                quantity      INTEGER NOT NULL CHECK (quantity > 0),
                price_charged DECIMAL(10,2) NOT NULL CHECK (price_charged >= 0)
            )
        """)
        _con.execute("""
            CREATE TABLE order_line_options (
                order_line_id INTEGER NOT NULL REFERENCES order_lines(order_line_id),
                option_id     INTEGER NOT NULL REFERENCES options(option_id),
                price_charged DECIMAL(10,2) NOT NULL CHECK (price_charged >= 0),
                PRIMARY KEY (order_line_id, option_id)
            )
        """)
        _con.execute("""
            CREATE TABLE payments (
                payment_id INTEGER PRIMARY KEY,
                order_id   INTEGER NOT NULL REFERENCES orders(order_id),
                method     VARCHAR NOT NULL CHECK (method IN ('cash', 'card', 'app', 'points')),
                amount     DECIMAL(10,2) NOT NULL CHECK (amount > 0)
            )
        """)

        _con.execute("INSERT INTO members SELECT * FROM members_rows")
        _con.execute("INSERT INTO products SELECT * FROM products_rows")
        _con.execute("INSERT INTO options SELECT * FROM options_rows")
        _con.execute("INSERT INTO orders SELECT * FROM orders_rows")
        _con.execute("INSERT INTO order_lines SELECT * FROM order_lines_rows")
        _con.execute("INSERT INTO order_line_options SELECT * FROM order_line_options_rows")
        _con.execute("INSERT INTO payments SELECT * FROM payments_rows")

        _con.execute("""
            CREATE VIEW weekly_revenue AS
                SELECT
                    date_trunc('week', o.ordered_at) AS week,
                    count(DISTINCT o.order_id)       AS orders,
                    sum(ol.price_charged * ol.quantity) AS lines_revenue_dollars
                FROM orders o
                JOIN order_lines ol ON ol.order_id = o.order_id
                GROUP BY week
        """)

    database = _file
    database.name
    return (database,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Every other cell asks through `ask`.** It opens the file only to read, runs one query, hands back the result as a table, and closes the file again.
    """)
    return


@app.cell
def _(database, duckdb):
    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return (ask,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. The Data

    `make_data.py` wrote the CSV files above, following every rule of the scenario, with one exception written down here: two orders' payments do not add up to the order's total, on purpose, for the question that checks that rule in Part B.

    - Order 2: its payments add up to **$5.00 less** than its lines and options.
    - Order 3: its payments add up to **$3.50 more** than its lines and options.

    Two other rows were left out on purpose, for the questions about things with nothing attached: the last 5 members (`member_id` 46–50) never placed an order, and the last product (`product_id` 20) was not sold in the 60 days before `as_of`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. A Look at the Data
    """)
    return


@app.cell
def _(alt, mo, orders_rows, pl):
    _weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    orders_by_weekday = (
        orders_rows
        .with_columns(pl.col("ordered_at").str.to_datetime().dt.strftime("%A").alias("weekday"))
        .group_by("weekday")
        .agg(pl.len().alias("orders"))
    )

    orders_by_weekday_chart = mo.ui.altair_chart(
        orders_by_weekday.plot.bar(
            x=alt.X("weekday", sort=_weekday_order, title="Day of the week"),
            y=alt.Y("orders", title="Number of orders"),
        ).properties(title="Orders by day of the week")
    )
    orders_by_weekday_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A real café sees fewer orders on weekends, when fewer students and staff are on campus; this generated data spreads orders evenly across every day instead, because `make_data.py` picks the order date uniformly at random without weighting it toward weekdays.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Row Counts
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT 'members' AS table_name, count(*) AS rows FROM members
        UNION ALL SELECT 'products', count(*) FROM products
        UNION ALL SELECT 'options', count(*) FROM options
        UNION ALL SELECT 'orders', count(*) FROM orders
        UNION ALL SELECT 'order_lines', count(*) FROM order_lines
        UNION ALL SELECT 'order_line_options', count(*) FROM order_line_options
        UNION ALL SELECT 'payments', count(*) FROM payments
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. A Row It Refuses

    The menu rule says a product's price is never below its cost. Here is an insert that breaks it.
    """)
    return


@app.cell
def _(database, duckdb):
    try:
        with duckdb.connect(database) as _con:
            _con.execute(
                "INSERT INTO products VALUES (9999, 'Underpriced Latte', 'coffee', 1.00, 2.50, true)"
            )
        refused_insert = "accepted"
    except duckdb.ConstraintException as _error:
        refused_insert = str(_error).splitlines()[0]

    refused_insert
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Answers You Already Knew

    Three counts `make_data.py` printed when it wrote the files, asked back from the database.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Expected: 50 members.*
    """)
    return


@app.cell
def _(ask):
    ask("SELECT count(*) FROM members")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Expected: 20 products.*
    """)
    return


@app.cell
def _(ask):
    ask("SELECT count(*) FROM products")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Expected: 8 options.*
    """)
    return


@app.cell
def _(ask):
    ask("SELECT count(*) FROM options")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. A View

    `weekly_revenue`, saved in the cell that builds the database, answers a question the café would ask every week: how many orders, and how much revenue from lines alone, in each calendar week.
    """)
    return


@app.cell
def _(ask):
    ask("SELECT * FROM weekly_revenue ORDER BY week DESC")
    return


if __name__ == "__main__":
    app.run()
