SELECT
    gr.qwe AS Количество_успешных_заказов
    ,gr_1.qwer AS Количество_заказов_отмеченных_как_фрод
    ,gr.qwe-gr_1.qwer AS Количество_поездок_без_нарушений 
FROM (
    SELECT 
    driver_id
    , count(id) AS qwe
    FROM facts.FS_Orders oo 
    WHERE
        1=1
        AND sub_state = 'ORDER_COMPLETED'
        AND driver_id = %s
        AND to_timestamp(oo.order_end_date+10800)::date >=%s
        AND to_timestamp(oo.order_end_date+10800)::date <=%s
    GROUP BY driver_id) gr 
LEFT JOIN (
    SELECT
        COUNT(DISTINCT o.id) AS qwer
        , o.driver_id
    FROM facts.FS_Orders o
    LEFT JOIN facts.FS_Fraud_orders fo
        ON o.id = fo.id
    LEFT JOIN facts.FS_Fraud_verifies fv
        ON fo.id = fv.order_id
    LEFT JOIN (
        SELECT
            MAX(id) id
            , order_pattern_id
            , resolution
            , session_id
        FROM facts.FS_Fraud_resolutions
        WHERE resolution IS NOT NULL
        GROUP BY order_pattern_id, resolution,session_id
        ) fr
        ON fv.id = fr.session_id
WHERE
    fr.resolution='YES'
    AND o.driver_id=%s
    AND to_timestamp(fo.order_date+10800)::date >=%s
    AND to_timestamp(fo.order_date+10800)::date <=%s
GROUP BY o.driver_id
    ) gr_1
    ON gr_1.driver_id =gr.driver_id