set linesize 150
select 
    /*+ RULE */ s1.username || '@' || s1.machine
    || ' ( SID=' || s1.sid || ' )  is blocking '
    || s2.username || '@' || s2.machine || ' ( SID=' || s2.sid || ' ) ' AS blocking_status
    from gv$lock l1, gv$session s1, gv$lock l2, gv$session s2
    where s1.sid=l1.sid and s2.sid=l2.sid
    and l1.BLOCK=1 and l2.request > 0
    and l1.id1 = l2.id1
    and l2.id2 = l2.id2 ;

--## Blocking lock Basic Query ##--

select
 (select username from v$session where sid=a.sid) blocker,
  a.sid,' is blocking ',
 (select username from v$session where sid=b.sid) blockee,
  b.sid
    from v$lock a, v$lock b
   where a.block = 1
     and b.request > 0
     and a.id1 = b.id1
     and a.id2 = b.id2;

--## Blocking Lock Advanced Query ##--

set pages 5000;
set lines 250;
col blocker format a25;
col blockee format a25;
col isblockin format a15;
select
  sblocker.username AS blocker
 ,blocker.sid
 ,sblocker.serial#
 ,'is blocking ' as isblockin
 ,sblockee.username AS blockee
 ,blockee.sid
 ,sblockee.seconds_in_wait secondsWait
from v$lock    blocker
    ,v$session sblocker
    ,v$lock    blockee
    ,v$session sblockee
where blocker.block = 1
and   blockee.request > 0
and   blocker.id1 = blockee.id1
and   blocker.id2 = blockee.id2
and   blocker.sid = sblocker.sid
and   blockee.sid = sblockee.sid;