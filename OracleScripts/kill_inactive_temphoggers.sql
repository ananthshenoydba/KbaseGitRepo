create or replace procedure kill_inactive_temphoggers
is
l_block_size number;
	BEGIN
		select value into l_block_size from v$parameter where name='db_block_size';
		FOR r1 IN 
				(
					SELECT a.sid||','||a.serial# AS sid_serial FROM  v$session a,
      				v$sort_usage b
					WHERE  a.saddr = b.session_addr
					and    a.status='INACTIVE'
					and    a.username in ('TFSCONNECT')
					and    a.module like 'JDBC Thin Client%'
					and    ROUND(((b.blocks*l_block_size)/1024/1024),2) > 200
				) 
		LOOP
			--dbms_output.put_line( 'alter system kill session ''' || r1.sid_serial || ''' immediate;');
			EXECUTE IMMEDIATE 'alter system kill session ''' || r1.sid_serial || ''' immediate';
		END LOOP;
	EXCEPTION
   		WHEN OTHERS THEN
      		dbms_output.put_line( SQLERRM );
END;
/

BEGIN   FOR x IN (SELECT 'alter system disconnect session ''' || SID || ',' || serial# || ''' post_transaction' kill_mt_sessions
             FROM   v$session a
             WHERE  username = 'SEFCONNECT' AND module like 'JDBC Thin Client%'
             AND    nvl(event,'x') != 'Streams AQ: waiting for messages in the queue'
             AND NOT EXISTS (SELECT * from queue_subscribers_t b WHERE b.session_code = a.client_identifier AND b.username = 'SEFCONNECT')
             ) LOOP
      EXECUTE IMMEDIATE x.kill_mt_sessions;
   END LOOP;
END;



BEGIN
  DBMS_SCHEDULER.CREATE_JOB (
   job_name           =>  'kill_inactive_temphoggers',
   job_type           =>  'PLSQL_BLOCK',
   job_action         =>  'BEGIN sys.kill_inactive_temphoggers; END;',
   start_date         =>  SYSTIMESTAMP,
   repeat_interval    =>  'freq=DAILY; byhour=4; byminute=0; bysecond=0;',
   auto_drop          =>   FALSE,
   comments           =>  'Killing Inactive TFSCONNECT sessions hogging Temp',
   enabled         => TRUE);
END;
/

BEGIN
  DBMS_SCHEDULER.CREATE_JOB (
   job_name           =>  'kill_inactive_tempsessions2',
   job_type           =>  'STORED_PROCEDURE',
   job_action         =>  'sys.kill_inactive_temphoggers',
   start_date         =>  SYSTIMESTAMP,
   repeat_interval    =>  'freq=DAILY; byhour=00; byminute=54; bysecond=0;',
   auto_drop          =>   FALSE,
   comments           =>  'Killing Inactive TFSCONNECT sessions hogging Temp',
   enabled         	  => TRUE);
END;
/ 

BEGIN
  DBMS_SCHEDULER.disable_job (job_name => 'kill_inactive_tempsessions');
END;
/

SELECT job_name, log_date, status, actual_start_date, run_duration, cpu_used FROM dba_scheduler_job_run_details where job_name like '%KILL%'

control_files	("+TRADS_DATA01/{DB_UNIQUE_NAME}/control01.ctl", "+TRADS_REDO01/{DB_UNIQUE_NAME}/control02.ctl", "+TRADS_REDO02/{DB_UNIQUE_NAME}/control02.ctl")	false	File Configuration