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

    return alt, duckdb


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

    "Last month" is the last full calendar month before `as_of`: October 2026.
    """)
    return


@app.cell
def _(as_of, ask):
    q1_result = ask(f"""
        SELECT p.name, sum(ol.quantity) AS units_sold
        FROM order_lines ol
        JOIN orders o ON o.order_id = ol.order_id
        JOIN products p ON p.product_id = ol.product_id
        WHERE o.ordered_at >= date_trunc('month', DATE '{as_of}') - INTERVAL 1 MONTH
          AND o.ordered_at <  date_trunc('month', DATE '{as_of}')
        GROUP BY p.name
        ORDER BY units_sold DESC
        LIMIT 3
    """)
    q1_result
    return (q1_result,)


@app.cell
def _(q1_result):
    print(
        f"Last month, the three best-selling products by units were "
        f"{q1_result['name'][0]} ({q1_result['units_sold'][0]} units), "
        f"{q1_result['name'][1]} ({q1_result['units_sold'][1]} units), and "
        f"{q1_result['name'][2]} ({q1_result['units_sold'][2]} units)."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 2. Revenue, cost and margin by menu category, options' earnings included under the category of the product on their line. (three tables or more)

    An option has no category of its own, so its revenue and cost have to be assigned through the order line it rode on: `order_line_options` joined to `order_lines` joined to `products` gives each option the category of the product it was added to. A `UNION ALL` of that with the lines' own revenue and cost gives one row per category combining both.
    """)
    return


@app.cell
def _(ask):
    q2_result = ask("""
        WITH revenue_by_category AS (
            SELECT p.category,
                   sum(ol.price_charged * ol.quantity) AS amount_revenue,
                   sum(p.cost * ol.quantity)            AS amount_cost
            FROM order_lines ol
            JOIN products p ON p.product_id = ol.product_id
            GROUP BY p.category

            UNION ALL

            SELECT p.category,
                   sum(olo.price_charged * ol.quantity) AS amount_revenue,
                   sum(opt.cost * ol.quantity)          AS amount_cost
            FROM order_line_options olo
            JOIN order_lines ol ON ol.order_line_id = olo.order_line_id
            JOIN products p ON p.product_id = ol.product_id
            JOIN options opt ON opt.option_id = olo.option_id
            GROUP BY p.category
        )
        SELECT
            category,
            sum(amount_revenue) AS revenue,
            sum(amount_cost)    AS cost,
            sum(amount_revenue) - sum(amount_cost) AS margin
        FROM revenue_by_category
        GROUP BY category
        ORDER BY revenue DESC
    """)
    q2_result
    return (q2_result,)


@app.cell
def _(q2_result):
    print(
        f"By revenue, {q2_result['category'][0]} is the top category at "
        f"${q2_result['revenue'][0]:.2f}, with a margin of ${q2_result['margin'][0]:.2f}; "
        f"the smallest category is {q2_result['category'][-1]} at ${q2_result['revenue'][-1]:.2f} revenue."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 3. For each member: the number of orders, the total spent and the average order, keeping the members whose total spent is above the members' average. (three tables or more)
    """)
    return


@app.cell
def _(ask):
    q3_result = ask("""
        WITH order_amounts AS (
            SELECT order_id, sum(price_charged * quantity) AS amount
            FROM order_lines
            GROUP BY order_id

            UNION ALL

            SELECT ol.order_id, sum(olo.price_charged * ol.quantity) AS amount
            FROM order_line_options olo
            JOIN order_lines ol ON ol.order_line_id = olo.order_line_id
            GROUP BY ol.order_id
        ),
        order_totals AS (
            SELECT o.member_id, oa.order_id, sum(oa.amount) AS order_total
            FROM order_amounts oa
            JOIN orders o ON o.order_id = oa.order_id
            GROUP BY o.member_id, oa.order_id
        ),
        member_totals AS (
            SELECT member_id,
                   count(*)         AS order_count,
                   sum(order_total) AS total_spent,
                   avg(order_total) AS average_order
            FROM order_totals
            WHERE member_id IS NOT NULL
            GROUP BY member_id
        )
        SELECT m.member_id, m.first_name, mt.order_count, mt.total_spent, mt.average_order
        FROM member_totals mt
        JOIN members m ON m.member_id = mt.member_id
        WHERE mt.total_spent > (SELECT avg(total_spent) FROM member_totals)
        ORDER BY mt.total_spent DESC
    """)
    q3_result
    return (q3_result,)


@app.cell
def _(q3_result):
    print(
        f"{len(q3_result)} members spent above the members' average. "
        f"The top spender is {q3_result['first_name'][0]} (member {q3_result['member_id'][0]}), "
        f"with {q3_result['order_count'][0]} orders totalling ${q3_result['total_spent'][0]:.2f}, "
        f"an average order of ${q3_result['average_order'][0]:.2f}."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 4. Every order's payments checked against its total, and a list of the orders where they do not match. (three tables or more) (checks a rule)

    `make_data.py` broke this rule on purpose in exactly two orders (see `build.py` section 2): order 2 is $5.00 short, order 3 is $3.50 over. This query should find exactly those two.
    """)
    return


