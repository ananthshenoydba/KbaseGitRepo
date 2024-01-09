For anyone interested – these are the scripts I used to locate, and reset Reports, obviously you need to manipulate the reports_code in clause :D  


-- Find the reports looking for ones that were sent in the down period
select *  from distr_reports_schedule_T
Where actual is null 
 order by actual desc, schedule desc

-- Remove the next sheduled run
DELETE from distr_reports_schedule_T
where report_code in ( 
'EOD.FUTURE',
'EOD.FUTURE.111',
'EOD.CONV.2'
)
AND actual is null ;

-- Set the report to rerun.
UPDATE distr_reports_schedule_T
SET ACTUAL = NULL, XML = null
where report_code in ( 
'EOD.FUTURE',
'EOD.FUTURE.111',
'EOD.CONV.2'
)
AND actual is not null and actual > trunc(sysdate);
