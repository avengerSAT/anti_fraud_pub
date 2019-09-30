SELECT
    CASE
    WHEN cc.last_name is not NULL THEN (cc.last_name::varchar)||' '||(cc.first_name ::varchar)
    ELSE cc.first_name
    END "Имя Клиента"
    , cc.id
    , cc.email AS "Почта клиента"
    , oo.customer_phone AS "Телефон клиента"
    , cc.trip_number::varchar AS "Количество поездок клиента"
    , CASE
    WHEN cc.status_reasons = '{}' THEN cc.status
    ELSE cc.status_reasons
    END "Статус"
FROM facts.FS_Customers cc
INNER JOIN (
	SELECT customer_id, customer_phone, ROW_NUMBER() OVER(PARTITION BY customer_id) AS rnk
	FROM facts.FS_Orders
	) oo
	ON cc.id = oo.customer_id AND rnk = 1
WHERE cc.id = %s
