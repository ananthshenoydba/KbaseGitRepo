#!/bin/bash
clear
sqlplus -s sys/sys as sysdba<<END
set serveroutput on;
set feedback off;
@tempusage.sql;
@undousage.sql;
@tablespaceusage.sql;
@impdpstatus.sql
exit;
END
#tail -17 /opt/contexts/backup/oracle/dpdump/PRDFX01/imp_prc_hist_pre2014.out | grep -E "State|Object Name|Completed Rows|Percent Done"
tail -17 /opt/contexts/backup/oracle/dpdump/PRDFX01/imp_prc_hist_2015.out | grep -E "State|Object Name|Completed Rows|Percent Done"
