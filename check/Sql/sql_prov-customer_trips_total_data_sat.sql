SELECT DISTINCT
    (drv.id::varchar)||'  /  '||(drv.ext_id::varchar) AS "Ид водителя"
    , CASE WHEN oo.driver_last_name is not NULL THEN (oo.driver_first_name::varchar)||' '||(oo.driver_last_name ::varchar)
    ELSE oo.driver_first_name
    END  "Имя водителя"
    , COUNT(oo.driver_id) AS Дуэт
    , CAST(((COUNT(oo.driver_id)/temp.cust_trips)*100) AS NUMERIC(6,0)) "Доля совместных поездок"
    , (MAX(to_timestamp(order_start_date)))::varchar AS "Время последней поездки"
    , ISNULL(CAST(SUM(сумма_доплаты)AS NUMERIC(8,0)), 0) "Сумма доплат"
FROM facts.FS_Orders oo  
LEFT JOIN facts.FS_Drivers drv
    ON drv.id = oo.driver_id
LEFT JOIN (
    SELECT DISTINCT
        order_id
        ,transaction_amount/100 AS сумма_доплаты
        FROM facts.FS_Drivers_balance_transaction
    WHERE transaction_type = 'Compensation'
    ) qwe
    ON qwe.order_id = oo.id
LEFT JOIN (
    SELECT DISTINCT
        customer_id, COUNT(1) as cust_trips 
    FROM facts.FS_Orders
    WHERE
        sub_state = 'ORDER_COMPLETED'
        AND customer_id = %s
    GROUP BY customer_id
    ) temp
    ON temp.customer_id = oo.customer_id
WHERE
    oo.customer_id = %s
    AND oo.driver_id IS NOT NULL
    AND sub_state = 'ORDER_COMPLETED'
GROUP BY
    "Ид водителя",
    "Имя водителя",
    temp.cust_trips
HAVING
    COUNT(oo.driver_id) >= 0