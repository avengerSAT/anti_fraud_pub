SELECT 
COUNT(*) as Количество_успешных_заказов
From facts.LM_Orders
WHERE city=%s
	and completeid=1
	and aautoid=%s
	and "date" BETWEEN %s and %s