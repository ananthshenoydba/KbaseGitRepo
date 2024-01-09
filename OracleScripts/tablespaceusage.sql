set lines 250;
set serveroutput on;
set heading off;
set feedback off;

exec DBMS_OUTPUT.PUT_LINE('============= TABLESPACES > 80% USED ================');

select case 
        when used_percent > 80 then tablespace_name 
        else 'None'
        end
from dba_tablespace_usage_metrics 
where used_percent > 80; 

exec DBMS_OUTPUT.PUT_LINE(chr(9));

exec DBMS_OUTPUT.PUT_LINE('=====================================================');

exec DBMS_OUTPUT.PUT_LINE(chr(9));
