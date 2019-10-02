WITH args AS (
SELECT
	CAST(20190909 AS INTEGER) date_from
	, CAST(20190920 AS INTEGER) date_to
	, CAST(8652 AS INTEGER) city_id)
SELECT
	id AS "Ид заказа"
	, TO_TIMESTAMP(order_date) AS "Дата"
	, city
	, CAST(driver_id AS DECIMAL(20,0))
	, rider_id
	, state
	, ISNULL(margin.margin, 0) AS "Доплата"
FROM facts.FS_Fraud_orders fo
LEFT JOIN args ON TRUE
LEFT JOIN (
	SELECT
		order_id
		, SUM(transaction_amount) / 100 AS margin
	FROM facts.FS_Drivers_balance_transaction
	WHERE 
		transaction_type NOT IN ('Fix Fare', 'Percent Fare')
		AND order_id IS NOT NULL
	GROUP BY order_id
	) margin
	ON fo.id = margin.order_id
WHERE
--	launch_region_id = city_id
	TO_TIMESTAMP(order_date) > (CURRENT_DATE - 14)
	AND margin.margin > 0
	AND state = 'UNVERIFIED'
ORDER BY "Дата" ASC