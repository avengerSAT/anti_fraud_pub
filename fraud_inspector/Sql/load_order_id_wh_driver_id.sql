SELECT
	oo.id AS order_id
	, TO_TIMESTAMP(oo.order_start_date) AS order_date
	, oo.launch_region_id
	, oo.driver_id
	, oo.customer_id AS customer_id
	, ('UNBLOCKED') AS state
	, (' ') AS pattern_name
	, ('UNVERIFIED') AS resolution
	, CAST(margin AS DECIMAL(10,0)) compensation
FROM facts.FS_Orders oo
LEFT JOIN (
	SELECT
		order_id
		,SUM(transaction_amount)/ 100 as margin
	FROM facts.FS_Drivers_balance_transaction
	WHERE 
		transaction_type NOT IN ('Fix Fare', 'Percent Fare')
		AND order_id IS NOT NULL
	GROUP BY order_id
	) margin
	ON oo.id = margin.order_id
WHERE TO_TIMESTAMP (oo.order_start_date) => %s 
	AND TO_TIMESTAMP(oo.order_start_date) =< %s 
	AND launch_region_id = %s  
	AND driver_id IN %s


	