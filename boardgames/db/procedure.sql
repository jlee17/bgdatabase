CREATE FUNCTION get_hashed_pw(uname TEXT)
RETURNS text AS $$
DECLARE passed text;
BEGIN
        SELECT  password INTO passed
        FROM    users
        WHERE   email = $1;

        RETURN passed;
END;
$$  LANGUAGE plpgsql;