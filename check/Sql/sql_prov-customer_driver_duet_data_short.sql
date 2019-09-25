SELECT DISTINCT
    oo.id AS ИД_поездки
    , oo.order_src_address AS Адрес_подачи
    , oo.order_dst_address AS Конечный_адрес
    , (to_timestamp(oo.order_start_date))::varchar AS Время_создания_заказа
    , (to_timestamp(oo.order_end_date))::varchar AS Время_окончания_поездки
    , oo.promo_code_description AS Промо
    , CAST(oo.promo_code_discount/100 AS DECIMAL(20,0))AS Номинал_промокода
    , CAST(dt.сумма_доплаты AS DECIMAL(4,0)) AS Сумма_доплаты
    , oo.sub_state AS Статус_поездки
FROM facts.FS_Orders oo
LEFT JOIN (
        SELECT
            order_id
            , transaction_amount / 100 AS сумма_доплаты
            FROM facts.FS_Drivers_balance_transaction
            WHERE transaction_type = 'Compensation'
        ) dt
        ON dt.order_id = oo.id
WHERE
    driver_id = %s
    AND customer_id = %s
    AND (sub_state = 'ORDER_COMPLETED' OR sub_state = 'CUSTOMER_CANCEL_AFTER_TRIP')