@app.cell
def _(ask):
    q4_result = ask("""
        WITH order_amounts AS (
            SELECT order_id, sum(price_charged * quantity) AS amount
            FROM order_lines
            GROUP BY order_id

            UNION ALL

            SELECT ol.order_id, sum(olo.price_charged * ol.quantity) AS amount
            FROM order_line_options olo
            JOIN order_lines ol ON ol.order_line_id = olo.order_line_id
            GROUP BY ol.order_id
        ),
        order_totals AS (
            SELECT order_id, sum(amount) AS lines_and_options_total
            FROM order_amounts
            GROUP BY order_id
        ),
        payment_totals AS (
            SELECT order_id, sum(amount) AS payments_total
            FROM payments
            GROUP BY order_id
        )
        SELECT
            ot.order_id,
            ot.lines_and_options_total,
            pt.payments_total,
            pt.payments_total - ot.lines_and_options_total AS difference
        FROM order_totals ot
        JOIN payment_totals pt ON pt.order_id = ot.order_id
        WHERE pt.payments_total <> ot.lines_and_options_total
        ORDER BY ot.order_id
    """)
    q4_result
    return (q4_result,)


@app.cell
def _(q4_result):
    _mismatch_list = ", ".join(
        f"order {row['order_id']} (off by ${row['difference']:.2f})"
        for row in q4_result.iter_rows(named=True)
    )
    print(f"{len(q4_result)} orders' payments do not match their total: {_mismatch_list}.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 5. The members who joined and have never ordered.
    """)
    return


@app.cell
def _(ask):
    q5_result = ask("""
        SELECT m.member_id, m.first_name, m.join_date
        FROM members m
        LEFT JOIN orders o ON o.member_id = m.member_id
        WHERE o.order_id IS NULL
        ORDER BY m.member_id
    """)
    q5_result
    return (q5_result,)


@app.cell
def _(q5_result):
    print(f"{len(q5_result)} members joined and have never placed an order: member ids {list(q5_result['member_id'])}.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 6. The share of orders paid at least partly with points, for each month.
    """)
    return


@app.cell
def _(ask):
    q6_result = ask("""
        WITH orders_by_month AS (
            SELECT order_id, date_trunc('month', ordered_at) AS month
            FROM orders
        ),
        points_orders AS (
            SELECT DISTINCT order_id
            FROM payments
            WHERE method = 'points'
        )
        SELECT
            om.month,
            count(*)                                        AS orders,
            count(po.order_id)                               AS orders_with_points,
            count(po.order_id) * 1.0 / count(*)              AS share_with_points
        FROM orders_by_month om
        LEFT JOIN points_orders po ON po.order_id = om.order_id
        GROUP BY om.month
        ORDER BY om.month
    """)
    q6_result
    return (q6_result,)


@app.cell
def _(q6_result):
    _best = q6_result.sort("share_with_points", descending=True).row(0, named=True)
    print(
        f"The share of orders paid at least partly with points ranges from "
        f"{q6_result['share_with_points'].min():.0%} to {q6_result['share_with_points'].max():.0%} across months; "
        f"the highest was {_best['month'].strftime('%B %Y')} at {_best['share_with_points']:.0%}."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 7. The products, available today or not, that have not sold in the last 60 days.
    """)
    return


@app.cell
def _(as_of, ask):
    q7_result = ask(f"""
        SELECT p.product_id, p.name, p.is_available
        FROM products p
        WHERE p.product_id NOT IN (
            SELECT ol.product_id
            FROM order_lines ol
            JOIN orders o ON o.order_id = ol.order_id
            WHERE o.ordered_at >= DATE '{as_of}' - INTERVAL 60 DAY
        )
        ORDER BY p.product_id
    """)
    q7_result
    return (q7_result,)


@app.cell
def _(q7_result):
    _names = ", ".join(q7_result["name"])
    print(f"{len(q7_result)} product(s) have not sold in the last 60 days: {_names}.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Question 8. Which product sold the most units on weekends?

    My own question. Uses `orders`, `order_lines` and `products` — three tables. This is also the question for "Reading It Back" below: first the raw join, with no filtering or grouping, to check the prediction committed as `db: prediction`.
    """)
    return


@app.cell
def _(ask):
    q8_raw_join = ask("""
        SELECT ol.order_line_id, o.order_id, p.product_id
        FROM order_lines ol
        JOIN orders o ON o.order_id = ol.order_id
        JOIN products p ON p.product_id = ol.product_id
    """)
    q8_join_row_count = len(q8_raw_join)
    q8_join_row_count
    return (q8_join_row_count,)


@app.cell
def _(q8_join_row_count):
    q8_prediction = 1988
    q8_prediction_correct = q8_join_row_count == q8_prediction
    print(
        f"Predicted {q8_prediction} rows; the raw join actually produced {q8_join_row_count} rows. "
        f"Prediction was {'correct' if q8_prediction_correct else 'not correct'}."
    )
    return (q8_prediction_correct,)


