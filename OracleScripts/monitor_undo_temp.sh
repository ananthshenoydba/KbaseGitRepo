#!/bin/bash
clear
sqlplus -s sys/sys as sysdba<<END
set serveroutput on;
set feedback off;
@tempusage_nodetails.sql;
@undousage_nodetails.sql;
exit;
END
