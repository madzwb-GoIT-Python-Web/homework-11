from alembic_utils.pg_function import PGFunction
days_to_birthday = PGFunction(
  schema='public',
  signature='days_to_birthday(born date, curr date)',
  definition="""
    RETURNS integer
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
    DECLARE
        diff INT = 0; 
        days INT = 0;
        birth_year INT = 0;
        birth_month INT = 0;
        birth_day INT = 0;
        is_leap BOOL = False;
        birth_date DATE;
    BEGIN
        birth_year = DATE_PART('year', curr);
        IF birth_year % 4 = 0 and (birth_year % 100 != 0 or birth_year % 400 = 0) THEN
            is_leap = True;
        ELSE
            is_leap = False;
        END IF;
        birth_day = DATE_PART('day', born);
        birth_month = DATE_PART('month', born);
        IF birth_day = 29 and birth_month = 2 and not is_leap THEN
            birth_date = make_date(birth_year, birth_month, 28);
        ELSE
            birth_date = make_date(birth_year, birth_month, birth_day);
        END IF;
        days = birth_date - curr;
        --days = DATE_PART('year', diff);
        --RETURN diff;
        IF days < 0 THEN
            birth_year = birth_year + 1;
            IF birth_year % 4 = 0 and (birth_year % 100 != 0 or birth_year % 400 = 0) THEN
                is_leap = True;
            ELSE
                is_leap = False;
            END IF;
            IF birth_day = 29 and birth_month = 2 and not is_leap THEN
                birth_date = make_date(birth_year, birth_month, 28);
            ELSE
                birth_date = make_date(birth_year, birth_month, birth_day);
            days = birth_date - curr;
            --days = DATE_PART('day', diff);
            END IF;
        END IF;
        RETURN days;
    END;
    $BODY$
  """
)

# import registrator.registrator as registrator

# import calendar
# from datetime import datetime, date

# def udf_days_to_birthday(born: date, to: date = date.today()):
#     # birthday = datetime(year = now.year, month = now.month, day = self._birthday.day)
#     if born.day == 29 and born.month == 2 and not calendar.isleap(to.year):
#         birthday = date(to.year,born.month,28)
#     else:
#         birthday = date(to.year, born.month, born.day)
#     diff = birthday - to
#     if diff.days < 0:
#         year = birthday.year + 1
#         if born.day == 29 and born.month == 2 and not calendar.isleap(year):
#             birthday = date(year, born.month,28)
#         else:
#             birthday = date(year, born.month,born.day)
#         diff = birthday - to
#     return diff.days

# class FUNCTIONS(registrator.REGISTRATOR):    ...
# FUNCTIONS.register("udf_", __name__, globals(), type(udf_days_to_birthday) ,["__builtins__",], True)
# registry = FUNCTIONS()