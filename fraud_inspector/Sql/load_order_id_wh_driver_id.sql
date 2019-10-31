SELECT
	oo.id AS order_id
	, TO_TIMESTAMP(oo.order_start_date) AS order_date
	, oo.launch_region_id
	, oo.driver_id
	, oo.customer_id AS customer_id
	, ('UNBLOCKED') AS state
	, (' ') AS pattern_name
	, ('UNVERIFIED') AS resolution
	, case WHEN margin is NULL   THEN 0 ELSE margin end compensation
FROM facts.FS_Orders oo
LEFT JOIN (
	SELECT
		order_id
		,SUM(transaction_amount)/ 100 as margin
	FROM facts.FS_Drivers_balance_transaction
	WHERE 
		transaction_type IN ('Compensation', 'Order Refund', 'Promocode discount')
		AND order_id IS NOT NULL
	GROUP BY order_id
	) margin
	ON oo.id = margin.order_id
WHERE TO_TIMESTAMP () > %s 
	AND TO_TIMESTAMP() < %s 
	AND launch_region_id = %s , 
	AND driver_id IN %s