with tradedataraw as
(
select 
t.id
,t.trade_date
,tu.country
,xml.EXTRACTVAL(t.xml, '/trades:Trade/trades:Details/strategies:Underlying/common:Reuters', xml.getns (vc50_ct ('NS_TRADES','NS_STRATEGIES','NS_COMMON'))) as RIC
,xml.EXTRACTVAL(t.xml, '/trades:Trade/trades:Details/strategies:Underlying/common:Description', xml.getns (vc50_ct ('NS_TRADES','NS_STRATEGIES','NS_COMMON'))) as Description
,tu.class
,tu.style
,tu.strategy
,tb.desk_code
,tp.pty_org
,tp.side
/*,case when tp.side='B' then xml.EXTRACTVAL(t.xml, '/trades:Trade/trades:Details/strategies:Counterparties/common:Buyer/common:Additional.Info/common:Option.Crossed', xml.getns (vc50_ct ('NS_TRADES', 'NS_STRATEGIES', 'NS_COMMON' )))
when tp.side='S' then xml.EXTRACTVAL(t.xml, '/trades:Trade/trades:Details/strategies:Counterparties/common:Seller/common:Additional.Info/common:Option.Crossed', xml.getns (vc50_ct ('NS_TRADES', 'NS_STRATEGIES', 'NS_COMMON' )))
end as OPTN_X
*/
,xml.EXTRACTVAL(t.xml, '/trades:Trade/trades:Interest/trades:Size', xml.getns (vc50_ct ('NS_TRADES'))) as Volume
,xml.EXTRACTVAL(t.xml, '/trades:Trade/trades:Details/strategies:Underlying/common:Contract_Size', xml.getns (vc50_ct ('NS_TRADES', 'NS_STRATEGIES', 'NS_COMMON' ))) as Multiplier
from trades_t t 
join trade_underlying_t tu on t.id=tu.trd_id
join trade_brokers_t tb on t.id=tb.trd_id
join trade_parties_t tp on t.id=tp.trd_id and tp.pty_org=tb.pty_org and tp.side in ('B','S')
where
t.deleted='N'
and t.EXT_IB is NULL
and t.trade_type in ('trades:vanilla','trades:trade.ticket.futures', 'trades:trade.ticket.divfuture') 
and tu.country='ITALY'
and t.id in (2022032680)
and t.trade_date between  TRUNC(LAST_DAY(ADD_MONTHS (sysdate, -2))+1) and trunc(LAST_DAY(LAST_DAY (ADD_MONTHS (sysdate, -2))+1))
and xml.EXTRACT (t.xml,'/trades:Trade/trades:Details/strategies:Counterparties/*/common:Additional.Info/common:Option.Crossed/text()', 
                  xml.getns (vc50_ct ('NS_TRADES','NS_STRATEGIES','NS_COMMON' ))) LIKE '%Yes%' 
),
pricedatafuturesoutright as
(
select 
t.id,
x.price,
y.common_code,
y.volume
from trades_t t join trade_underlying_t tu on t.id=tu.trd_id 
and t.trade_date between  TRUNC(LAST_DAY(ADD_MONTHS (sysdate, -2))+1) and trunc(LAST_DAY(LAST_DAY (ADD_MONTHS (sysdate, -2))+1)) 
and t.deleted='N'
and t.EXT_IB is NULL
and TU.style='FUTURES'
and TU.strategy='OUTRIGHT' 
--and t.id in (2022000213, 2022007495, 2022007496)
and tu.country='ITALY', 
     XMLTABLE(xmlnamespaces('http://www.tfs.com/equity.derivatives/common' as "common",
                'http://www.tfs.com/equity.derivatives/trades' as "trades",
                'http://www.tfs.com/equity.derivatives/strategies' as "strategies"), 
              'for $i in /trades:Trade/trades:Details/strategies:Strategy/strategies:Legs/* return $i'
        passing t.xml
        columns
            direction VARCHAR(255) path '/*/strategies:Direction',
            price varchar2(255) path '/*/strategies:Price/text()') x,
     XMLTABLE(xmlnamespaces('http://www.tfs.com/equity.derivatives/common' as "common",
                'http://www.tfs.com/equity.derivatives/trades' as "trades",
                'http://www.tfs.com/equity.derivatives/strategies' as "strategies"), 
              'for $i in /trades:Trade/trades:Details/strategies:Counterparties/* return $i'
        passing t.xml
        columns
            buyer_or_seller VARCHAR(255) path './local-name(.)',
            Common_code VARCHAR(255) path '/*/common:Code',
            option_x VARCHAR(255) path '/*/common:Additional.Info/common:Option.Crossed',
            Volume VARCHAR(255) path '/*/common:Allocation/common:Trade.Volume'
            ) y
where x.direction=1 and y.option_x='Yes' and y.buyer_or_seller='Buyer'
)
,
pricedatafuturesspread as
(
select a.id, a.price, a.common_code, a.volume from (
select 
t.id
,
case 
    when x.direction=1 then 'Buyer'
    when x.direction=-1 then 'Seller'
 end as side,
x.price,
y.*
from trades_t t join trade_underlying_t tu on t.id=tu.trd_id 
and t.trade_date between  TRUNC(LAST_DAY(ADD_MONTHS (sysdate, -2))+1) and trunc(LAST_DAY(LAST_DAY (ADD_MONTHS (sysdate, -2))+1)) 
and t.deleted='N'
and t.EXT_IB is NULL
and TU.style='FUTURES'
and TU.strategy='FUTURES SPREAD' 
and tu.country='ITALY', 
XMLTABLE(xmlnamespaces('http://www.tfs.com/equity.derivatives/common' as "common",
            'http://www.tfs.com/equity.derivatives/trades' as "trades",
            'http://www.tfs.com/equity.derivatives/strategies' as "strategies"), 
              'for $i in /trades:Trade/trades:Details/strategies:Strategy/strategies:Legs/* return $i'
                passing t.xml
                    columns
                        direction VARCHAR(255) path '/*/strategies:Direction',
                        price varchar2(255) path '/*/strategies:Price/text()'
        ) x
        ,
XMLTABLE(xmlnamespaces('http://www.tfs.com/equity.derivatives/common' as "common",
                'http://www.tfs.com/equity.derivatives/trades' as "trades",
                'http://www.tfs.com/equity.derivatives/strategies' as "strategies"), 
              'for $i in /trades:Trade/trades:Details/strategies:Counterparties/* return $i'
        passing t.xml
        columns
            b_or_s VARCHAR(255) path './local-name(.)',
            Common_code VARCHAR(255) path '/*/common:Code',
            option_x VARCHAR(255) path '/*/common:Additional.Info/common:Option.Crossed',
            Volume VARCHAR(255) path '/*/common:Allocation/common:Trade.Volume'
            ) y
where y.option_x='Yes') a where a.side=a.b_or_s
),
vanillaconversion as
(
select a.id, a.price, a.common_code, a.volume from (
select 
t.id
,case 
    when x.direction=1 then 'Buyer'
    when x.direction=-1 then 'Seller'
 end as side
,x.*
,y.*
from trades_t t join trade_underlying_t tu on t.id=tu.trd_id 
and t.trade_date between  TRUNC(LAST_DAY(ADD_MONTHS (sysdate, -2))+1) and trunc(LAST_DAY(LAST_DAY (ADD_MONTHS (sysdate, -2))+1)) 
and t.deleted='N'
and t.EXT_IB is NULL
and TU.style='LISTED'
and TU.strategy='CONVERSION'
and t.id in (2022032680)
and tu.country='ITALY', 
XMLTABLE(xmlnamespaces('http://www.tfs.com/equity.derivatives/common' as "common",
            'http://www.tfs.com/equity.derivatives/trades' as "trades",
            'http://www.tfs.com/equity.derivatives/strategies' as "strategies"), 
              'for $i in /trades:Trade/trades:Details/strategies:Strategy/strategies:Legs.1/* return $i'
                passing t.xml
                    columns
                        direction VARCHAR(255) path '/*/strategies:Direction',
                        price varchar2(255) path '/*/strategies:price.per.option'
        ) x
        ,
XMLTABLE(xmlnamespaces('http://www.tfs.com/equity.derivatives/common' as "common",
                'http://www.tfs.com/equity.derivatives/trades' as "trades",
                'http://www.tfs.com/equity.derivatives/strategies' as "strategies"), 
              'for $i in /trades:Trade/trades:Details/strategies:Counterparties/* return $i'
        passing t.xml
        columns
            b_or_s VARCHAR(255) path './local-name(.)',
            Common_code VARCHAR(255) path '/*/common:Code',
            option_x VARCHAR(255) path '/*/common:Additional.Info/common:Option.Crossed',
            Volume VARCHAR(255) path '/*/common:Allocation/common:Trade.Volume'
            ) y
where y.option_x='Yes' /*and x.direction=1*/) a where a.side=a.b_or_s
),
rawdata as 
(
select 
a.ID
,a.TRADE_DATE
,a.country
,a.ric
,a.description
,a.class
,a.style
,a.desk_code
,a.pty_org
,a.strategy
--,a.side
,case when b.volume is not null then b.volume
    else a.volume
end as volume
,a.multiplier
, b.price 
from 
tradedataraw a join pricedatafuturesoutright b on a.id=b.id and a.pty_org=b.common_code 
union
select 
a.ID
,a.TRADE_DATE
,a.country
,a.ric
,a.description
,a.class
,a.style
,a.desk_code
,a.pty_org
,a.strategy
--,a.side
,case when b.volume is not null then b.volume
      else a.volume
 end as volume
,a.multiplier
, b.price 
from 
tradedataraw a join pricedatafuturesspread b on a.id=b.id and a.pty_org=b.common_code
union 
select 
a.ID
,a.TRADE_DATE
,a.country
,a.ric
,a.description
,a.class
,'VANILLA' as style
,a.desk_code
,a.pty_org
,a.strategy
--,a.side
,case when b.volume is not null then b.volume
    else a.volume
end as volume
,a.multiplier
, b.price 
from 
tradedataraw a join vanillaconversion b on a.id=b.id and a.pty_org=b.common_code)
select a.*, a.volume*a.multiplier*a.price as premium from rawdata a