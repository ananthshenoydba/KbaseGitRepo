set serveroutput on;
declare
    cursor prodtables is select table_name from user_tables where table_name not like '%_X' order by 1 asc;
    --cursor prodtables is select table_name from user_tables where table_name in ('PRICES_T','PRICES_PENDING_T') order by 1 asc;
    r_table varchar2(100);
    r_numrows number;
    r_numrows_remote number;
    local_sql varchar2(150);
    remote_sql varchar2(150);
begin
OPEN prodtables;
    LOOP
        FETCH prodtables INTO r_table;
        EXIT WHEN prodtables%NOTFOUND;
        begin
        local_sql:='select count(*) from ' || r_table;
        execute immediate local_sql into r_numrows;
        end;
        begin
        remote_sql:='select count(*) from ' || r_table||'@uat19c';
        execute immediate remote_sql into r_numrows_remote;
            exception
                WHEN OTHERS THEN
                r_numrows_remote:= -1;
        end;            
        dbms_output.PUT_LINE('tablename ==> ' || r_table || ' no of rows '|| r_numrows || ' no of remote rows ' || r_numrows_remote);
    end loop;
close prodtables;
end;