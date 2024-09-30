select 
session.client_addr
,session.datname
,session.usename
,session.state
,session.backend_start
,session.backend_type
,case when ssl_status.ssl then 'Yes' else 'No' end as ssl_in_use
,ssl_status.version
,ssl_status.cipher
from
pg_stat_activity session
left join pg_roles role
on role.oid = session.usesysid
left join pg_stat_ssl ssl_status
on ssl_status.pid = session.pid
where
session.client_addr = inet_client_addr()
and session.client_port = inet_client_port();

--INSERT INTO processing.inbound_control_state (system, data_collection, extraction_timestamp, status ) VALUES ('psd', 'tests', current_timestamp, 'IN-PROGRESS');

select system, data_collection, to_char(extraction_timestamp, 'yyyymmdd hh:mi:ss tt') extraction_timestamp, status from processing.inbound_control_state;