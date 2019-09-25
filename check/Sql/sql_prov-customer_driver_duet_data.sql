SELECT
    o.id AS "ИД поездки"
    , CASE WHEN o.arrive_time - o.order_start_date < 60
    THEN CAST(o.arrive_time - o.order_start_date AS DECIMAL (5,2)) || ' sec'
    WHEN o.arrive_time - o.order_start_date IS NULL
    THEN ''
    ELSE CAST((o.arrive_time - o.order_start_date) / 60 AS DECIMAL (5,2)) || ' min'
    END "Подача мин"
    , TO_TIMESTAMP(o.order_start_date) AS "Старт поездки"
    , TO_TIMESTAMP(o.order_end_date) AS "Финиш поездки"
    , ISNULL(CAST(ttl_time.trip_time / 60000 AS DECIMAL (5,2)), 0) || ' min' "Время поездки мин"
    , ISNULL(CAST(ttl_time.trip_distance / 1000 AS DECIMAL (20,3)), 0) || ' km' "Расстояние поездки"
    , ISNULL(pca.code, 'Пусто') AS "Промо код"
    , CASE WHEN margin.margin IS NULL
    THEN 0
    ELSE CAST(margin.margin AS int)
    END Доплата
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