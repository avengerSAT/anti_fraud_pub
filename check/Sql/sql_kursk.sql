SELECT DISTINCT
drv.id as driver_id,
drv.ext_id as d_driver_id,
ffo.id as order_id,
dbt.transaction_amount as comp,
dbt2.transaction_amount as spis,
gr.count_orders 
From facts.FS_Fraud_orders ffo
left join (
SELECT
order_id,
transaction_amount/100 as transaction_amount
FROM facts.FS_Drivers_balance_transaction
where transaction_type in ('Compensation')) dbt
on dbt.order_id=ffo.id
left join (
SELECT
order_id,
transaction_amount/100 as transaction_amount
FROM facts.FS_Drivers_balance_transaction
where transaction_type in ('Order Refund')) dbt2
on dbt2.order_id=ffo.id
left JOIN facts.FS_Drivers drv
on drv.id=ffo.driver_id
left join (
SELECT
driver_id,
COUNT(id) as count_orders
from facts.FS_Orders
WHERE sub_state in ('ORDER_COMPLETED')
	AND (TO_TIMESTAMP(order_end_date+10800) BETWEEN %s AND %s )
GROUP BY driver_id) gr
on gr.driver_id=ffo.driver_id
WHERE ffo.launch_region_id= 4712
	AND (TO_TIMESTAMP(ffo.order_date+10800) BETWEEN %s AND %s )

	