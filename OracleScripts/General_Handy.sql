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

