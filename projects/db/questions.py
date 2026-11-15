# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo[sql]",
#     "duckdb",
#     "polars",
#     "altair",
# ]
# ///
"""Answers business questions for the Babson Bean Café database.
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
    # Babson Bean Café Database — Part B: The Questions

    This notebook asks `database.duckdb`, built by `build.py`, eight business questions and checks that the numbers are right.
    """)
    return


@app.cell
def _(duckdb, mo):
    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return (ask,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `as_of`: every "last 30 days" and "last month" counts back from this date.
    """)
    return


@app.cell
def _(date):
    as_of = date(2026, 11, 8)
    return (as_of,)


@app.cell
def _():
    from datetime import date

    return (date,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 1. The three best-selling products last month, by units.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 2. Revenue, cost and margin by menu category, options' earnings included under the category of the product on their line. (three tables or more)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 3. For each member: the number of orders, the total spent and the average order, keeping the members whose total spent is above the members' average. (three tables or more)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 4. Every order's payments checked against its total, and a list of the orders where they do not match. (three tables or more) (checks a rule)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 5. The members who joined and have never ordered.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 6. The share of orders paid at least partly with points, for each month.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 7. The products, available today or not, that have not sold in the last 60 days.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 8. Which product sold the most units on weekends?

    My own question. Uses `orders`, `order_lines` and `products` — three tables.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. How I Know These Numbers Are Right
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Working With the Agent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Reading It Back

    **Question picked:** Question 8, "Which product sold the most units on weekends?" I'm using this one because its join is easy to reason about: every order line belongs to exactly one order and references exactly one product, so the join is one-to-one on both sides, row for row.

    **Prediction, committed before running the joins:** I predict that joining `order_lines` to `orders` and `products` will produce 1,988 rows before filtering or grouping, because each order line belongs to exactly one order and references exactly one product.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Going Further
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Time Spent
    """)
    return


if __name__ == "__main__":
    app.run()
