class sql_vert():
    # ИД КЛИЕНТА, длинный ИД ВОДИТЕЛЯ, короткий ИД ВОДИТЕЛЯ через ИД ПОЕЗДКИ
    sql = """ 
    SELECT DISTINCT
    dd.ext_id
    ,oo.customer_id
    ,oo.driver_id
    FROM facts.FS_Orders oo 
    left JOIN facts.FS_Drivers dd 
    on oo.driver_id = dd.id
    where oo.id=%s
    """   
    # Данные Клиента через ИД КЛИЕНТА
    sql_1 = """ 
    SELECT DISTINCT
    case WHEN cc.last_name is not NULL THEN (cc.last_name::varchar)||' '||(cc.first_name ::varchar) else cc.first_name end  Имя_Клиента
    ,oo.customer_id
    ,cc.email AS почта_клиента
    ,oo.customer_phone AS телефон_клиента
    ,CAST(cc.trip_number AS DECIMAL(4,0)) as Количество_поездок_клиента
    ,case when cc.status_reasons = '{}' then cc.status else cc.status_reasons end Статус
    FROM facts.FS_Orders oo
    LEFT JOIN facts.FS_Customers cc ON oo.customer_id=cc.id
    WHERE customer_id=%s 
    """
    #Данные Водителя через длинный ИД ВОДИТЕЛЯ
    sql_2 = """ 
    SELECT DISTINCT
    case WHEN last_name is not NULL THEN (first_name::varchar)||' '||(last_name ::varchar) else first_name end  Имя_водителя
    ,(drv.id::varchar)||'  /  '||(drv.ext_id::varchar) as driver_id
    ,prs.email AS почта_водителя
    ,pr.phone AS телефон_водителя
    ,drv.promo_code AS промокод_водителя
    FROM facts.FS_Profiles pr
    LEFT JOIN facts.FS_Drivers drv ON drv.profile_id = pr.id
    LEFT JOIN facts.FS_Profiles_security prs ON pr.id = prs.id
    WHERE drv.ext_id = %s
    """
    # Сводные данные о поездках клиента
    sql_3 = """
    SELECT DISTINCT
    (drv.id::varchar)||'  /  '||(drv.ext_id::varchar) as Ид_водителя
    ,case WHEN oo.driver_last_name is not NULL THEN (oo.driver_first_name::varchar)||' '||(oo.driver_last_name ::varchar) else oo.driver_first_name end  Имя_водителя
    ,COUNT(oo.driver_id) AS Дуэт
    ,CAST(((COUNT(oo.driver_id)/temp.cust_trips)*100) AS NUMERIC(6,0)) Доля_совместных_поездок
    ,(MAX(to_timestamp(order_start_date)))::varchar AS Время_последней_поездки
    ,CAST(SUM(сумма_доплаты)AS NUMERIC(8,0)) as Сумма_доплат
    FROM facts.FS_Orders oo  
    LEFT JOIN facts.FS_Drivers drv ON drv.id = oo.driver_id
    LEFT JOIN (
    SELECT DISTINCT
    order_id
    ,transaction_amount/100 as сумма_доплаты
    from facts.FS_Drivers_balance_transaction
    WHERE  transaction_type='Compensation'
    ) qwe ON qwe.order_id = oo.id
    LEFT JOIN (
    SELECT DISTINCT
    customer_id, count(customer_id) as cust_trips 
    FROM facts.FS_Orders
    WHERE sub_state = 'ORDER_COMPLETED' AND customer_id = %s
    GROUP BY customer_id
    ) temp ON temp.customer_id = oo.customer_id
    WHERE oo.customer_id = %s and oo.driver_id is not NULL and sub_state = 'ORDER_COMPLETED'
    GROUP BY Ид_водителя ,Имя_водителя,temp.cust_trips
    HAVING
    COUNT(oo.driver_id) >= 0
    ORDER BY
    Дуэт DESC
    """
    # Данные о совместных поездках вариант 1
    sql_4 = """
    SELECT DISTINCT
    oo.id as ИД_поездки
    ,oo.order_src_address as Адрес_подачи
    ,oo.order_dst_address as Конечный_адрес
    ,(to_timestamp(oo.order_start_date))::varchar as Время_создания_заказа
    ,(to_timestamp(oo.order_end_date))::varchar as Время_окончания_поездки
    ,oo.promo_code_description as Промо
    ,CAST(oo.promo_code_discount/100 AS DECIMAL(20,0))as Номинал_промокода
    ,CAST(dt.сумма_доплаты AS DECIMAL(4,0)) as Сумма_доплаты
    ,oo.sub_state as Статус_поездки
    FROM facts.FS_Orders oo
    LEFT JOIN (select order_id,transaction_amount/100 as сумма_доплаты from facts.FS_Drivers_balance_transaction WHERE transaction_type='Compensation') dt 
    on dt.order_id = oo.id
    WHERE driver_id=%s and customer_id=%s and (sub_state = 'ORDER_COMPLETED' OR sub_state = 'CUSTOMER_CANCEL_AFTER_TRIP')
    """
    # Данные о совместных поездках вариант 2
    sql_5="""
    SELECT
    o.id AS ИД_поездки
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
    """
    # Информация о списанных средствах (по фроду)
    sql_6 = """
    SELECT DISTINCT
    region_id as Город
    ,(to_timestamp(oo.order_start_date)::date)::varchar as Дата_проверки
    ,COUNT(dt.order_id) as Количество_поездок_с_компенсацией
    ,CAST(SUM(transaction_amount/100)AS DECIMAL(14,0)) as Сумма_компенсации
    ,CAST(SUM(case WHEN qwe.Сумма_списаний_за_поездку is NULL THEN '0' else qwe.Сумма_списаний_за_поездку end )AS DECIMAL(14,0)) as Сумма_списаний
    ,CAST(SUM(dt.transaction_amount/100+(case WHEN qwe.Сумма_списаний_за_поездку is NULL THEN '0' else qwe.Сумма_списаний_за_поездку end ))AS DECIMAL(14,0)) as Сумма_после_проверки
    from facts.FS_Drivers_balance_transaction dt
    LEFT join facts.FS_Orders oo
    on dt.order_id=oo.id
    left join (
    SELECT DISTINCT
    dt.order_id,
    SUM(transaction_amount/100) as Сумма_списаний_за_поездку
    from facts.FS_Drivers_balance_transaction dt
    left JOIN (  SELECT
    o.id as order_id
        FROM facts.FS_Orders o
        LEFT JOIN facts.FS_Fraud_orders fo
            ON o.id = fo.id
        LEFT JOIN facts.FS_Fraud_verifies fv
            ON fo.id = fv.order_id
        LEFT JOIN 
    (SELECT MAX(id) id, order_pattern_id, resolution ,session_id
    FROM facts.FS_Fraud_resolutions
    WHERE resolution IS NOT NULL
    GROUP BY order_pattern_id, resolution,session_id) fr
            ON fv.id = fr.session_id
        WHERE resolution = 'YES'
    ) gr_1 on gr_1.order_id=dt.order_id
    WHERE transaction_type='Order Refund'
    and gr_1.order_id is not NULL
    GROUP BY dt.order_id  ) qwe on qwe.order_id= dt.order_id
    WHERE 1=1
        AND transaction_type='Compensation'
        AND to_timestamp(oo.order_start_date)::date is not NULL
        AND to_timestamp(oo.order_start_date)::date >= %s
        AND to_timestamp(oo.order_start_date)::date <= %s
    group by region_id, Дата_проверки
    """
    # Проверка по водителю  через ид поездки
    sql_7 = """ 
    select DISTINCT
    gr.trip_number as Дуэт
    ,(to_timestamp(oo.arrive_time)-to_timestamp(oo.accept_time))::varchar as  Подача
    ,to_timestamp(oo.order_start_date) as Старт_поездки
    ,oo.order_src_address as Адрес_подачи
    ,to_timestamp(oo.order_end_date) as Время_окончания_поездки
    ,oo.order_dst_address as Конечный_адрес
    ,oo.promo_code_description as Промо
    ,oo.promo_code_discount/100 as Номинал_промокода
    ,(to_timestamp(oo.order_end_date)-to_timestamp(oo.order_start_date))::varchar as Время_заказа
    ,oo.sub_state as Статус_поездки
    ,oo.id as ИД_поездки
    ,grs.trip_number as Кол_поездок_клиента
    ,oo.customer_id as ИД_клиента
    ,cc.status as Стасус
    ,case WHEN cc.last_name is not NULL THEN (cc.last_name::varchar)||' '||(cc.first_name ::varchar) else cc.first_name end Имя_клиента
    ,cc.phone AS Телефон_клиента
    ,cc.email AS Почта_клиента
    ,(drv.id::varchar)||'  /  '||(drv.ext_id::varchar) as ИД_водителя
    ,case WHEN pr.last_name is not NULL THEN (pr.first_name::varchar)||' '||(pr.last_name ::varchar) else pr.first_name end Имя_водителя
    ,prs.email as Почта_водителя
    ,pr.phone AS Телефон_водителя
    ,drv.promo_code AS Промо_водителя
    ,case when cc.status_reasons is NULL Then ' ' ELSE cc.status_reasons end Статус_р
    FROM facts.FS_Orders oo
    LEFT JOIN facts.FS_Drivers drv ON oo.driver_id=drv.id
    LEFT JOIN facts.FS_Profiles pr ON drv.profile_id = pr.id
    LEFT JOIN facts.FS_Profiles_security prs ON pr.id = prs.id
    LEFT JOIN facts.FS_Customers cc ON cc.id=oo.customer_id
    LEFT JOIN facts.FS_Orders_customer_cost oc ON oc.order_id=oo.id
    LEFT JOIN (SELECT customer_id, count (*) as trip_number FROM facts.FS_Orders WHERE (sub_state = 'ORDER_COMPLETED' OR sub_state = 'CUSTOMER_CANCEL_AFTER_TRIP') 
    group by customer_id ) grs on grs.customer_id=oo.customer_id
    LEFT JOIN (SELECT  DISTINCT 
    customer_id, driver_id, count(*) as trip_number
    FROM facts.FS_Orders 
    WHERE (sub_state = 'ORDER_COMPLETED' OR sub_state = 'CUSTOMER_CANCEL_AFTER_TRIP') and driver_id=%s
    GROUP BY customer_id, driver_id) gr ON gr.driver_id = oo.driver_id and gr.customer_id = oo.customer_id
    WHERE (sub_state = 'ORDER_COMPLETED' OR sub_state = 'CUSTOMER_CANCEL_AFTER_TRIP') and oo.driver_id=%s
    """   
    # Количество успешных и фрод поездок
    sql_8 = """ 
    SELECT
    gr.qwe as Количество_успешных_заказов
    ,gr_1.qwer as Количество_заказов_отмеченных_как_фрод
    ,gr.qwe-gr_1.qwer as Количество_поездок_без_нарушений 
    from 
    (SELECT 
    driver_id
    ,count(id) as qwe
    FROM facts.FS_Orders oo 
    WHERE 1=1
    AND sub_state = 'ORDER_COMPLETED'
    AND driver_id = %s
    AND to_timestamp(oo.order_end_date)::date >=%s
    AND to_timestamp(oo.order_end_date)::date <=%s
    GROUP By driver_id) gr 
    left join (
    SELECT
    COUNT(DISTINCT o.id) AS qwer
    , o.driver_id
    FROM facts.FS_Orders o
    LEFT JOIN facts.FS_Fraud_orders fo
    ON o.id = fo.id
    LEFT JOIN facts.FS_Fraud_verifies fv
    ON fo.id = fv.order_id
    LEFT JOIN 
    (SELECT MAX(id) id, order_pattern_id, resolution ,session_id
    FROM facts.FS_Fraud_resolutions
    WHERE resolution IS NOT NULL
    GROUP BY order_pattern_id, resolution,session_id) fr
    ON fv.id = fr.session_id
    where  fr.resolution='YES'
    and o.driver_id=%s
    and to_timestamp(fo.order_date)::date >=%s
    and to_timestamp(fo.order_date)::date <=%s
    GROUP BY o.driver_id
    ) gr_1 on gr_1.driver_id =gr.driver_id
    """
    #Длинный ИД ВОДИТЕЛЯ через КОРОТКИЙ ИД ВОДИТЕЛЯ
    sql_9 = """ 
    SELECT 
    id
    FROM facts.FS_Drivers drv
    WHERE ext_id=%s
    """