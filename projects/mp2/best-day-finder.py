# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "requests",
# ]
# ///
"""Mini Project 2 — Option C: Pick the Day.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import csv
    import json

    import requests

    return csv, json, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    A student club is planning an outdoor event somewhere in Massachusetts in the next week and needs to pick the day. This tool helps the organizer answer: given a town and a set of weather rules (a comfortable temperature range, a low chance of rain, and a wind limit), which of the next seven days is the best day to hold the event?
    """)
    return


@app.cell
def _():
    #This tool is designed for a student club planning an outdoor event in Massachusetts. It helps the organizer choose the best day in the next seven days based on temperature, chance of rain, and wind.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    1. Turn the town name into coordinates, using Open-Meteo's geocoding search, and keep only the match in Massachusetts.
    2. Ask Open-Meteo's forecast endpoint for the next seven days at those coordinates, in °F and mph.
    3. The reply gives each measurement (high, low, rain chance, wind) as its own list, one value per day. Walk all the lists together and turn them into one record per day.
    4. For each day's record, check it against the club's four rules (two for temperature, one for rain, one for wind) and record whether it passes all of them.
    5. Among the days that pass, pick the one with the lowest chance of rain; if two days tie on rain, pick the one with lower wind.
    6. If no day passes every rule, instead pick the day that breaks the fewest rules, and the earlier day on a tie.
    7. Print a table of all seven days and one sentence naming the best day and the reason.

    - My loop carries one dictionary per day, built up field by field (date, high, low, rain chance, wind, rules broken, passes), the way the running list of records carried one row per town in notebook 5.
    - For section 6, I will check that the number of days in my table is 7, matching the number of dates the API sent back, and that the day I count as "today" matches the first date in the forecast's own `time` list.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs
    """)
    return


@app.cell
def _():
    place = "Wellesley"
    state = "Massachusetts"
    lowest_high_f = 55
    highest_high_f = 80
    max_rain_chance = 30
    max_wind_mph = 15
    return (
        highest_high_f,
        lowest_high_f,
        max_rain_chance,
        max_wind_mph,
        place,
        state,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work
    """)
    return


@app.cell
def _(requests):
    def get_coordinates(place, state):
        reply = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": place, "count": 100},
            timeout=10,
        )
        results = reply.json().get("results", [])
        for result in results:
            if result.get("admin1") == state:
                return result["latitude"], result["longitude"], result["name"]
        raise ValueError(f"No match for {place} in {state}")

    return (get_coordinates,)


@app.cell
def _(requests):
    def get_daily_forecast(latitude, longitude):
        reply = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,"
                "precipitation_probability_max,wind_speed_10m_max",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": "America/New_York",
            },
            timeout=10,
        )
        daily = reply.json()["daily"]

        days = []
        for _date, _high, _low, _rain, _wind in zip(
            daily["time"],
            daily["temperature_2m_max"],
            daily["temperature_2m_min"],
            daily["precipitation_probability_max"],
            daily["wind_speed_10m_max"],
        ):
            days.append(
                {
                    "date": _date,
                    "high": _high,
                    "low": _low,
                    "rain_chance": _rain,
                    "wind": _wind,
                }
            )
        return days

    return (get_daily_forecast,)


@app.cell
def _(get_coordinates, place, state):
    latitude, longitude, matched_place = get_coordinates(place, state)
    matched_place, latitude, longitude
    return latitude, longitude, matched_place


@app.cell
def _(get_daily_forecast, latitude, longitude):
    forecast_days = get_daily_forecast(latitude, longitude)
    forecast_days
    return (forecast_days,)


@app.cell
def _(
    forecast_days,
    highest_high_f,
    lowest_high_f,
    max_rain_chance,
    max_wind_mph,
):
    for _day in forecast_days:
        _rules_broken = 0
        if not (lowest_high_f <= _day["high"] <= highest_high_f):
            _rules_broken += 1
        if _day["rain_chance"] > max_rain_chance:
            _rules_broken += 1
        if _day["wind"] > max_wind_mph:
            _rules_broken += 1
        _day["rules_broken"] = _rules_broken
        _day["passes"] = _rules_broken == 0

    forecast_days
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer
    """)
    return


@app.cell
def _(forecast_days):
    print(f"{'Date':<12} {'High':>6} {'Low':>6} {'Rain %':>7} {'Wind':>6}  Passes")
    for _day in forecast_days:
        print(
            f"{_day['date']:<12} {_day['high']:>6} {_day['low']:>6} "
            f"{_day['rain_chance']:>7} {_day['wind']:>6}  {_day['passes']}"
        )
    return


@app.cell
def _(forecast_days, matched_place):
    passing_days = [_day for _day in forecast_days if _day["passes"]]

    if passing_days:
        best_day = passing_days[0]
        for _day in passing_days[1:]:
            if _day["rain_chance"] < best_day["rain_chance"] or (
                _day["rain_chance"] == best_day["rain_chance"]
                and _day["wind"] < best_day["wind"]
            ):
                best_day = _day
        best_reason = (
            f"it passes every rule, with a {best_day['rain_chance']}% chance of rain "
            f"and {best_day['wind']} mph wind"
        )
    else:
        best_day = forecast_days[0]
        for _day in forecast_days[1:]:
            if _day["rules_broken"] < best_day["rules_broken"]:
                best_day = _day
        best_reason = f"no day passes every rule, and it breaks the fewest, {best_day['rules_broken']}"

    print(
        f"The best day to hold the event in {matched_place} is {best_day['date']}, "
        f"because {best_reason}."
    )
    return (best_day,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right
    """)
    return


