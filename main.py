import pandas as pd
import numpy as np

df = pd.read_csv("client_money_summary.csv")

def score_travel_card(row):
    travel = row.get("sum_Путешествия", 0)
    taxi = row.get("sum_Такси", 0)
    hotels = row.get("sum_Отели", 0)
    score = 0.04 * (travel + taxi + hotels)
    return round(score, 2)

def score_premium_card(row):
    base_score = 0.02 * row.get("total_transaction_amount", 0)
    deposit = row.get("avg_monthly_balance_KZT", 0)
    
    if deposit >= 6000000:
        base_score = 0.04 * row.get("total_transaction_amount", 0)
    elif deposit >= 1000000:
        base_score = 0.03 * row.get("total_transaction_amount", 0)

    jewelry = row.get("sum_Ювелирные украшения", 0)
    perfume = row.get("sum_Косметика и Парфюмерия", 0)
    restaurant = row.get("sum_Кафе и рестораны", 0)
    bonus_score = 0.04 * (jewelry + perfume + restaurant)
    
    total_score = min(base_score + bonus_score, 100000 * 3)
    return round(total_score, 2)

def score_credit_card(row):
    online_services = row.get("sum_Кино", 0) + row.get("sum_Развлечения", 0)
    
    categories = [
        row.get("sum_Продукты питания", 0),
        row.get("sum_Кафе и рестораны", 0),
        row.get("sum_Такси", 0),
        row.get("sum_Одежда и обувь", 0),
        row.get("sum_Авто", 0)
    ]
    top_categories = sum(sorted(categories, reverse=True)[:3])
    
    score = 0.10 * (online_services + top_categories)
    return round(score, 2)

def score_currency_exchange(row):
    return 1 if row.get("total_transfer_amount", 0) > 1000000 else 0

def score_cash_loan(row):
    return 1 if row.get("outgoing_transfer", 0) > 1500000 else 0

def score_multi_deposit(row):
    return round(0.145 * row.get("avg_monthly_balance_KZT", 0), 2)

def score_save_deposit(row):
    if row.get("outgoing_transfer", 0) < 100000:
        return round(0.165 * row.get("avg_monthly_balance_KZT", 0), 2)
    return 0

def score_accum_deposit(row):
    if row.get("incoming_transfer", 0) > 100000:
        return round(0.155 * row.get("avg_monthly_balance_KZT", 0), 2)
    return 0

def score_invest(row):
    balance = row.get("avg_monthly_balance_KZT", 0)
    outgoing = row.get("outgoing_transfer", 0)
    return 1 if (balance > 100000 and outgoing < balance * 0.8) else 0

def score_gold(row):
    return 1 if row.get("avg_monthly_balance_KZT", 0) > 2000000 else 0

product_scores = []

for _, row in df.iterrows():
    scores = {
        "Карта для путешествий": score_travel_card(row),
        "Премиальная карта": score_premium_card(row),
        "Кредитная карта": score_credit_card(row),
        "Обмен валют": score_currency_exchange(row),
        "Кредит наличными": score_cash_loan(row),
        "Депозит Мультивалютный": score_multi_deposit(row),
        "Депозит Сберегательный": score_save_deposit(row),
        "Депозит Накопительный": score_accum_deposit(row),
        "Инвестиции": score_invest(row),
        "Золотые слитки": score_gold(row),
    }
    
    best_product = max(scores.items(), key=lambda x: x[1])[0]
    
    product_scores.append({
        "client_code": row["client_code"],
        "name": row["name"],
        "best_product": best_product,
        "best_score": scores[best_product],
        **scores
    })

