SET SERVEROUTPUT ON;
SET FEEDBACK OFF;

exec DBMS_OUTPUT.PUT_LINE('============= IMPDP JOB STATUS ================');

DECLARE
  ind NUMBER;              
  h1 NUMBER;               
  percent_done NUMBER;     
  job_state VARCHAR2(30);  
  js ku$_JobStatus;        
  ws ku$_WorkerStatusList; 
  sts ku$_Status;          
BEGIN
h1 := DBMS_DATAPUMP.attach('SYS_IMPORT_FULL_02', 'SYS');
dbms_datapump.get_status(h1,
           dbms_datapump.ku$_status_job_error +
           dbms_datapump.ku$_status_job_status +
           dbms_datapump.ku$_status_wip, 0, job_state, sts);
js := sts.job_status;
ws := js.worker_status_list;
      dbms_output.put_line('*** Job percent done = ' ||
                           to_char(js.percent_done));
      dbms_output.put_line('restarts - '||js.restart_count);
ind := ws.first;
  while ind is not null loop
    dbms_output.put_line('rows completed - '||ws(ind).completed_rows);
    ind := ws.next(ind);
  end loop;
DBMS_DATAPUMP.detach(h1);
end;
/

exec DBMS_OUTPUT.PUT_LINE('==============-=-=-=-=-=-=-=-=-=-=============');

DECLARE
  ind NUMBER;
  h1 NUMBER;
  percent_done NUMBER;
  job_state VARCHAR2(30);
  js ku$_JobStatus;
  ws ku$_WorkerStatusList;
  sts ku$_Status;
BEGIN
h1 := DBMS_DATAPUMP.attach('SYS_IMPORT_FULL_03', 'SYS');
dbms_datapump.get_status(h1,
           dbms_datapump.ku$_status_job_error +
           dbms_datapump.ku$_status_job_status +
           dbms_datapump.ku$_status_wip, 0, job_state, sts);
js := sts.job_status;
ws := js.worker_status_list;
      dbms_output.put_line('*** Job percent done = ' ||
                           to_char(js.percent_done));
      dbms_output.put_line('restarts - '||js.restart_count);
ind := ws.first;
  while ind is not null loop
    dbms_output.put_line('rows completed - '||ws(ind).completed_rows);
    ind := ws.next(ind);
  end loop;
DBMS_DATAPUMP.detach(h1);
end;
/

exec DBMS_OUTPUT.PUT_LINE('==============-=-=-=-=-=-=-=-=-=-=============');
/*
DECLARE
  ind NUMBER;
  h1 NUMBER;
  percent_done NUMBER;
  job_state VARCHAR2(30);
  js ku$_JobStatus;
  ws ku$_WorkerStatusList;
  sts ku$_Status;
BEGIN
h1 := DBMS_DATAPUMP.attach('SYS_IMPORT_FULL_04', 'SYS');
dbms_datapump.get_status(h1,
           dbms_datapump.ku$_status_job_error +
           dbms_datapump.ku$_status_job_status +
           dbms_datapump.ku$_status_wip, 0, job_state, sts);
js := sts.job_status;
ws := js.worker_status_list;
      dbms_output.put_line('*** Job percent done = ' ||
                           to_char(js.percent_done));
      dbms_output.put_line('restarts - '||js.restart_count);
ind := ws.first;
  while ind is not null loop
    dbms_output.put_line('rows completed - '||ws(ind).completed_rows);
    ind := ws.next(ind);
  end loop;
DBMS_DATAPUMP.detach(h1);
end;
/
*/
exec DBMS_OUTPUT.PUT_LINE('==============-=-=-=-=-=-=-=-=-=-=============');
