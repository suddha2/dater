"""Parsers and serializers for /widgets API endpoints."""
import re
from datetime import date, datetime, time, timezone
from flask_restx.inputs import positive, URL
from dateutil import parser
from flask_restx import Model
from flask_restx.fields import Boolean, DateTime, Integer, List, Nested, String, Url
from flask_restx.inputs import URL
from flask_restx.reqparse import RequestParser

from src.util.datetime_util import make_tzaware, DATE_MONTH_NAME

pagination_reqparser = RequestParser(bundle_errors=True)
pagination_reqparser.add_argument("page", type=positive, required=False, default=1)
pagination_reqparser.add_argument(
    "per_page", type=positive, required=False, choices=[5, 10, 25, 50, 100], default=10
)

def widget_name(name):
    """Validation method for a string containing only letters, numbers, '-' and '_'."""
    if not re.compile(r"^[\w-]+$").match(name):
        raise ValueError(
            f"'{name}' contains one or more invalid characters. Widget name must "
            "contain only letters, numbers, hyphen and underscore characters."
        )
    return name


def future_date_from_string(date_str):
    """Validation method for a date in the future, formatted as a string."""
    try:
        parsed_date = parser.parse(date_str)
    except ValueError:
        raise ValueError(
            f"Failed to parse '{date_str}' as a valid date. You can use any format "
            "recognized by dateutil.parser. For example, all of the strings below "
            "are valid ways to represent the same date: '2018-5-13' -or- '05/13/2018' "
            "-or- 'May 13 2018'."
        )

    if parsed_date.date() < date.today():
        raise ValueError(
            f"Successfully parsed {date_str} as "
            f"{parsed_date.strftime(DATE_MONTH_NAME)}. However, this value must be a "
            f"date in the future and {parsed_date.strftime(DATE_MONTH_NAME)} is BEFORE "
            f"{datetime.now().strftime(DATE_MONTH_NAME)}"
        )
    deadline = datetime.combine(parsed_date.date(), time.max)
    deadline_utc = make_tzaware(deadline, use_tz=timezone.utc)
    return deadline_utc


create_widget_reqparser = RequestParser(bundle_errors=True)
create_widget_reqparser.add_argument(
    "name",
    type=widget_name,
    location="form",
    required=True,
    nullable=False,
    case_sensitive=True,
)
create_widget_reqparser.add_argument(
    "info_url",
    type=URL(schemes=["http", "https"]),
    location="form",
    required=True,
    nullable=False,
)
create_widget_reqparser.add_argument(
    "deadline",
    type=future_date_from_string,
    location="form",
    required=True,
    nullable=False,
)
