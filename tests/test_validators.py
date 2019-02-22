from typesystem.base import ErrorMessage
from typesystem.validators import (
    Boolean,
    String,
    Integer,
    Number,
    Date,
    DateTime,
    Time,
    Object,
)
import datetime


def test_string():
    validator = String()
    assert validator.validate("abc").value == "abc"
    assert validator.validate(None).errors == ["null"]
    assert validator.validate(123).errors == ["type"]

    validator = String(max_length=10)
    assert validator.validate("abc" * 10).errors == ["max_length"]

    validator = String(min_length=3)
    assert validator.validate("a").errors == ["min_length"]

    validator = String(allow_blank=False)
    assert validator.validate("").errors == ["blank"]

    validator = String(allow_null=True)
    assert validator.validate(None).value is None

    validator = String(exact="example")
    assert validator.validate("foo").errors == ["exact"]
    assert validator.validate("example")

    validator = String(enum=["red", "blue", "green"])
    assert validator.validate("foo").errors == ["enum"]
    assert validator.validate("red")

    validator = String(pattern="^[abc]*$")
    assert validator.validate("cba").value == "cba"
    assert validator.validate("cbxa").errors == ["pattern"]


def test_integer():
    validator = Integer()
    assert validator.validate(123).value == 123
    assert validator.validate("123").value == 123
    assert validator.validate(123.0).value == 123
    assert validator.validate(None).errors == ["null"]
    assert validator.validate("abc").errors == ["type"]
    assert validator.validate(True).errors == ["type"]
    assert validator.validate(123.1).errors == ["integer"]
    assert validator.validate(float("inf")).errors == ["integer"]
    assert validator.validate(float("nan")).errors == ["integer"]
    assert validator.validate("123", strict=True).errors == ["type"]

    validator = Integer(allow_null=True)
    assert validator.validate(None).value is None

    validator = Integer(maximum=10)
    assert validator.validate(100).errors == ["maximum"]
    assert validator.validate(10).value == 10

    validator = Integer(minimum=3)
    assert validator.validate(1).errors == ["minimum"]
    assert validator.validate(3).value == 3

    validator = Integer(exclusive_maximum=10)
    assert validator.validate(10).errors == ["exclusive_maximum"]

    validator = Integer(exclusive_minimum=3)
    assert validator.validate(3).errors == ["exclusive_minimum"]

    validator = Integer(enum=[1, 2, 3])
    assert validator.validate(5).errors == ["enum"]

    validator = Integer(enum=[123])
    assert validator.validate(5).errors == ["exact"]

    validator = Integer(exact=123)
    assert validator.validate(5).errors == ["exact"]

    validator = Integer(multiple_of=10)
    assert validator.validate(5).errors == ["multiple_of"]


def test_number():
    validator = Number()
    assert validator.validate(123.1).value == 123.1
    assert validator.validate(123).value == 123.0
    assert validator.validate("123.1").value == 123.1
    assert validator.validate(None).errors == ["null"]
    assert validator.validate("abc").errors == ["type"]
    assert validator.validate(True).errors == ["type"]
    assert validator.validate(float("inf")).errors == ["finite"]
    assert validator.validate(float("nan")).errors == ["finite"]
    assert validator.validate("123", strict=True).errors == ["type"]

    validator = Number(allow_null=True)
    assert validator.validate(None).value is None

    validator = Number(maximum=10.0)
    assert validator.validate(100.0).errors == ["maximum"]
    assert validator.validate(10.0).value == 10.0

    validator = Number(minimum=3.0)
    assert validator.validate(1.0).errors == ["minimum"]
    assert validator.validate(3.0).value == 3.0

    validator = Number(exclusive_maximum=10.0)
    assert validator.validate(10.0).errors == ["exclusive_maximum"]

    validator = Number(exclusive_minimum=3.0)
    assert validator.validate(3.0).errors == ["exclusive_minimum"]

    validator = Number(enum=[1.0, 2.0, 3.0])
    assert validator.validate(5.0).errors == ["enum"]

    validator = Number(enum=[123.0])
    assert validator.validate(5.0).errors == ["exact"]

    validator = Number(exact=123.0)
    assert validator.validate(5.0).errors == ["exact"]

    validator = Number(multiple_of=10.0)
    assert validator.validate(5.0).errors == ["multiple_of"]


def test_boolean():
    validator = Boolean()
    assert validator.validate(True).value is True
    assert validator.validate(False).value is False
    assert validator.validate("True").value is True
    assert validator.validate(1).value is True
    assert validator.validate(None).errors == ["null"]
    assert validator.validate(2).errors == ["type"]

    validator = Boolean(allow_null=True)
    assert validator.validate(None).value is None
    assert validator.validate("").value is None

    validator = Boolean()
    validated = validator.validate("True", strict=True)
    assert validated.errors == ["type"]