@app.cell
def _(ask):
    q8_result = ask("""
        SELECT p.name, sum(ol.quantity) AS units_sold
        FROM order_lines ol
        JOIN orders o ON o.order_id = ol.order_id
        JOIN products p ON p.product_id = ol.product_id
        WHERE dayofweek(o.ordered_at) IN (0, 6)
        GROUP BY p.name
        ORDER BY units_sold DESC
        LIMIT 5
    """)
    q8_result
    return (q8_result,)


@app.cell
def _(q8_result):
    print(
        f"On weekends, {q8_result['name'][0]} sold the most units, with "
        f"{q8_result['units_sold'][0]} units sold."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. How I Know These Numbers Are Right

    Two of the answers above, checked a second way.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Check 1 — Question 2's total revenue, a different way.** Question 2 adds up revenue by category after a `UNION ALL` of lines and options. Here, the same total is computed directly, from `order_lines` and `order_line_options` alone, with no category grouping at all.
    """)
    return


@app.cell
def _(ask, q2_result):
    check1_from_q2 = q2_result["revenue"].sum()
    check1_direct = ask("""
        SELECT
            (SELECT sum(price_charged * quantity) FROM order_lines)
          + (SELECT sum(olo.price_charged * ol.quantity)
             FROM order_line_options olo
             JOIN order_lines ol ON ol.order_line_id = olo.order_line_id)
          AS total_revenue
    """)["total_revenue"][0]
    print(
        f"Question 2's categories sum to ${check1_from_q2:.2f}; "
        f"computed directly with no grouping, the total is ${check1_direct:.2f}. "
        f"{'They agree.' if round(float(check1_from_q2), 2) == round(float(check1_direct), 2) else 'They do NOT agree.'}"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Check 2 — Question 5's member count, a different way.** Question 5 uses a `LEFT JOIN ... WHERE ... IS NULL` to find members with no orders. Here, the same count is found with `NOT IN` on a subquery instead, a different way of asking for the same thing.
    """)
    return


@app.cell
def _(ask, q5_result):
    check2_from_q5 = len(q5_result)
    check2_not_in = ask("""
        SELECT count(*) AS never_ordered_count
        FROM members
        WHERE member_id NOT IN (SELECT member_id FROM orders WHERE member_id IS NOT NULL)
    """)["never_ordered_count"][0]
    print(
        f"Question 5's LEFT JOIN finds {check2_from_q5} members with no orders; "
        f"the NOT IN subquery finds {check2_not_in}. "
        f"{'They agree.' if check2_from_q5 == check2_not_in else 'They do NOT agree.'}"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Working With the Agent

    For Question 2, the agent's first approach did not correctly assign option revenue and cost to a menu category because the `options` table does not have a category field. I checked the database structure and saw that the category comes from the product associated with the order line. We changed the query so that each option uses the category of its related product. I then checked the result by comparing the total category revenue with the total revenue calculated separately, and both were $13,371.96.
    """)
    return


@app.cell(hide_code=True)
def _(mo, q8_join_row_count, q8_prediction_correct):
    mo.md(f"""
    ## 3. Reading It Back

    **Question picked:** Question 8, "Which product sold the most units on weekends?" I'm using this one because its join is easy to reason about: every order line belongs to exactly one order and references exactly one product, so the join is one-to-one on both sides, row for row.

    **Prediction, committed before running the joins (`db: prediction`):** I predict that joining `order_lines` to `orders` and `products` will produce 1,988 rows before filtering or grouping, because each order line belongs to exactly one order and references exactly one product.

    **Actual joined row count:** {q8_join_row_count}. The prediction was **{"correct" if q8_prediction_correct else "not correct"}**.

    **What one row of the final Question 8 result means:** one row is one product and how many units of it were bought on Saturdays or Sundays in total, added up across every weekend order line in the whole year of data — for example, the top row means that one product was the single biggest weekend seller, counted in units, not dollars.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Going Further

    A chart of Question 6's monthly share, reusing the same calculation, no new metric.
    """)
    return


@app.cell
def _(alt, mo, q6_result):
    going_further_chart = mo.ui.altair_chart(
        q6_result.plot.line(
            x=alt.X("month", title="Month", axis=alt.Axis(format="%b %Y", labelAngle=-45)),
            y=alt.Y("share_with_points", title="Share of orders paid with points", axis=alt.Axis(format="%")),
        ).properties(title="Share of orders paid at least partly with points, by month")
    )
    going_further_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I tried charting Question 6's monthly share of points-paid orders instead of just reading the table. The chart makes it easier to see the month-to-month ups and downs at a glance, and whether the share is trending up, down, or just bouncing around, which is harder to judge from a column of percentages.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Time Spent

    Time spent on Part B outside class: 2 hours
    """)
    return


if __name__ == "__main__":
    app.run()
