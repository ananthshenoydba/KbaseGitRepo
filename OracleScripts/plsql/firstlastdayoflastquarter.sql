set serveroutput on;
set term on;
declare
firstday timestamp;
lastday timestamp;
thismonth number;
lastyear varchar2(4);
curnyear varchar2(4);
begin
    select extract(month from sysdate) into thismonth from dual;
    select extract(year from sysdate)-1 into lastyear from dual;
    select extract(year from sysdate) into curnyear from dual;
    if thismonth in (1,2,3) then
        firstday := to_date('01-OCT-'||lastyear, 'DD-MON-YYYY');
        lastday := to_date('31-DEC-'||lastyear, 'DD-MON-YYYY');
    elsif thismonth in (4, 5, 6) then
        firstday := to_timestamp(to_char('01-JAN-'||curnyear), 'DD-MON-YYYY HH24.MI.SS');
        lastday := to_date('31-MAR-'||curnyear, 'DD-MON-YYYY');
        dbms_output.PUT_LINE(firstday);
        dbms_output.PUT_LINE(lastday);
    elsif thismonth in (7, 8, 9) then
        firstday := to_date('01-APR-'||curnyear, 'DD-MON-YYYY');
        lastday := to_date('30-JUN-'||curnyear, 'DD-MON-YYYY');
    else
        firstday := to_date('01-JUL-'||curnyear, 'DD-MON-YYYY');
        lastday := to_date('30-SEP-'||curnyear, 'DD-MON-YYYY');
    end if;
end;
/