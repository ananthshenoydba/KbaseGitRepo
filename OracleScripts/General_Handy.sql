- GENERIC LOG FILE INFO -
=========================

SELECT a.GROUP#, a.THREAD#, a.SEQUENCE#, a.ARCHIVED, a.STATUS, b.MEMBER AS REDOLOG_FILE_NAME, (a.BYTES/1024/1024) AS SIZE_MB
FROM v$log a JOIN v$logfile b ON a.Group#=b.Group# ORDER BY a.GROUP#;

===================
- MOVING REDOLOGS -
===================

alter system set db_create_online_log_dest_1='+PRDEQD11_REDO01' scope=both;
alter system set db_create_online_log_dest_2='+PRDEQD11_REDO02' scope=both;

select count(*),to_char(first_time,'YYYY:MM:DD:HH24')from v$log_history group by to_char(first_time,'YYYY:MM:DD:HH24') order by 2;

ALTER DATABASE ADD LOGFILE group 4 ('+PRDEQN11_REDO01', '+PRDEQN11_REDO02') SIZE 512M;

ALTER DATABASE DROP LOGFILE GROUP 8;
ALTER DATABASE ADD LOGFILE group 8 ('+PRDEQD11_REDO01', '+PRDEQD11_REDO02') SIZE 512M;

SELECT a.GROUP#, a.THREAD#, a.SEQUENCE#, a.ARCHIVED, a.STATUS, b.MEMBER AS REDOLOG_FILE_NAME, (a.BYTES/1024/1024) AS SIZE_MB
FROM v$log a JOIN v$logfile b ON a.Group#=b.Group# ORDER BY a.GROUP#;

===================
- SHOW JOB STATUS -
===================

set pages 50000;
set lines 250;
col what format a45;
col status format a15;
col schema_user format a10;
col next_date format a20;
col this_date format a20;

SELECT   a.job,
         DECODE(NVL(b.SID, '1'),
                1, 'SCHEDULED',
                'RUNNING') status,
         a.schema_user,
         a.this_date,
         a.next_date,
         a.broken,
         a.failures,
         a.what
FROM     dba_jobs a,
         dba_jobs_running b
WHERE    a.job = b.job(+) and a.schema_user in ('TFS', 'TFSAR', 'SEF_OWNER')
ORDER BY 2;

 repair tfs.interests_t sourcewhere "id in (select id from tfs.int_filter_t where updated > trunc(sysdate,'YYYY'))" targetwhere "id in (select id from sef_owner.fx_int_filter_t where updated > trunc(sysdate,'YYYY'))"
