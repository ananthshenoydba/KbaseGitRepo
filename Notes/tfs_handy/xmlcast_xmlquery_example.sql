select a.trade_date,
       a.id as "Internal Trade ID",
       u.external_id,
       xmlcast(xmlquery('declare namespace trades="http://www.tfs.com/energy/trades"; declare namespace strategies="http://www.tfs.com/energy/strategies"; /trades:Trade/trades:Details/strategies:Item/strategies:Broker.Description' passing a.xml returning content) as varchar2(100)) as "Contract Name",
       xmlcast(xmlquery('declare namespace trades="http://www.tfs.com/energy/trades"; declare namespace common="http://www.tfs.com/energy/common"; /trades:Trade/trades:Counterparties/common:Buyer[common:Code="MERC"]/common:Code' passing a.xml returning content) as varchar2(100)) as "Buyer",
       xmlcast(xmlquery('declare namespace trades="http://www.tfs.com/energy/trades"; declare namespace common="http://www.tfs.com/energy/common"; /trades:Trade/trades:Counterparties/common:Buyer[common:Code="MERC"]/common:Desk' passing a.xml returning content) as varchar2(100)) as "Desk (buyer)",
       xmlcast(xmlquery('declare namespace trades="http://www.tfs.com/energy/trades"; declare namespace common="http://www.tfs.com/energy/common"; /trades:Trade/trades:Counterparties/common:Buyer[common:Code="MERC"]/common:Brokers/common:Broker.Split/common:Broker.Code' passing a.xml returning content) as varchar2(100)) as "Broker (buyer)",
       xmlcast(xmlquery('declare namespace trades="http://www.tfs.com/energy/trades"; declare namespace common="http://www.tfs.com/energy/common"; /trades:Trade/trades:Counterparties/common:Buyer[common:Code="MERC"]/common:Brokerage/common:brokerage.amount/@Formatted' passing a.xml returning content) as varchar2(100)) as "Brokerage (buyer)",
       xmlcast(xmlquery('declare namespace trades="http://www.tfs.com/energy/trades"; declare namespace common="http://www.tfs.com/energy/common"; /trades:Trade/trades:Counterparties/common:Seller[common:Code="MERC"]/common:Code' passing a.xml returning content) as varchar2(100)) as "Seller",
       xmlcast(xmlquery('declare namespace trades="http://www.tfs.com/energy/trades"; declare namespace common="http://www.tfs.com/energy/common"; /trades:Trade/trades:Counterparties/common:Seller[common:Code="MERC"]/common:Desk' passing a.xml returning content) as varchar2(100)) as "Desk (seller)",
       xmlcast(xmlquery('declare namespace trades="http://www.tfs.com/energy/trades"; declare namespace common="http://www.tfs.com/energy/common"; /trades:Trade/trades:Counterparties/common:Seller[common:Code="MERC"]/common:Brokers/common:Broker.Split/common:Broker.Code' passing a.xml returning content) as varchar2(100)) as "Broker (seller)",
       xmlcast(xmlquery('declare namespace trades="http://www.tfs.com/energy/trades"; declare namespace common="http://www.tfs.com/energy/common"; /trades:Trade/trades:Counterparties/common:Seller[common:Code="MERC"]/common:Brokerage/common:brokerage.amount/@Formatted' passing a.xml returning content) as varchar2(100)) as "Brokerage (seller)"
from   trades_t a,
       trade_underlying_t u
where  exists (select 1 from trade_parties_t p
               where  p.prd_code = a.prd_code
               and    p.trd_id = a.id
               and    p.pty_org in ('MERC'))
--and    a.trade_date between to_date('01-may-2020','dd-mon-yyyy') and to_date('31-Jul-2020','dd-mon-yyyy')
and    a.id = 206501622 
and    a.prd_code = u.prd_code
and    a.id = u.trd_id
and    u.class = 'ELECTRICITY';