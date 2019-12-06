SELECT DISTINCT
    gr.trip_number AS Дуэт
    , (to_timestamp(oo.arrive_time)-to_timestamp(oo.accept_time))::varchar AS  Подача
    , to_timestamp(oo.order_start_date+10800) AS "Старт поездки"
    , oo.order_src_address AS "Адрес подачи"
    , to_timestamp(oo.order_END_date+10800) AS "Время окончания поездки"
    , oo.order_dst_address AS "Конечный адрес"
    , oo.promo_code_description AS Промо
    , oo.promo_code_dIScount/100 AS "Номинал промокода"
    , (to_timestamp(oo.order_END_date)-to_timestamp(oo.order_start_date))::varchar AS "Время заказа"
    , oo.sub_state AS "Статус поездки"
    , oo.id AS "ИД поездки"
    , grs.trip_number AS "Кол поездок клиента"
    , oo.customer_id AS "ИД клиента"
    , cc.status AS Статус
    , CASE WHEN cc.last_name IS NOT NULL THEN (cc.last_name::varchar)||' '||(cc.first_name ::varchar) else cc.first_name END "Имя клиента"
    , cc.phone AS "Телефон клиента"
    , cc.email AS "Почта клиента"
    , (drv.id::varchar)||'  /  '||(drv.ext_id::varchar) AS "ИД водителя"
    , CASE WHEN pr.last_name IS NOT NULL THEN (pr.first_name::varchar)||' '||(pr.last_name ::varchar) else pr.first_name END "Имя водителя"
    , prs.email AS "Почта водителя"
    , pr.phone AS "Телефон водителя"
    , drv.promo_code AS "Промо водителя"
    , CASE WHEN cc.status_reasons IS NULL Then ' ' ELSE cc.status_reasons END "Статус р"
FROM facts.FS_Orders oo
LEFT JOIN facts.FS_Drivers drv ON oo.driver_id=drv.id
LEFT JOIN facts.FS_Profiles pr ON drv.profile_id = pr.id
LEFT JOIN facts.FS_Profiles_security prs ON pr.id = prs.id
LEFT JOIN facts.FS_Customers cc ON cc.id=oo.customer_id
LEFT JOIN facts.FS_Orders_customer_cost oc ON oc.order_id=oo.id
LEFT JOIN (
        SELECT
            customer_id
            , count (*) AS trip_number
            FROM facts.FS_Orders
            WHERE (sub_state = 'ORDER_COMPLETED' OR sub_state = 'CUSTOMER_CANCEL_AFTER_TRIP')
            GROUP BY customer_id
        ) grs
        ON grs.customer_id=oo.customer_id
LEFT JOIN (
        SELECT  DISTINCT
            customer_id
            , driver_id
            , count(*) AS trip_number
        FROM facts.FS_Orders 
        WHERE (sub_state = 'ORDER_COMPLETED' OR sub_state = 'CUSTOMER_CANCEL_AFTER_TRIP')
            AND driver_id = %s
        GROUP BY customer_id, driver_id
    ) gr
    ON gr.driver_id = oo.driver_id
        AND gr.customer_id = oo.customer_id
WHERE
    (sub_state = 'ORDER_COMPLETED' OR sub_state = 'CUSTOMER_CANCEL_AFTER_TRIP')
    AND oo.driver_id=%s