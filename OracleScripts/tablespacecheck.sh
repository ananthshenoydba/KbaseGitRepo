#!/bin/bash
#######################################################################################################################
#
# Created 2019-09-05 AShenoy
#
#######################################################################################################################

scriptname=$0
. ~/.bash_profile
thisHost=`hostname`
scriptdir="/opt/oracle/scripts"
logdir="${scriptdir}/log"
logname=TblSpc_check
warning=70
critical=80
warningcount=0

to="ananth.shenoy@tradition.com"
from="database.server@tradition.int"


# Set Timestamp for log files
tstamp=`date "+%Y-%m-%d"`
warnlog="${scriptdir}/log/$thisHost_$tstamp.txt"

# Check for Script directory
if [ ! -d ${scriptdir} ]
   then
       echo -e "\e[1;31m\n\t\t Error: Script directory ${scriptdir} not found \e[0m"
       exit 1
fi

#Check for Log directory
if [ ! -d ${logdir} ]
   then
       # Log directory does not exist. Try to create it...
       mkdir ${logdir}
           if [ $? -ne 0 ]; then
              echo -e "\e[1;31m\n\t\t Error: Create log directory ${logdir} retured an error \e[0m"
          exit 1
           fi
fi

# Set current directory to script dir
cd ${scriptdir}

if [[  `pwd` != ${scriptdir} ]]; then
   echo "Error: Current dir != Script dir (${scriptdir})"
   exit 1
fi

# Initialise log file
LOG=${logdir}/${logname}_$tstamp.log

echo '' > $LOG
echo "Starting $0 at" >> $LOG
date >> $LOG

for i in `ps -ef | grep pmon | grep -v grep| grep -v ASM | awk '{print $8}'|cut -d'_' -f3`;
        do
        . $HOME/setenv $i
               warningcount=`${ORACLE_HOME}/bin/sqlplus -s / as sysdba <<-EOF
               	set feed off
               	set pages 0
               	select count(*) from dba_tablespace_usage_metrics where USED_PERCENT > $warning and used_percent < $critical;
               	exit;
               	/
		EOF`

                if [ $warningcount -gt 0 ]
                then
                dummy=`sqlplus -s / as sysdba <<-EOF
                        col used_percent format 99.99
                        set heading off
                        set feedback off
                        spool $warnlog append
                        select 'TABLESPACES above WARNING($warning%) in $i are:' from dual;
                        set heading on
                        select tablespace_name, used_percent from dba_tablespace_usage_metrics where USED_PERCENT > $warning and used_percent < $critical;
                        spool off
                        exit
			EOF`
                fi;

               criticalcount=`${ORACLE_HOME}/bin/sqlplus -s / as sysdba <<-EOF
                set feed off
                set pages 0
                select count(*) from dba_tablespace_usage_metrics where USED_PERCENT > $critical;
                exit;
                /
		EOF`

                if [ $criticalcount -gt 0 ]
                then
                dummy=`sqlplus -s / as sysdba <<-EOF
                        col used_percent format 99.99
                        set heading off
                        set feedback off
                        spool $warnlog append
                        select 'TABLESPACES above CRITICAL($critical%) in $i are:' from dual;
                        set heading on
                        select tablespace_name, used_percent from dba_tablespace_usage_metrics where USED_PERCENT > $critical;
                        spool off
                        exit;
                        /
			EOF`
                 fi;
		
	       rmantable='v$rman_backup_job_details' 		
	       rmancount=`${ORACLE_HOME}/bin/sqlplus -s / as sysdba <<-EOF
                set feed off
                set pages 0
		select count(*) from $rmantable where start_time >= trunc(sysdate -1) and start_time < trunc(sysdate) and status != 'COMPLETED';                
		exit;
                /
		EOF`
		
		echo $rmancount
		
		if [ $rmancount -gt 0 ]
		then
		dummy=`sqlplus -s / as sysdba <<-EOF
                        col failure_count format 999
                        set heading off
                        set feedback off
                        spool $warnlog append
                        select 'RMAN Backups have FAILED in $i Details Below:' from dual;
                        set heading on
                        select INPUT_TYPE, count(*) as failure_count from $rmantable where start_time >= trunc(sysdate -1) and start_time < trunc(sysdate) and status != 'COMPLETED' group by INPUT_TYPE;
                        spool off
                        exit;
                        /
			EOF`
        	fi 
	done

# echo "Tidy up old log files in: ${logdir}" >>$LOG
# echo "Current dir = `pwd`" >>$LOG

#    find ${logdir} -maxdepth 1 -name "${logname}_????-??-??-??-??-??.log" -mtime +32 -exec ls -l {} \; >> $LOG
#    find ${logdir} -maxdepth 1 -name "${logname}_????-??-??-??-??-??.log" -mtime +32 -exec rm -v {} \; >> $LOG

echo "Ouput generated by: ${scriptname}" >> $LOG
##### Last Line of Script #####
