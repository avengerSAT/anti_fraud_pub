SELECT
	fo.id AS order_id
	, TO_TIMESTAMP(order_date) AS order_date
	, fo.launch_region_id
	, CAST(driver_id AS DECIMAL(10,0)) driver_id
	, rider_id AS customer_id
	, ('UNBLOCKED') AS state
	, pattern_name
	, ('UNVERIFIED') AS resolution
	, margin AS compensation
FROM facts.FS_Fraud_orders fo
LEFT JOIN (SELECT *
	FROM facts.FS_Fraud_orders_pattern fop
	LEFT JOIN facts.FS_Fraud_patterns fp
		ON fop.pattern_id = fp.id
	) fop
	ON fo.id = fop.order_id
LEFT JOIN (
	SELECT
		order_id
		, SUM(transaction_amount) / 100 AS margin
	FROM facts.FS_Drivers_balance_transaction
	WHERE 
		transaction_type IN ('Compensation', 'Order Refund', 'Promocode discount')
		AND order_id IS NOT NULL
	GROUP BY order_id
	) margin
	ON fo.id = margin.order_id
WHERE TO_TIMESTAMP(order_date) BETWEEN %s AND %s