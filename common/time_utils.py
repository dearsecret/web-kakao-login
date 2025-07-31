from django.utils.timezone import is_naive, make_aware
from psycopg2.extras import DateTimeTZRange , DateRange
from datetime import datetime, time, timedelta, date

def make_aware_if_needed(dt):
    if dt is None:
        return None
    return make_aware(dt) if is_naive(dt) else dt


def create_aware_range(start, end):
    return DateTimeTZRange(
        make_aware_if_needed(start),
        make_aware_if_needed(end)
    )


get_noon_range = lambda: (
    DateTimeTZRange(
        *(lambda now=datetime.now(): 
            (datetime.combine(now.date(), time(12)) if now.time() >= time(12) 
                else datetime.combine(now.date() - timedelta(days=1), time(12)),
             datetime.combine(now.date() + timedelta(days=1), time(12)) if now.time() >= time(12)
                else datetime.combine(now.date(), time(12)))
        )()
    , '[)')
)

get_month_range = lambda: (
    DateRange(
        lower=date.today().replace(day=1),
        upper=(date.today().replace(day=1).replace(month=((date.today().month % 12) + 1)) - timedelta(days=1)),
        bounds='[]'  # 포함, 포함
    )
)