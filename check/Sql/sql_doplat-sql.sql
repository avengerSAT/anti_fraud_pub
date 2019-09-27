SELECT DISTINCT
    region_id AS "ИД региона"
    ,(to_timestamp(oo.order_start_date)::date)::varchar As "Дата проверки"
    ,COUNT(dt.order_id) AS "Количество поездок с компенсацией"
    ,CAST(SUM(transaction_amount/100)AS DECIMAL(14,0)) AS "Сумма компенсации"
    ,CAST(SUM(CASE WHEN qwe.Сумма_списаний_за_поездку IS NULL THEN '0' ELSE qwe.Сумма_списаний_за_поездку END) AS DECIMAL(14,0)) AS "Сумма списаний"
    ,CAST(SUM(dt.transaction_amount/100+(CASE WHEN qwe.Сумма_списаний_за_поездку IS NULL THEN '0' ELSE qwe.Сумма_списаний_за_поездку END)) AS DECIMAL(14,0)) as "Сумма после проверки"
FROM facts.FS_Drivers_balance_transaction dt
LEFT JOIN facts.FS_Orders oo
    ON dt.order_id=oo.id
LEFT JOIN (
        SELECT DISTINCT
            dt.order_id,
            SUM(transaction_amount/100) AS Сумма_списаний_за_поездку
        FROM facts.FS_Drivers_balance_transaction dt
        LEFT JOIN (
                SELECT
                    o.id AS order_id
                FROM facts.FS_Orders o
                LEFT JOIN facts.FS_Fraud_orders fo
                    ON o.id = fo.id
                LEFT JOIN facts.FS_Fraud_verifies fv
                    ON fo.id = fv.order_id
                LEFT JOIN (
                    SELECT MAX(id) id
                        , order_pattern_id
                        , resolution
                        , session_id
                    FROM facts.FS_Fraud_resolutions
                    WHERE resolution IS NOT NULL
                    GROUP BY order_pattern_id, resolution, session_id
                    ) fr
                    ON fv.id = fr.session_id
                WHERE resolution = 'YES'
            ) gr_1
            ON gr_1.order_id=dt.order_id
        WHERE transaction_type='Order Refund'
        AND gr_1.order_id IS NOT NULL
        GROUP BY dt.order_id
    ) qwe
    ON qwe.order_id= dt.order_id
WHERE 1=1
 	 AND transaction_type='Compensation'
 	 AND to_timestamp(oo.order_start_date)::date IS NOT NULL
 	 AND to_timestamp(oo.order_start_date)::date >= %s
 	 AND to_timestamp(oo.order_start_date)::date <= %s
GROUP BY "ИД региона", "Дата проверки"