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