df_scoring = pd.DataFrame(product_scores)
def generate_push_notification(client_row, scoring_row):
    name = client_row["name"]
    best_product = scoring_row["best_product"]
    best_score = scoring_row["best_score"]
    
    taxi = client_row.get("sum_Такси", 0)
    travel = client_row.get("sum_Путешествия", 0) + client_row.get("sum_Отели", 0)
    restaurant = client_row.get("sum_Кафе и рестораны", 0)
    products = client_row.get("sum_Продукты питания", 0)
    balance = client_row.get("avg_monthly_balance_KZT", 0)

    def format_amount(amount):
        return f"{amount:,.0f}".replace(",", " ")
    
    if best_product == "Карта для путешествий":
        if taxi > 100000:
            return f"{name}, вы часто ездите на такси — {format_amount(taxi)} ₸ за 3 месяца. Карта для путешествий вернёт 4% — это {format_amount(best_score)} ₸ кешбэка. Оформить?"
        elif travel > 100000:
            return f"{name}, с картой для путешествий вы получите 4% кешбэк на отели и перелёты. Идеально для ваших поездок. Открыть карту?"
        else:
            return f"{name}, карта для путешествий с кешбэком 4% на такси и отели. Начните экономить на поездках. Посмотреть?"
    
    elif best_product == "Премиальная карта":
        if restaurant > 300000:
            return f"{name}, с вашими тратами в ресторанах ({format_amount(restaurant)} ₸) премиальная карта вернёт до {format_amount(best_score)} ₸ кешбэка. Оформить?"
        elif balance > 1000000:
            return f"{name}, с вашим остатком {format_amount(balance)} ₸ премиальная карта даст повышенный кешбэк и бесплатные переводы. Подключить?"
        else:
            return f"{name}, премиальная карта с кешбэком до 4% и привилегиями. Улучшите ваш банкинг. Открыть?"
    
    elif best_product == "Кредитная карта":
        return f"{name}, кредитная карта с кешбэком 10% в ваших любимых категориях. Пользуйтесь без процентов до 2 месяцев. Оформить?"
    
    elif best_product == "Обмен валют":
        return f"{name}, меняйте валюту в приложении по выгодному курсу без комиссии. Автопокупка по целевому курсу. Настроить?"
    
    elif best_product == "Кредит наличными":
        return f"{name}, нужны деньги на цели? Кредит наличными до 2 000 000 ₸ по ставке от 12%. Решение за 5 минут. Узнать условия?"
    
    elif best_product == "Депозит Мультивалютный":
        yearly_income = best_score * 4
        return f"{name}, разместите средства на мультивалютном депозите под 14.5%. Заработайте до {format_amount(yearly_income)} ₸ в год. Открыть вклад?"
    
    elif best_product == "Депозит Сберегательный":
        yearly_income = best_score * 4
        return f"{name}, максимальный доход на сбережениях — 16.5% годовых. Защита KDIF. Заработайте до {format_amount(yearly_income)} ₸. Открыть?"
    
    elif best_product == "Депозит Накопительный":
        yearly_income = best_score * 4
        return f"{name}, копите с доходностью 15.5%. Пополняйте когда удобно. Заработайте до {format_amount(yearly_income)} ₸ в год. Начать?"
    
    elif best_product == "Инвестиции":
        return f"{name}, начните инвестировать с любой суммы. Покупка акций без комиссий в первый год. Это проще, чем кажется! Открыть счёт?"
    
    elif best_product == "Золотые слитки":
        return f"{name}, золото — надёжный способ сохранить капитал. Покупайте слитки онлайн от 1 грамма. Диверсифицируйте сбережения. Подробнее?"
    
    return f"{name}, у нас для вас специальное предложение! Посмотреть?"

push_notifications = []
for _, scoring_row in df_scoring.iterrows():
    client_code = scoring_row["client_code"]
    client_data = df[df["client_code"] == client_code].iloc[0]
    
    push_text = generate_push_notification(client_data, scoring_row)
    
    push_notifications.append({
        "client_code": client_code,
        "product": scoring_row["best_product"],
        "push_notification": push_text
    })
