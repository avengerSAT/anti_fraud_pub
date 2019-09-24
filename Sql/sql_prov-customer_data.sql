SELECT DISTINCT
    CASE
    WHEN cc.last_name is not NULL THEN (cc.last_name::varchar)||' '||(cc.first_name ::varchar)
    ELSE cc.first_name
    END "Имя Клиента"
    , oo.customer_id
    , cc.email AS "Почта клиента"
    , oo.customer_phone AS "Телефон клиента"
    , CAST(cc.trip_number AS DECIMAL(4,0)) as "Количество поездок клиента"
    , CASE
    WHEN cc.status_reasons = '{}' THEN cc.status
    ELSE cc.status_reasons
    END "Статус"
FROM facts.FS_Orders oo
LEFT JOIN facts.FS_Customers cc ON oo.customer_id = cc.id
WHERE customer_id = %s 