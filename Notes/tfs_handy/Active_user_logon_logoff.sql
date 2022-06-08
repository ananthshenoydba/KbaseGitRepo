with enabled as
(
select 
a.person_code, a.name, a.type
from 
people_t a 
where a.person_org='TF2' 
and a.location='SG' 
and a.status=0
),
logonactivity as
(
select 
a.person_code, a.name, a.type,
max(b.action_time) LAST_LOGON
from 
people_t a 
left join session_details_history_t b on a.person_code=b.user_code 
where a.person_org='TF2' 
and a.location='SG' 
and a.status=0
--and b.action_time > '01-NOV-21'
--and a.person_code='AUGUSTINEY'
and b.action='ON'
group by a.person_code, a.name, a.type
),
logoffactivity as
(
select 
a.person_code, a.name, a.type,
max(b.action_time) LAST_LOGOFF
from 
people_t a 
left join session_details_history_t b on a.person_code=b.user_code 
where a.person_org='TF2' 
and a.location='SG' 
and a.status=0
--and b.action_time > '01-NOV-21'
--and a.person_code='AUGUSTINEY'
and b.action='OFF'
group by a.person_code, a.name, a.type
)
select a.*, b.last_logon, c.LAST_LOGOFF
from enabled a 
left join logonactivity b on a.person_code=b.person_code 
left join logoffactivity c on a.person_code=c.person_code 
order by 1

--select * from session_details_history_t where user_code='SG_BRO'

--select * from people_t where person_code='SG_BRO'