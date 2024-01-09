set lines 250;
col user_sz_gb format a10;
col reusable_space_gb format a20;
col allocated_gb format a20;
col total format a10;
col free_gb format a10;

exec DBMS_OUTPUT.PUT_LINE('============= UNDO STATS ================');

with 
      free_sz as ( select t.tablespace_name, to_char(nvl(sum(f.bytes)/1024/1024/1024,0),'000.99') free_gb from dba_free_space f right join dba_tablespaces t on f.tablespace_name=t.tablespace_name where t.contents='UNDO' group by t.tablespace_name), 
      a as 
      (select tablespace_name, sum(case when status = 'EXPIRED' then blocks end)*8/1048576 reusable_space_gb, 
      sum(case when status in ('ACTIVE', 'UNEXPIRED') then blocks end)*8/1048576 allocated_gb 
      from dba_undo_extents where status in ('ACTIVE', 'EXPIRED', 'UNEXPIRED') 
      group by tablespace_name ), 
      undo_sz as 
      (select tablespace_name, sum(df.user_bytes)/1048576/1024  user_sz_gb from dba_tablespaces ts join dba_data_files df using (tablespace_name) where ts.contents = 'UNDO' and ts.status = 'ONLINE' group by tablespace_name)
      select 
      tablespace_name, 
      TO_CHAR(round(user_sz_gb, 7),'000.99') as user_sz_gb,
      TO_CHAR(round(free_gb, 2), '000.99') as free_gb, 
      TO_CHAR(round(reusable_space_gb, 2), '000.99') as reusable_space_gb , 
      TO_CHAR(round(allocated_gb, 2), '000.99') as allocated_gb , 
      TO_CHAR(round (free_gb + reusable_space_gb + allocated_gb , 2), '000.99') total 
      from undo_sz join free_sz using (tablespace_name) join a using (tablespace_name);

exec DBMS_OUTPUT.PUT_LINE(chr(9));

exec DBMS_OUTPUT.PUT_LINE('============= UNDO STATS BY SESSION ================');

col sid_serial format a15;
col orauser format a25;
col program format a50;
select
   TO_CHAR(s.sid)||','||TO_CHAR(s.serial#) sid_serial,
   NVL(s.username, 'None') orauser,
   s.program,
   r.name undoseg,
   round(t.used_ublk * TO_NUMBER(x.value)/1024/1024 ,2)||'M' "Undo Used"
from
   sys.v_$rollname r,
   sys.v_$session s,
   sys.v_$transaction t,
   sys.v_$parameter x
where
   s.taddr = t.addr
AND
   r.usn = t.xidusn(+)
AND
   x.name = 'db_block_size';
/

exec DBMS_OUTPUT.PUT_LINE(chr(9));

