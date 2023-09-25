-- FUNCTION: public.days_to_birthday(date, date)

-- DROP FUNCTION IF EXISTS public.days_to_birthday(date, date);

CREATE OR REPLACE FUNCTION public.days_to_birthday(born date, curr date)
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
$BODY$;

ALTER FUNCTION public.days_to_birthday(date, date)
    OWNER TO postgres;
