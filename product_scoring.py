import pandas as pd

df = pd.read_csv("client_money_summary.csv")

def score_travel_card(row):
    travel = row.get("sum_Путешествия", 0)
    taxi = row.get("sum_Такси", 0)
    train = row.get("sum_Поезда", 0)
    plane = row.get("sum_Самолеты", 0)
    score = 0.04 * (travel + taxi + train + plane)
    return score

def score_premium_card(row):
    base_score = 0.02 * row.get("total_transaction_amount", 0)
    deposit = row.get("avg_monthly_balance_KZT", 0)
    if deposit >= 6_000_000:
        base_score = 0.04 * row.get("total_transaction_amount", 0)
    elif deposit >= 1_000_000:
        base_score = 0.03 * row.get("total_transaction_amount", 0)
    jewelry = row.get("sum_Ювелирные изделия", 0)
    perfume = row.get("sum_Парфюмерия", 0)
    restaurant = row.get("sum_Кафе и рестораны", 0)
    bonus_score = 0.04 * (jewelry + perfume + restaurant)
    total_score = min(base_score + bonus_score, 100_000)
    return total_score

def score_credit_card(row):
    online = row.get("sum_Онлайн-сервисы", 0)
    games = row.get("sum_Игры", 0)
    delivery = row.get("sum_Доставка", 0)
    cinema = row.get("sum_Кино", 0)
    score = 0.10 * (online + games + delivery + cinema)
    return score

def score_currency_exchange(row):
    return 1 if row.get("total_transfer_amount", 0) > 0 else 0

def score_cash_loan(row):
    return 1 if row.get("outgoing_transfer", 0) > 500_000 else 0

def score_multi_deposit(row):
    return 0.145 * row.get("avg_monthly_balance_KZT", 0)

def score_save_deposit(row):
    if row.get("outgoing_transfer", 0) == 0:
        return 0.165 * row.get("avg_monthly_balance_KZT", 0)
    return 0

def score_accum_deposit(row):
    if row.get("incoming_transfer", 0) > 0:
        return 0.155 * row.get("avg_monthly_balance_KZT", 0)
    return 0

def score_invest(row):
    return 1 if row.get("avg_monthly_balance_KZT", 0) > 100_000 else 0

def score_gold(row):
    return 1 if row.get("avg_monthly_balance_KZT", 0) > 1_000_000 else 0

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
    best_product = max(scores, key=scores.get)
    current_product = row.get("status", "")

    product_scores.append({
        "client_code": row["client_code"],
        "name": row.get("name", ""),
        "current_product": current_product,
        "best_product": best_product,
        "best_score": scores[best_product],
        **scores
    })

df_score = pd.DataFrame(product_scores)
df_score.to_csv("client_product_scoring.csv", index=False, encoding="utf-8-sig")
print("✅ Скоринг по продуктам с текущей картой клиента сохранён в client_product_scoring.csv")