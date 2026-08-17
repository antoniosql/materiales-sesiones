SELECT CustomerKey

  ,rfm_recency
  ,rfm_frequency
  ,rfm_monetary
  ,(rfm_recency * rfm_frequency * rfm_monetary) rfm_Score_Classic
  ,cast(round(((3*rfm_recency) + (2*rfm_frequency) + rfm_monetary)*3.3,0) as int) rfm_Score_New
  ,cast(cast(rfm_recency as varchar)+''+cast(rfm_frequency as varchar)+''+cast(rfm_monetary as varchar)as int) rfm_Score_Concat
  ,ceiling(cast(rfm_recency + rfm_frequency + rfm_monetary AS FLOAT) / cast(3 AS FLOAT)) rfm_avg
FROM (
  SELECT CustomerKey,
    
    case when last_order_date>FORMAT(dateadd(DAY, - 15, cast('20140209' as date)), 'yyyyMMdd') then 5
    when last_order_date<=FORMAT(dateadd(DAY, - 15, cast('20140209' as date)), 'yyyyMMdd') and last_order_date>FORMAT(dateadd(DAY, - 45, cast('20140209' as date)), 'yyyyMMdd') then 4
    when last_order_date<=FORMAT(dateadd(DAY, - 45, cast('20140209' as date)), 'yyyyMMdd') and last_order_date>FORMAT(dateadd(MONTH, - 3, cast('20140209' as date)), 'yyyyMMdd') then 3
    when last_order_date<=FORMAT(dateadd(MONTH, - 3, cast('20140209' as date)), 'yyyyMMdd') and last_order_date>FORMAT(dateadd(MONTH, - 6, cast('20140209' as date)), 'yyyyMMdd') then 2
    when last_order_date<=FORMAT(dateadd(MONTH, - 6, cast('20140209' as date)), 'yyyyMMdd') and last_order_date>FORMAT(dateadd(MONTH, - 24, cast('20140209' as date)), 'yyyyMMdd') then 1 
      end as rfm_recency
    ,case when count_order=1 then 1
    when count_order=2  then 2
    when count_order=3 then 3
    when count_order between 4 and 6 then 4
    when count_order>=7 then 5
      end AS rfm_frequency
    ,case when avg_amount<150 then 1
    when avg_amount>=150 and avg_amount<2000 then 2
    when avg_amount>=2000 and avg_amount<2650 then 3
    when avg_amount>=2650 and avg_amount<3500 then 4
    when avg_amount>=3500  then 5 end AS rfm_monetary
  FROM (
    SELECT CustomerKey
      ,max(OrderDateKey) AS last_order_date
      ,count(*) AS count_order
      ,avg([SalesAmount]) AS avg_amount
    FROM FactInternetSales Sa
    WHERE OrderDateKey > FORMAT(dateadd(YEAR, - 2, cast('20140209' as date)), 'yyyyMMdd')
    GROUP BY CustomerKey
    ) a
  ) b;