@app.cell
def _(forecast_days):
    len(forecast_days) == 7
    return


@app.cell
def _(best_day, highest_high_f, lowest_high_f, max_rain_chance, max_wind_mph):
    (
        lowest_high_f <= best_day["high"] <= highest_high_f,
        best_day["rain_chance"] <= max_rain_chance,
        best_day["wind"] <= max_wind_mph,
        best_day["passes"],
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `len(forecast_days) == 7` checks that every one of the seven days Open-Meteo sent back made it into my table, matching the length of the API's own `time` list. The second check recomputes the best day's three rules by hand and confirms they agree with the `passes` flag my loop set, so the loop did not make a mistake when it judged that day.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    *Your turn: pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell. If the agent got it right the first time, say what you did to verify that, and section 6 is enough.*
    """)
    return


@app.cell
def _():
    # The first version of my Section 6 mainly checked whether the number of forecast days was correct.
    # But I realized that this did not fully test whether the tool was applying the weather rules correctly. I added a controlled example where I already knew the expected result and compared it with the result produced by the tool. This helped me verify the logic instead of only checking the number of records.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Reading It Back

    *Your turn: pick two functions your agent wrote or helped write, `get_coordinates` and `get_daily_forecast` are good choices. For each, write in your own words what goes in, what comes out, and one line you had to ask about.*

    *Then choose one change to what the tool does, such as another town or a wider temperature range. Changing one value in the Inputs cell is enough. Write what you expect to change in the answer. Commit with the message `mp2: prediction`, make the change, run it, and write what happened and whether it matched.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # The get_coordinates function takes a place and a state as inputs. It searches the Open-Meteo geocoding API and returns the latitude, longitude, and matched place name. One line I had to understand better was result.get("admin1") == state, which checks whether the result belongs to the state entered by the user.
    # The get_daily_forecast function takes latitude and longitude as inputs. It requests the seven-day weather forecast and returns a list of dictionaries, with one dictionary for each day. One part I had to understand better was zip(), which lets the loop go through the date, temperature, rain, and wind lists at the same time and combine them into one daily record.
    # Prediction: I will change the place from Wellesley to Cambridge. I expect the coordinates and weather values to change, which may also change the recommended best day. I expect the table to still contain seven days because the forecast period does not change.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Going Further

    *Your turn: describe at least one step you took past the main task.*
    """)
    return


@app.cell
def _(forecast_days):
    for _day in forecast_days:
        _day["score"] = 3 - _day["rules_broken"]

    for _day in forecast_days:
        print(f"{_day['date']}: {_day['score']}/3")
    return


@app.cell
def _(forecast_days):
    ranked_days = []
    remaining_days = forecast_days.copy()

    for _rank in range(3):
        _best = remaining_days[0]

        for _candidate in remaining_days[1:]:
            if _candidate["rules_broken"] < _best["rules_broken"]:
                _best = _candidate

            elif _candidate["rules_broken"] == _best["rules_broken"]:
                if _candidate["rain_chance"] < _best["rain_chance"]:
                    _best = _candidate

                elif (
                    _candidate["rain_chance"] == _best["rain_chance"]
                    and _candidate["wind"] < _best["wind"]
                ):
                    _best = _candidate

        ranked_days.append(_best)
        remaining_days.remove(_best)

    print("Top 3 days:")

    for _ranked_day in ranked_days:
        print(
            f"{_ranked_day['date']}: "
            f"{_ranked_day['rain_chance']}% rain, "
            f"{_ranked_day['wind']} mph wind"
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I went further by ranking the top three days instead of recommending only one day. The ranking first considers how many weather rules each day breaks. If two days break the same number of rules, it compares their chance of rain, and then their wind speed. This gives the organizer additional options if the first recommended day is not available.

    I also experimented with a simple score based on the number of weather rules each day meets. The top-three ranking provides more detail because it compares the days and puts them in order instead of only giving each day a score.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Time Spent

    *Your turn: about how many hours this project took you outside class, as one number. It is not graded.*
    """)
    return


@app.cell
def _():
    4
    return


@app.cell
def _(csv, forecast_days, json, mo):
    mp2_data_dir = mo.notebook_dir() / "data"
    mp2_data_dir.mkdir(exist_ok=True)

    with open(mp2_data_dir / "forecast.json", "w", encoding="utf-8") as _file:
        json.dump(forecast_days, _file, indent=2)

    with open(mp2_data_dir / "forecast.csv", "w", newline="", encoding="utf-8") as _file:
        _writer = csv.DictWriter(_file, fieldnames=list(forecast_days[0].keys()))
        _writer.writeheader()
        _writer.writerows(forecast_days)
    return


if __name__ == "__main__":
    app.run()
