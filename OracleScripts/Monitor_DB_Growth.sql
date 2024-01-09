CREATE TABLE monitor_data_growth
    (dom DATE ,
    table_name VARCHAR2(100 BYTE) ,
    tablespace_name VARCHAR2(100 BYTE) ,
    tablesize_kbs NUMBER,
    lobsize_kbs NUMBER,
    indexsize_kbs NUMBER,
    ttl_tb_sz_mbs NUMBER)
  SEGMENT CREATION IMMEDIATE
  TABLESPACE  users
  NOPARALLEL
  LOGGING
  MONITORING
/

-- Constraints for MONITOR_DATA_GROWTH

ALTER TABLE monitor_data_growth
ADD CONSTRAINT datagrowth_pk PRIMARY KEY (dom, table_name, tablespace_name)
USING INDEX
  TABLESPACE  users
/

CREATE TABLE db_growth
    (db_name VARCHAR2(9 BYTE) ,
    dom DATE ,
    dbsizegbs NUMBER,
    dbsizembs NUMBER)
  SEGMENT CREATION IMMEDIATE
  TABLESPACE  users
  NOPARALLEL
  LOGGING
  MONITORING
/


-- Constraints for DB_GROWTH

ALTER TABLE db_growth
ADD CONSTRAINT db_growth_pk PRIMARY KEY (db_name, dom)
USING INDEX
  TABLESPACE  users
/

CREATE OR REPLACE 
PROCEDURE monitor_db_size
AS
BEGIN
INSERT INTO monitor_data_growth (DOM,TABLE_NAME,TABLESPACE_NAME,TABLESIZE_KBS,LOBSIZE_KBS,INDEXSIZE_KBS,TTL_TB_SZ_MBS) 
with 
logsegs as
        (
        select 
        b.table_name, sum(bytes)/1024 KBs 
        from 
        dba_segments a join dba_lobs b on a.segment_name=b.segment_name and a.owner=b.owner and a.owner='TFS' 
        group by 
        b.table_name 
        order by 2 desc
        ),
tablesegs as 
        (
        select 
        a.segment_name as table_name, 
        a.tablespace_name, 
        sum(bytes)/1024 KBs 
        from 
        dba_segments a where a.owner='TFS' and a.segment_type = 'TABLE' and ( a.segment_name like '%_T' or a.segment_name like '%_HT')
        group by 
        a.segment_name,
        a.tablespace_name
        order by 1 asc 
        ),
indexsegs as
        (
        select 
        b.table_name, sum(bytes)/1024 KBs 
        from 
        dba_segments a join dba_indexes b on a.segment_name=b.index_name 
        and a.owner='TFS' 
        and a.segment_type = 'INDEX'
        group by 
        b.table_name 
        )
select 
    trunc(sysdate)
    ,a.table_name 
    ,a.tablespace_name 
    ,nvl(a.kbs,0) 
    ,nvl(b.kbs,0) 
    ,nvl(c.kbs,0) 
    ,round((a.kbs + nvl(b.kbs,0) + nvl(c.kbs,0))/1024,2)
from tablesegs a 
    left join logsegs b on a.table_name=b.table_name 
    left join indexsegs c on a.table_name=c.table_name;

    insert into db_growth (DB_NAME,DOM,DBSIZEMBS,DBSIZEGBS)
    select 
    (select name from v$database)
    ,TRUNC(sysdate)
    ,sum(ttl_Tb_Sz_MBs)
    ,round(sum(ttl_Tb_Sz_MBs)/1024 ,2)
    from monitor_data_growth a 
    where a.dom=trunc(sysdate)
    group by TRUNC(sysdate);
commit;
END;
/

-- End of DDL Script for Procedure TFSMON.MONITOR_DB_SIZE

BEGIN 
   dbms_scheduler.create_job ( 
    job_name => 'db_growth_snapshot', 
    job_type => 'PLSQL_BLOCK', 
    job_action => 'monitor_db_size;', 
    start_date => SYSTIMESTAMP, 
    enabled => true, 
    repeat_interval => 'FREQ=DAILY;BYHOUR=13;BYMINUTE=45;BYSECOND=0'
   ); 
END;
/


----------- USEFUL QUERIES ------------

begin
  DBMS_SCHEDULER.drop_JOB('db_growth_snapshot');
END;
/


begin
  dbms_scheduler.set_attribute
  (name => 'db_growth_snapshot',
  attribute => 'REPEAT_INTERVAL',
  value     => 'FREQ=DAILY;BYHOUR=13;BYMINUTE=34;BYSECOND=0');
  end;
/

col JOB_NAME for a20;
col JOB_ACTION for a20;
col SCHEDULE_NAME for a20;
select JOB_NAME
  , JOB_TYPE, JOB_ACTION
  , SCHEDULE_NAME, ENABLED
    , AUTO_DROP, STATE
  , TO_CHAR(NEXT_RUN_DATE,'YYYY-MM-DD HH24:MI') as NEXT_RUN
from USER_SCHEDULER_JOBS;

select value from v$parameter where name='job_queue_processes';

select count(*) from user_scheduler_running_jobs;