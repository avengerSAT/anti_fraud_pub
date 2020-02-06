SELECT DISTINCT
drv.id as driver_id,
drv.ext_id as d_driver_id,
fo.id as order_id,
dbt.transaction_amount as comp,
dbt2.transaction_amount as spis,
gr.count_orders
From facts.FS_Orders fo
left join (
SELECT
order_id,
transaction_amount/100 as transaction_amount
FROM facts.FS_Drivers_balance_transaction
where transaction_type in ('Compensation')) dbt
on dbt.order_id=fo.id
left join (
SELECT
order_id,
transaction_amount/100 as transaction_amount
FROM facts.FS_Drivers_balance_transaction
where transaction_type in ('Order Refund')) dbt2
on dbt2.order_id=fo.id
left JOIN facts.FS_Drivers drv
on drv.id=fo.driver_id
left join (
SELECT
driver_id,
COUNT(id) as count_orders
from facts.FS_Orders
WHERE sub_state in ('ORDER_COMPLETED')
	AND (TO_TIMESTAMP(order_end_date) BETWEEN %s AND %s )
GROUP BY driver_id) gr
on gr.driver_id=fo.driver_id
WHERE fo.id in %s



	