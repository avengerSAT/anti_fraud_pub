WITH ids AS (
SELECT
    oo.id
    , oo.driver_id
    , CASE WHEN oo.driver_last_name is not NULL THEN (oo.driver_first_name::varchar)||' '||(oo.driver_last_name ::varchar)
    ELSE oo.driver_first_name
    END drv_name
    , TO_TIMESTAMP(order_start_date+10800)::varchar start_date
    FROM facts.FS_Orders oo
    WHERE oo.customer_id = %s
    )
SELECT
	ids.id "Ид заказа"
	, (drv.id::varchar)||'  /  '||(drv.ext_id::varchar) AS "Ид водителя"
	, ids.drv_name "Имя водителя"
	, ids.start_date "Начало поездки"
	, ISNULL(margin.margin, 0)::integer AS "Доплата"
FROM ids
LEFT JOIN facts.FS_Drivers drv
    ON drv.id = ids.driver_id
LEFT JOIN (
	    SELECT
	        order_id
	        , SUM(transaction_amount) / 100 AS margin
	    FROM facts.FS_Drivers_balance_transaction
	    INNER JOIN ids
	    	ON ids.id = order_id
	    WHERE transaction_type NOT IN ('Fix Fare', 'Percent Fare')
	        AND order_id IS NOT NULL
	    GROUP BY order_id
	    ) margin
		ON ids.id = margin.order_id
GROUP BY
	ids.id
	, ids.drv_name
	, ids.start_date
	, drv.id
	, drv.ext_id
	, margin.margin
