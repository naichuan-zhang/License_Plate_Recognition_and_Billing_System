import datetime


def get_parking_time(start_t, end_t):
    start = datetime.datetime.strptime(start_t, "%Y-%m-%d %H:%M")
    end = datetime.datetime.strptime(end_t, "%Y-%m-%d %H:%M")
    delta = end - start
    y = round(delta.total_seconds() / 60 / 60)
    if y == 0:
        y = 1
    return y


def get_week_number(date):
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
    day = date.weekday()
    return day
