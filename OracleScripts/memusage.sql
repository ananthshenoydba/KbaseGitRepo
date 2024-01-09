REM =============================================================================
REM ************ SCRIPT TO MONITOR MEMORY USAGE BY DATABASE SESSIONS ************
REM =============================================================================
REM Created: 21/march/2003
REM Last update: 28/may/2003
REM
REM NAME
REM ====
REM MEMORY.sql
REM
REM AUTHOR
REM ======
REM Mauricio Buissa
REM
REM DISCLAIMER
REM ==========
REM This script is provided for educational purposes only. It is NOT supported by
REM Oracle World Wide Technical Support. The script has been tested and appears
REM to work as intended. However, you should always test any script before
REM relying on it.
REM
REM PURPOSE
REM =======
REM Retrieves PGA and UGA statistics for users and background processes sessions.
REM
REM EXECUTION ENVIRONMENT
REM =====================
REM SQL*Plus
REM
REM ACCESS PRIVILEGES
REM =================
REM Select on V$SESSTAT, V$SESSION, V$BGPROCESS, V$PROCESS and V$INSTANCE.
REM
REM USAGE
REM =====
REM $ sqlplus "/ as sysdba" @MEMORY
REM
REM INSTRUCTIONS
REM ============
REM Call MEMORY.sql from SQL*Plus, connected as any DBA user.
REM Press <ENTER> whenever you want to refresh information.
REM You can change the ordered column and the statistics shown by choosing from the menu.
REM Spool files named MEMORY_YYYYMMDD_HH24MISS.lst will be generated in the current directory.
REM Every time you refresh screen, a new spool file is created, with a snapshot of the statistics shown.
REM These snapshot files may be uploaded to Oracle Support Services for future reference, if needed.
REM
REM REFERENCES
REM ==========
REM "Oracle Reference" - Online Documentation
REM
REM SAMPLE OUTPUT
REM =============
REM :::::::::::::::::::::::::::::::::: PROGRAM GLOBAL AREA statistics :::::::::::::::::::::::::::::::::
REM
REM SESSION                                            PID/THREAD       CURRENT SIZE       MAXIMUM SIZE
REM -------------------------------------------------- ---------- ------------------ ------------------
REM     9 - SYS: myworkstation                               2258           10.59 MB           10.59 MB
REM     3 - LGWR: testserver                                 2246            5.71 MB            5.71 MB
REM     2 - DBW0: testserver                                 2244            2.67 MB            2.67 MB
REM ...
REM
REM :::::::::::::::::::::::::::::::::::: USER GLOBAL AREA statistics ::::::::::::::::::::::::::::::::::
REM
REM SESSION                                            PID/THREAD       CURRENT SIZE       MAXIMUM SIZE
REM -------------------------------------------------- ---------- ------------------ ------------------
REM     9 - SYS: myworkstation                               2258            0.29 MB            0.30 MB
REM     5 - SMON: testserver                                 2250            0.06 MB            0.06 MB
REM     4 - CKPT: testserver                                 2248            0.05 MB            0.05 MB
REM ...
REM
REM SCRIPT BODY
REM ===========

REM Starting script execution
CLE SCR
PROMPT .
PROMPT .              ======== SCRIPT TO MONITOR MEMORY USAGE BY DATABASE SESSIONS ========
PROMPT .

REM Setting environment variables
SET LINESIZE       200
SET PAGESIZE       500
SET FEEDBACK       OFF
SET VERIFY         OFF
SET SERVEROUTPUT   ON
SET TRIMSPOOL      ON
COL "SESSION"      FORMAT A50
COL "PID/THREAD"   FORMAT A10
COL "      CURRENT SIZE" FORMAT A18
COL "      MAXIMUM SIZE" FORMAT A18

REM Setting user variables values
SET    TERMOUT OFF
DEFINE sort_order = 3
DEFINE show_pga   = 'ON'
DEFINE show_uga   = 'ON'
COL    sort_column NEW_VALUE sort_order
COL    pga_column  NEW_VALUE show_pga
COL    uga_column  NEW_VALUE show_uga
COL    snap_column NEW_VALUE snap_time
SELECT nvl(:sort_choice, 3) "SORT_COLUMN"
FROM   dual
/
SELECT nvl(:pga_choice, 'ON') "PGA_COLUMN"
FROM   dual
/
SELECT nvl(:uga_choice, 'ON') "UGA_COLUMN"
FROM   dual
/
SELECT to_char(sysdate, 'YYYYMMDD_HH24MISS') "SNAP_COLUMN"
FROM   dual
/

REM Creating new snapshot spool file
SPOOL MEMORY_&snap_time

