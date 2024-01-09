#!/bin/bash
clear
sqlplus -s sys/sys as sysdba<<END
set serveroutput on;
set feedback off;
execute undousage;
execute dppumpstatus;
execute tempusage;
exit;
END
