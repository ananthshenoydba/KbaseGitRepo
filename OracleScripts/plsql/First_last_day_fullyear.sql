with dateparam as
( 
SELECT TRUNC(SYSDATE-365, 'YYYY') + LEVEL - 1 AS mydate FROM dual CONNECT BY TRUNC(TRUNC(SYSDATE, 'YYYY') + LEVEL - 1, 'YYYY') = TRUNC(SYSDATE, 'YYYY') 
) 
select distinct ADD_MONTHS(last_day(mydate)+1, -1) as firstday, 
to_char(add_months(last_day(mydate)+1,-1),'DAY') as DOW ,
case 
    when to_char(add_months(last_day(mydate)+1,-1),'D') = '7' then ADD_MONTHS(last_day(mydate)+1, -1)+1
    when to_char(add_months(last_day(mydate)+1,-1),'D') = '6' then ADD_MONTHS(last_day(mydate)+1, -1)+2
    else ADD_MONTHS(last_day(mydate)+1, -1)
end as firstbusinessday
,case   
    when to_char(add_months(last_day(mydate)+1,-1),'D') = '7' then to_char(add_months(last_day(mydate)+1,-1)+1,'DAY') 
    when to_char(add_months(last_day(mydate)+1,-1),'D') = '6' then to_char(add_months(last_day(mydate)+1,-1)+2,'DAY') 
    else to_char(add_months(last_day(mydate)+1,-1),'DAY') 
end as firstbusinessdayofweek
,last_day(mydate) as lastday 
,case
    when to_char(last_day(mydate),'D') = '6' then last_day(mydate)-1 -- reduce one day if last day is Saturday
    when to_char(last_day(mydate),'D') = '7' then last_day(mydate)-2 -- reduce two days if last day is Sunday
    else last_day(mydate) 
end as lastbusinessday 
,case  
    when to_char(last_day(mydate),'D') = '6' then to_char(last_day(mydate)-1,'DAY') 
    when to_char(last_day(mydate),'D') = '7' then to_char(last_day(mydate)-2,'DAY') 
    else to_char(last_day(mydate),'DAY') 
    end as lastbusinessdayofweek 
from dateparam
order by 1 asc