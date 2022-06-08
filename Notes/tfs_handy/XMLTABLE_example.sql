select 
t.id
,t.trade_date
,x.*
--,xml.EXTRACTVAL(t.xml, '/trades:Trade/trades:Details/strategies:Counterparties/*', xml.getns (vc50_ct ('NS_TRADES', 'NS_STRATEGIES', 'NS_COMMON' ))) as OptionX
from trades_t t, 
     XMLTABLE(xmlnamespaces('http://www.tfs.com/equity.derivatives/common' as "common",
                'http://www.tfs.com/equity.derivatives/trades' as "trades",
                'http://www.tfs.com/equity.derivatives/strategies' as "strategies"), 
              'for $i in /trades:Trade/trades:Details/strategies:Counterparties/* return $i'
        passing t.xml
        columns
            buyer_or_seller VARCHAR(255) path './local-name(.)',
            buyer_code      varchar2(255) path './common:Code'
        ) x
where t.id=2021000017


select * from requests_t where lower(source) like '%xmltable%xmlnamespace%'