REM Showing PGA statistics for each session and background process
SET      TERMOUT &show_pga
PROMPT
PROMPT   :::::::::::::::::::::::::::::::::: PROGRAM GLOBAL AREA statistics :::::::::::::::::::::::::::::::::
SELECT   to_char(ssn.sid, '9999') || ' - ' || nvl(ssn.username, nvl(bgp.name, 'background')) ||
                  nvl(lower(ssn.machine), ins.host_name) "SESSION",
             to_char(prc.spid, '999999999') "PID/THREAD",
             to_char((se1.value/1024)/1024, '999G999G990D00') || ' MB' "      CURRENT SIZE",
             to_char((se2.value/1024)/1024, '999G999G990D00') || ' MB' "      MAXIMUM SIZE"
    FROM     v$sesstat se1, v$sesstat se2, v$session ssn, v$bgprocess bgp, v$process prc,
          v$instance ins,  v$statname stat1, v$statname stat2
 WHERE    se1.statistic# = stat1.statistic# and stat1.name = 'session pga memory'
 AND      se2.statistic#  = stat2.statistic# and stat2.name = 'session pga memory max'
 AND      se1.sid        = ssn.sid
 AND      se2.sid        = ssn.sid
 AND      ssn.paddr      = bgp.paddr (+)
 AND      ssn.paddr      = prc.addr  (+)
ORDER BY &sort_order DESC
/

REM Showing UGA statistics for each session and background process
SET      TERMOUT &show_uga
PROMPT
PROMPT   :::::::::::::::::::::::::::::::::::: USER GLOBAL AREA statistics ::::::::::::::::::::::::::::::::::
SELECT   to_char(ssn.sid, '9999') || ' - ' || nvl(ssn.username, nvl(bgp.name, 'background')) ||
                  nvl(lower(ssn.machine), ins.host_name) "SESSION",
             to_char(prc.spid, '999999999') "PID/THREAD",
             to_char((se1.value/1024)/1024, '999G999G990D00') || ' MB' "      CURRENT SIZE",
             to_char((se2.value/1024)/1024, '999G999G990D00') || ' MB' "      MAXIMUM SIZE"
    FROM     v$sesstat se1, v$sesstat se2, v$session ssn, v$bgprocess bgp, v$process prc,
          v$instance ins,  v$statname stat1, v$statname stat2
 WHERE    se1.statistic# = stat1.statistic# and stat1.name = 'session uga memory'
 AND      se2.statistic#  = stat2.statistic# and stat2.name = 'session uga memory max'
 AND      se1.sid        = ssn.sid
 AND      se2.sid        = ssn.sid
 AND      ssn.paddr      = bgp.paddr (+)
 AND      ssn.paddr      = prc.addr  (+)
ORDER BY &sort_order DESC
/

REM Showing sort information
SET TERMOUT ON
PROMPT
BEGIN
    IF (&sort_order = 1) THEN
        dbms_output.put_line('Ordered by SESSION');
    ELSIF (&sort_order = 2) THEN
        dbms_output.put_line('Ordered by PID/THREAD');
    ELSIF (&sort_order = 3) THEN
        dbms_output.put_line('Ordered by CURRENT SIZE');
    ELSIF (&sort_order = 4) THEN
        dbms_output.put_line('Ordered by MAXIMUM SIZE');
    END IF;
END;
/

REM Closing current snapshot spool file
SPOOL OFF

REM Showing the menu and getting sort order and information viewing choice
PROMPT
PROMPT Choose the column you want to sort:        == OR ==        You can choose which information to see:  
PROMPT ... 1. Order by SESSION                                    ... 5. PGA and UGA statistics (default)
PROMPT ... 2. Order by PID/THREAD                                 ... 6. PGA statistics only
PROMPT ... 3. Order by CURRENT SIZE (default)                     ... 7. UGA statistics only
PROMPT ... 4. Order by MAXIMUM SIZE
PROMPT
ACCEPT choice NUMBER PROMPT 'Enter the number of your choice or press <ENTER> to refresh information: '
VAR    sort_choice NUMBER
VAR    pga_choice  CHAR(3)
VAR    uga_choice  CHAR(3)
BEGIN
    IF (&choice = 1 OR &choice = 2 OR &choice = 3 OR &choice = 4) THEN
        :sort_choice := &choice;
        :pga_choice  := '&show_pga';
        :uga_choice  := '&show_uga';
    ELSIF (&choice = 5) THEN
        :sort_choice := &sort_order;
        :pga_choice  := 'ON';
        :uga_choice  := 'ON';
    ELSIF (&choice = 6) THEN
        :sort_choice := &sort_order;
        :pga_choice  := 'ON';
        :uga_choice  := 'OFF';
    ELSIF (&choice = 7) THEN
        :sort_choice := &sort_order;
        :pga_choice  := 'OFF';
        :uga_choice  := 'ON';
    ELSE
        :sort_choice := &sort_order;
        :pga_choice  := '&show_pga';
        :uga_choice  := '&show_uga';
    END IF;
END;
/

REM Finishing script execution

PROMPT Type "@MEMORY" and press <ENTER>
SET FEEDBACK     ON
SET VERIFY       ON
SET SERVEROUTPUT OFF
SET TRIMSPOOL    OFF

REM =============
REM END OF SCRIPT
REM =============
