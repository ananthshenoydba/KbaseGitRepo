with rawdata as(
select a.SEGMENT_NAME, a.SEGMENT_TYPE, b.table_name as LOB_TABLE, c.table_name as INDEX_TABLE, sum(a.bytes)/1024/1024/1024 as GB 
from 
    dba_segments a left join dba_lobs b on a.SEGMENT_NAME=b.segment_name  
                    left join dba_indexes c on a.segment_name=c.index_name and a.segment_type in ('INDEX', 'LOBINDEX')
                    where a.segment_type not like '%UNDO%' and a.owner='TFS'
                    group by a.SEGMENT_NAME, a.SEGMENT_TYPE, b.table_name,c.table_name order by 5 desc , 4, 3 ,1 asc
),
summary as( 
select CASE 
            WHEN rd.segment_type='LOBSEGMENT' THEN rd.LOB_TABLE
            WHEN rd.segment_type='INDEX' THEN rd.INDEX_TABLE 
            WHEN rd.segment_type='TABLE' THEN rd.SEGMENT_NAME
            ELSE 'UNKNOWN SEGMENT'
       END as TABLENAME
            , GB
            from rawdata rd
)
select tablename, trunc(sum(GB), 3) as GB from summary group by tablename order by 2 desc 