def generate_push_notification(client_row, scoring_row):
    name = client_row["name"]
    best_product = scoring_row["best_product"]
    best_score = scoring_row["best_score"]
    
    taxi = client_row.get("sum_Такси", 0)
    travel = client_row.get("sum_Путешествия", 0) + client_row.get("sum_Отели", 0)
    restaurant = client_row.get("sum_Кафе и рестораны", 0)
    products = client_row.get("sum_Продукты питания", 0)
    balance = client_row.get("avg_monthly_balance_KZT", 0)
    
    def format_amount(amount):
        return f"{amount:,.0f}".replace(",", " ")
    
    if best_product == "Карта для путешествий":
        if taxi > 100000:
            return f"{name}, вы часто ездите на такси — {format_amount(taxi)} ₸ за 3 месяца. Карта для путешествий вернёт 4% — это {format_amount(best_score)} ₸ кешбэка. Оформить?"
        elif travel > 100000:
            return f"{name}, с картой для путешествий вы получите 4% кешбэк на отели и перелёты. Идеально для ваших поездок. Открыть карту?"
        else:
            return f"{name}, карта для путешествий с кешбэком 4% на такси и отели. Начните экономить на поездках. Посмотреть?"
    
    elif best_product == "Премиальная карта":
        if restaurant > 300000:
            return f"{name}, с вашими тратами в ресторанах ({format_amount(restaurant)} ₸) премиальная карта вернёт до {format_amount(best_score)} ₸ кешбэка. Оформить?"
        elif balance > 1000000:
            return f"{name}, с вашим остатком {format_amount(balance)} ₸ премиальная карта даст повышенный кешбэк и бесплатные переводы. Подключить?"
        else:
            return f"{name}, премиальная карта с кешбэком до 4% и привилегиями. Улучшите ваш банкинг. Открыть?"
    
    elif best_product == "Кредитная карта":
        return f"{name}, кредитная карта с кешбэком 10% в ваших любимых категориях. Пользуйтесь без процентов до 2 месяцев. Оформить?"
    
    elif best_product == "Обмен валют":
        return f"{name}, меняйте валюту в приложении по выгодному курсу без комиссии. Автопокупка по целевому курсу. Настроить?"
    
    elif best_product == "Кредит наличными":
        return f"{name}, нужны деньги на цели? Кредит наличными до 2 000 000 ₸ по ставке от 12%. Решение за 5 минут. Узнать условия?"
    
    elif best_product == "Депозит Мультивалютный":
        yearly_income = best_score * 4
        return f"{name}, разместите средства на мультивалютном депозите под 14.5%. Заработайте до {format_amount(yearly_income)} ₸ в год. Открыть вклад?"
    
    elif best_product == "Депозит Сберегательный":
        yearly_income = best_score * 4
        return f"{name}, максимальный доход на сбережениях — 16.5% годовых. Защита KDIF. Заработайте до {format_amount(yearly_income)} ₸. Открыть?"
    
    elif best_product == "Депозит Накопительный":
        yearly_income = best_score * 4
        return f"{name}, копите с доходностью 15.5%. Пополняйте когда удобно. Заработайте до {format_amount(yearly_income)} ₸ в год. Начать?"
    
    elif best_product == "Инвестиции":
        return f"{name}, начните инвестировать с любой суммы. Покупка акций без комиссий в первый год. Это проще, чем кажется! Открыть счёт?"
    
    elif best_product == "Золотые слитки":
        return f"{name}, золото — надёжный способ сохранить капитал. Покупайте слитки онлайн от 1 грамма. Диверсифицируйте сбережения. Подробнее?"
    
    return f"{name}, у нас для вас специальное предложение! Посмотреть?"

push_notifications = []
for _, scoring_row in df_scoring.iterrows():
    client_code = scoring_row["client_code"]
    client_data = df[df["client_code"] == client_code].iloc[0]
    
    push_text = generate_push_notification(client_data, scoring_row)
    
    push_notifications.append({
        "client_code": client_code,
        "product": scoring_row["best_product"],
        "push_notification": push_text
    })
df_final = pd.DataFrame(push_notifications)
df_final.to_csv("client_product_pushes.csv", index=False, encoding="utf-8-sig")

print("✅ Персонализированные push-уведомления созданы!")
print("✅ Основной файл: client_product_pushes.csv")
print(f"✅ Обработано клиентов: {len(df_final)}")