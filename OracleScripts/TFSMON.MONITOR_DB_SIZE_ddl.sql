-- Start of DDL Script for Procedure TFSMON.MONITOR_DB_SIZE
-- Generated 28/02/2022 10:49:18 from TFSMON@PRDTRADS

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

    insert into db_growth (DB_NAME,DOM,DBSIZEMBS,DBSIZEGBS,DAYOFWEEK)
    select 
    (select name from v$database)
    ,TRUNC(sysdate)
    ,sum(ttl_Tb_Sz_MBs)
    ,round(sum(ttl_Tb_Sz_MBs)/1024 ,2)
    ,to_char(sysdate, 'DY')
    from monitor_data_growth a 
    where a.dom=trunc(sysdate)
    group by TRUNC(sysdate);
commit;
END;
/



-- End of DDL Script for Procedure TFSMON.MONITOR_DB_SIZE