def test_object():
    validator = Object()
    assert validator.validate({}).value == {}
    assert validator.validate(None).errors == ["null"]
    assert validator.validate(123).errors == ["type"]
    assert validator.validate({1: 123}).errors == ["invalid_key"]

    validator = Object(allow_null=True)
    assert validator.validate(None).value == None

    validator = Object(min_properties=1)
    assert validator.validate({}).errors == ["empty"]
    assert validator.validate({"a": 1}).is_valid

    validator = Object(min_properties=2)
    assert validator.validate({}).errors == ["min_properties"]
    assert validator.validate({"a": 1, "b": 2}).is_valid

    validator = Object(max_properties=2)
    assert validator.validate({}).is_valid
    assert validator.validate({"a": 1, "b": 2, "c": 3}).errors == ["max_properties"]

    validator = Object(required=["example"])
    assert validator.validate({"example": 123}).value == {"example": 123}
    assert validator.validate({}).errors.to_dict(style="code") == {
        "example": "required"
    }

    validator = Object(properties={"example": Integer()})
    assert validator.validate({"example": "123"}).value == {"example": 123}
    assert validator.validate({"example": "abc"}).errors.to_dict(style="code") == {
        "example": "type"
    }

    validator = Object(pattern_properties={"^x-.*$": Integer()})
    assert validator.validate({"x-example": "123"}).value == {"x-example": 123}
    assert validator.validate({"x-example": "abc"}).errors.to_dict(style="code") == {
        "x-example": "type"
    }

    validator = Object(properties={"example": Integer(default=0)})
    assert validator.validate({"example": "123"}).value == {"example": 123}
    assert validator.validate({}).value == {"example": 0}

    validator = Object(additional_properties=False)
    assert validator.validate({"example": "123"}).errors.to_dict(style="code") == {
        "example": "invalid_property"
    }

    validator = Object(additional_properties=True)
    assert validator.validate({"example": "abc"}).value == {"example": "abc"}

    validator = Object(additional_properties=None)
    assert validator.validate({"example": "abc"}).value == {}

    validator = Object(additional_properties=Integer())
    assert validator.validate({"example": "123"}).value == {"example": 123}
    assert validator.validate({"example": "abc"}).errors.to_dict(style="code") == {
        "example": "type"
    }

    validator = Object(properties={"example": Integer()})
    assert validator.validate({"example": "123"}).value == {"example": 123}
    assert validator.validate({"example": "abc"}).errors.to_dict(style="code") == {
        "example": "type"
    }

    validator = Object(additional_properties=Object(additional_properties=Integer()))
    assert validator.validate({"example": {"nested": "123"}}).value == {
        "example": {"nested": 123}
    }
    assert validator.validate({"example": {"nested": "abc"}}).errors.to_dict(
        style="code"
    ) == {"example": {"nested": "type"}}
    assert dict(validator.validate({"example": {"nested": "abc"}}).errors) == {
        "example": {"nested": "Must be a number."}
    }


def test_dict_errors():
    validator = Integer()
    validated = validator.validate("abc")
    assert validated.errors[""] == "Must be a number."

    validator = Integer()
    validated = validator.validate("abc")
    assert dict(validated.errors) == {"": "Must be a number."}


def test_list_errors():
    validator = Integer()
    validated = validator.validate("abc")
    assert list(validated.errors) == [
        ErrorMessage(text="Must be a number.", code="type")
    ]


# Date


def test_date_from_string():
    validator = Date()
    value = "2049-01-01"

    validated = validator.validate(value)

    assert validated.value == datetime.date(2049, 1, 1)


def test_date_from_date():
    validator = Date()
    value = datetime.date(2049, 1, 1)

    validated = validator.validate(value)

    assert validated.value == value


def test_date_from_incorrect_format():
    validator = Date()
    value = "20490101"

    validated = validator.validate(value)

    assert validated.errors == ["format"]


def test_date_from_invalid_date():
    validator = Date()
    value = "2049-01-32"

    validated = validator.validate(value)

    assert validated.errors == ["invalid"]


#  Time


def test_time_from_string():
    validator = Time()
    value = "12:00:01"

    validated = validator.validate(value)

    assert validated.value == datetime.time(12, 0, 1)


def test_time_with_milliseconds():
    validator = Time()
    value = "12:00:01.001"

    validated = validator.validate(value)

    assert validated.value == datetime.time(12, 0, 1, 1000)


def test_time_with_microseconds():
    validator = Time()
    value = "12:00:01.000001"

    validated = validator.validate(value)

    assert validated.value == datetime.time(12, 0, 1, 1)


def test_time_from_time():
    validator = Time()
    value = datetime.time(12, 0, 1)

    validated = validator.validate(value)

    assert validated.value == value


def test_time_from_incorrect_format():
    validator = Time()
    value = "12.00.01"

    validated = validator.validate(value)

    assert validated.errors == ["format"]


def test_time_from_invalid_tiem():
    validator = Time()
    value = "12:00:60"

    validated = validator.validate(value)

    assert validated.errors == ["invalid"]


# DateTime


def test_datetime_from_string():
    validator = DateTime()
    value = "2049-1-1 12:00:00"

    validated = validator.validate(value)

    assert validated.value == datetime.datetime(2049, 1, 1, 12, 0, 0)


def test_datetime_with_utc_timezone():
    validator = DateTime()
    value = "2049-1-1 12:00:00Z"

    validated = validator.validate(value)

    assert validated.value == datetime.datetime(
        2049, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc
    )


def test_datetime_with_offset_timezone():
    validator = DateTime()
    value = "2049-1-1 12:00:00-0230"
    delta = -datetime.timedelta(hours=2, minutes=30)

    validated = validator.validate(value)

    assert validated.value == datetime.datetime(
        2049, 1, 1, 12, 0, 0, tzinfo=datetime.timezone(delta)
    )


def test_datetime_from_datetime():
    validator = DateTime()
    value = datetime.datetime(2049, 1, 1, 12, 0, 0)

    validated = validator.validate(value)

    assert validated.value == value


def test_datetime_from_incorrect_format():
    validator = DateTime()
    value = "2049:01:01 12:00:00"

    validated = validator.validate(value)

    assert validated.errors == ["format"]


def test_datetime_from_invalid_datetime():
    validator = DateTime()
    value = "2049-01-01 12:00:60"

    validated = validator.validate(value)

    assert validated.errors == ["invalid"]
