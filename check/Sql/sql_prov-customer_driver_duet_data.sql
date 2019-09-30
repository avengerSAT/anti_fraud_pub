WITH ids AS (
SELECT o.id FROM facts.FS_Orders o WHERE customer_id = %s
)
SELECT
    o.id AS "ИД поездки"
    , o.order_src_address AS "Адрес подачи"
    , o.order_dst_address AS "Конечный адрес"
    , o.arrive_time - o.order_start_date AS "Подача мин"
    , TO_TIMESTAMP(o.order_start_date) AS "Создание поездки"
    , TO_TIMESTAMP(o.order_end_date) AS "Финиш поездки"
    , ttl_time.trip_time AS "Время поездки мин"
    , ttl_time.trip_distance AS "Расстояние поездки"
    , promo.code AS "Промо код"
    , margin.margin AS Доплата
FROM facts.FS_Orders o
LEFT JOIN (
		SELECT
		    order_id
		    , time + long_time + country_time AS trip_time
		    , distance + long_distance + country_distance AS trip_distance
		FROM facts.FS_Orders_customer_cost ocs
		INNER JOIN ids
			ON ids.id = ocs.order_id
		WHERE cost_type = 'regular'
    	) ttl_time
        ON o.id = ttl_time.order_id
LEFT JOIN (
	SELECT order_id, code
	FROM facts.FS_Promo_codes_history pch
	INNER JOIN ids
		ON ids.id = pch.order_id
	INNER JOIN facts.FS_Promo_codes_activated pca
		ON pch.activated_promo_code_id = pca.id
		) promo
		ON promo.order_id = o.id
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
		ON o.id = margin.order_id
WHERE o.customer_id = %s AND o.driver_id = %s