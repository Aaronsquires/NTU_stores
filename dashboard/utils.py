from datetime import date, timedelta


def string_to_date_interval(string):
    end = date.today()

    if string == 'day':
        start = end
    elif string == 'week':
        start = end - timedelta(weeks=1)
    elif string == 'month':
        start = end - timedelta(days=30.4375)
    elif string == 'three_months':
        start = end - 3 * timedelta(days=30.4375)
    elif string == 'six_months':
        start = end - 6 * timedelta(days=30.4375)
    elif string == 'year':
        start = end - timedelta(days=365)
    else:
        start = False

    return start, end
