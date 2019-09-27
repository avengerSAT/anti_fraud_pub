SELECT
    o.id AS "ИД поездки"
    , o.order_src_address AS "Адрес подачи"
    , o.order_dst_address AS "Конечный адрес"
    , o.arrive_time - o.order_start_date AS "Подача мин"
    , TO_TIMESTAMP(o.order_start_date) AS "Создание поездки"
    , TO_TIMESTAMP(o.order_end_date) AS "Финиш поездки"
    , ttl_time.trip_time AS "Время поездки мин"
    , ttl_time.trip_distance AS "Расстояние поездки"
    , pca.code AS "Промо код"
    , margin.margin AS Доплата
FROM facts.FS_Orders o
LEFT JOIN (
    SELECT
        order_id
        , time + long_time + country_time AS trip_time
        , distance + long_distance + country_distance AS trip_distance
    FROM facts.FS_Orders_customer_cost
    WHERE cost_type = 'regular') ttl_time
        ON o.id = ttl_time.order_id
LEFT JOIN facts.FS_Promo_codes_history pch
ON o.id = pch.order_id
LEFT JOIN facts.FS_Promo_codes_activated pca
ON pch.activated_promo_code_id = pca.id
LEFT JOIN (
    SELECT
        order_id
        , SUM(transaction_amount) / 100 AS margin
    FROM facts.FS_Drivers_balance_transaction
    WHERE driver_id = %s
        AND transaction_type NOT IN ('Fix Fare', 'Percent Fare')
        AND order_id IS NOT NULL
    GROUP BY order_id) margin
ON o.id = margin.order_id
WHERE o.customer_id = %s AND o.driver_id = %s