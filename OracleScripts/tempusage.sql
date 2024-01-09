SET PAGESIZE 50000
SET LINESIZE 300
SET SERVEROUTPUT on; 
SET feedback off;
COLUMN tablespace FORMAT A10
COLUMN temp_size FORMAT A10
COLUMN sid_serial FORMAT A15
COLUMN username FORMAT A15
COLUMN program FORMAT A50

exec DBMS_OUTPUT.PUT_LINE('============= TEMP STATS ================');

SELECT A.tablespace_name tablespace, D.mb_total,
    SUM (A.used_blocks * D.block_size) / 1024 / 1024 mb_used,
    D.mb_total - SUM (A.used_blocks * D.block_size) / 1024 / 1024 mb_free
   FROM v$sort_segment A,
    (
   SELECT B.name, C.block_size, SUM (C.bytes) / 1024 / 1024 mb_total
    FROM v$tablespace B, v$tempfile C
     WHERE B.ts#= C.ts#
      GROUP BY B.name, C.block_size) D
    WHERE A.tablespace_name = D.name
    GROUP by A.tablespace_name, D.mb_total;

exec DBMS_OUTPUT.PUT_LINE(chr(9));

exec DBMS_OUTPUT.PUT_LINE('============= TEMP STATS BY SESSION ================');
 
SELECT b.tablespace,
       SUM(ROUND(((b.blocks*p.value)/1024/1024),2)) AS Tmp_Usg_MB,
       a.sid,
       a.serial#,
       NVL(a.username, '(oracle)') AS username,
       a.program,
       a.status,
       a.sql_id,
       a.logon_time
FROM   gv$session a,
       gv$sort_usage b,
       gv$parameter p
WHERE  p.name  = 'db_block_size'
AND    a.saddr = b.session_addr
AND    a.inst_id=b.inst_id
AND    a.inst_id=p.inst_id
group by b.tablespace,a.sid, a.serial#, a.username,a.program,
       a.status,
       a.sql_id,
       a.logon_time
ORDER BY 2 asc;

exec DBMS_OUTPUT.PUT_LINE(chr(9));
