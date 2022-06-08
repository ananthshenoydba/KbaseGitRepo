/*select * from organisations_t where code like '9STREET.GTX'

select * from underlying_t where rownum < 10;

select 
t.*
from 
trade_parties_t tp join trades_t t on tp.trd_id=t.id 
and tp.pty_org = '9STREET.GTX' and t.deleted='N'*/

select xmlelement("REPORT",(
select
XMLELEMENT("ORGS",
XMLAGG(
    x.details order by x.code)
    ) 
from organisations x
where x.code in (
select y.org_code from trading_entities_classes y  , trading_entities f
where y.class_code = 'BOND.GOTTEX'
and y.code = f.code and y.org_code = f.org_code 
)

),(

select 
XMLAGG(
XMLELEMENT
    ("LAST_TRADE", 
        XMLELEMENT("ORG", g.pty_org),
        XMLELEMENT("LAST", max(g.trade_date))
    ) 
      ) 
from trd_select g 
where g.pty_org_entity in (
select a.code from trading_entities_classes a , trading_entities b
where a.class_code = 'BOND.GOTTEX'
and a.code = b.code and a.org_code = b.org_code 
)
group by g.pty_org
),
(
select 
xmlagg(
xmlelement
    ("Trades_dealt",
        xmlelement("ORG",tec.org_code),
        xmlelement("BOND_COUNT",count(t.id)),
        xmlelement("FUTURE_COUNT",count(tf.id))
    )
      ) 
from 
trading_entities_classes tec join trading_entities te
on tec.code = te.code and tec.org_code = te.org_code and tec.class_code = 'BOND.GOTTEX'
left join trade_parties tp on tp.pty_org = tec.org_code 
left join trades_t t on tp.trd_id=t.id and t.deleted='N' and t.descr='BOND' 
left join trades_t tf on tp.trd_id=tf.id and tf.deleted='N' and tf.descr='FUTURE'
group by tec.org_code
)
,
(
    select XMLAGG(XMLELEMENT("CREATED", XMLELEMENT("ORG", y.code),XMLELEMENT("FIRST", min(y.changed)))) from organisations_history_t y 
    where y.code like '%.GTX'
    group by y.code
 )
)
from dual