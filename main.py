# import pandas as pd
# import numpy as np
# import os

# def main():
#     # Шаг 1: Сбор данных из файлов
#     folder = "data"
#     clients_df = pd.DataFrame()
    
#     # Поиск файла с клиентами
#     for f in os.listdir(folder):
#         if "clients" in f and f.endswith(".csv"):
#             clients_df = pd.read_csv(os.path.join(folder, f))
#             clients_df["client_code"] = clients_df["client_code"].astype(str)
#             break
    
#     results = []
    
#     # Обработка данных по клиентам
#     for client_num in range(1, 61):
#         client_code = str(client_num)
#         client_info = clients_df[clients_df["client_code"] == client_code] if not clients_df.empty else pd.DataFrame()
        
#         # Извлечение информации о клиенте
#         name = client_info.iloc[0]["name"] if not client_info.empty and "name" in client_info.columns else ""
#         status = client_info.iloc[0]["status"] if not client_info.empty and "status" in client_info.columns else ""
#         age = client_info.iloc[0]["age"] if not client_info.empty and "age" in client_info.columns else ""
#         city = client_info.iloc[0]["city"] if not client_info.empty and "city" in client_info.columns else ""
#         avg_balance = client_info.iloc[0]["avg_monthly_balance_KZT"] if not client_info.empty and "avg_monthly_balance_KZT" in client_info.columns else 0
        
#         # Обработка транзакций
#         t_file = os.path.join(folder, f"client_{client_code}_transactions_3m.csv")
#         if os.path.exists(t_file):
#             df_t = pd.read_csv(t_file)
#             total_transaction_amount = df_t["amount"].sum()
#             category_sums = df_t.groupby("category")["amount"].sum().to_dict()
#         else:
#             total_transaction_amount = 0
#             category_sums = {}
        
#         # Обработка переводов
#         tr_file = os.path.join(folder, f"client_{client_code}_transfers_3m.csv")
#         if os.path.exists(tr_file):
#             df_tr = pd.read_csv(tr_file)
#             incoming = df_tr[df_tr["direction"].str.lower().str.contains("in")]["amount"].sum() if "direction" in df_tr.columns else 0
#             outgoing = df_tr[df_tr["direction"].str.lower().str.contains("out")]["amount"].sum() if "direction" in df_tr.columns else 0
#             total_transfer_amount = df_tr["amount"].sum()
#         else:
#             incoming = 0
#             outgoing = 0
#             total_transfer_amount = 0
        
#         # Формирование строки результата
#         result_row = {
#             "client_code": client_code,
#             "name": name,
#             "status": status,
#             "age": age,
#             "city": city,
#             "avg_monthly_balance_KZT": avg_balance,
#             "total_transaction_amount": total_transaction_amount,
#             "total_transfer_amount": total_transfer_amount,
#             "incoming_transfer": incoming,
#             "outgoing_transfer": outgoing,
#         }
        
#         # Добавление сумм по категориям
#         for cat, val in category_sums.items():
#             result_row[f"sum_{cat}"] = val
        
#         results.append(result_row)
    
#     # Создание DataFrame с данными клиентов
#     df = pd.DataFrame(results)
    
#     # Функции скоринга продуктов
#     def score_travel_card(row):
#         travel = row.get("sum_Путешествия", 0)
#         taxi = row.get("sum_Такси", 0)
#         hotels = row.get("sum_Отели", 0)
#         score = 0.04 * (travel + taxi + hotels)
#         return round(score, 2)
    
#     def score_premium_card(row):
#         base_score = 0.02 * row.get("total_transaction_amount", 0)
#         deposit = row.get("avg_monthly_balance_KZT", 0)
        
#         if deposit >= 6000000:
#             base_score = 0.04 * row.get("total_transaction_amount", 0)
#         elif deposit >= 1000000:
#             base_score = 0.03 * row.get("total_transaction_amount", 0)
        
#         jewelry = row.get("sum_Ювелирные украшения", 0)
#         perfume = row.get("sum_Косметика и Парфюмерия", 0)
#         restaurant = row.get("sum_Кафе и рестораны", 0)
#         bonus_score = 0.04 * (jewelry + perfume + restaurant)
        
#         total_score = min(base_score + bonus_score, 100000 * 3)
#         return round(total_score, 2)
    
#     def score_credit_card(row):
#         online_services = row.get("sum_Кино", 0) + row.get("sum_Развлечения", 0)
        
#         categories = [
#             row.get("sum_Продукты питания", 0),
#             row.get("sum_Кафе и рестораны", 0),
#             row.get("sum_Такси", 0),
#             row.get("sum_Одежда и обувь", 0),
#             row.get("sum_Авто", 0)
#         ]
#         top_categories = sum(sorted(categories, reverse=True)[:3])
        
#         score = 0.10 * (online_services + top_categories)
#         return round(score, 2)
    
#     def score_currency_exchange(row):
#         return 1 if row.get("total_transfer_amount", 0) > 1000000 else 0
    
#     def score_cash_loan(row):
#         return 1 if row.get("outgoing_transfer", 0) > 1500000 else 0
    
#     def score_multi_deposit(row):
#         return round(0.145 * row.get("avg_monthly_balance_KZT", 0), 2)
    
#     def score_save_deposit(row):
#         if row.get("outgoing_transfer", 0) < 100000:
#             return round(0.165 * row.get("avg_monthly_balance_KZT", 0), 2)
#         return 0
    
#     def score_accum_deposit(row):
#         if row.get("incoming_transfer", 0) > 100000:
#             return round(0.155 * row.get("avg_monthly_balance_KZT", 0), 2)
#         return 0
    
#     def score_invest(row):
#         balance = row.get("avg_monthly_balance_KZT", 0)
#         outgoing = row.get("outgoing_transfer", 0)
#         return 1 if (balance > 100000 and outgoing < balance * 0.8) else 0
    
#     def score_gold(row):
#         return 1 if row.get("avg_monthly_balance_KZT", 0) > 2000000 else 0
    
#     # Скоринг продуктов
#     product_scores = []
    
#     for _, row in df.iterrows():
#         scores = {
#             "Карта для путешествий": score_travel_card(row),
#             "Премиальная карта": score_premium_card(row),
#             "Кредитная карта": score_credit_card(row),
#             "Обмен валют": score_currency_exchange(row),
#             "Кредит наличными": score_cash_loan(row),
#             "Депозит Мультивалютный": score_multi_deposit(row),
#             "Депозит Сберегательный": score_save_deposit(row),
#             "Депозит Накопительный": score_accum_deposit(row),
#             "Инвестиции": score_invest(row),
#             "Золотые слитки": score_gold(row),
#         }
        
#         best_product = max(scores.items(), key=lambda x: x[1])[0]
        
#         product_scores.append({
#             "client_code": row["client_code"],
#             "name": row["name"],
#             "best_product": best_product,
#             "best_score": scores[best_product],
#             **scores
#         })
    
#     df_scoring = pd.DataFrame(product_scores)
    
#     # Генерация персонализированных push-уведомлений
# # ...existing code...

#     # Генерация персонализированных push-уведомлений
#     def generate_push_notification(client_row, scoring_row):
#         name = client_row["name"]
#         best_product = scoring_row["best_product"]
#         best_score = scoring_row["best_score"]
        
#         # Замена NaN на 0
#         if pd.isna(best_score):
#             best_score = 0
        
#         taxi = client_row.get("sum_Такси", 0) or 0
#         travel = (client_row.get("sum_Путешествия", 0) or 0) + (client_row.get("sum_Отели", 0) or 0)
#         restaurant = client_row.get("sum_Кафе и рестораны", 0) or 0
#         balance = client_row.get("avg_monthly_balance_KZT", 0) or 0
        
#         def format_amount(amount):
#             # Обработка NaN и None
#             if pd.isna(amount) or amount is None:
#                 amount = 0
#             return f"{amount:,.0f}".replace(",", " ").replace("nan", "0")
        
#         if best_product == "Карта для путешествий":
#             if taxi > 100000:
#                 return f"{name}, вы часто ездите на такси — {format_amount(taxi)} ₸ за 3 месяца. Карта для путешествий вернёт 4% кешбэка. Оформить?"
#             elif travel > 100000:
#                 return f"{name}, с картой для путешествий вы получите 4% кешбэк на отели и перелёты. Идеально для ваших поездок. Открыть карту?"
#             else:
#                 return f"{name}, карта для путешествий с кешбэком 4% на такси и отели. Начните экономить на поездках. Посмотреть?"
        
#         elif best_product == "Премиальная карта":
#             if restaurant > 300000:
#                 return f"{name}, с вашими тратами в ресторанах ({format_amount(restaurant)} ₸) премиальная карта вернёт до {format_amount(best_score)} ₸ кешбэка. Оформить?"
#             elif balance > 1000000:
#                 return f"{name}, с вашим остатком {format_amount(balance)} ₸ премиальная карта даст повышенный кешбэк и привилегии. Подключить?"
#             else:
#                 return f"{name}, премиальная карта с кешбэком до 4% и эксклюзивными предложениями. Улучшите ваш банкинг. Открыть?"
        
#         elif best_product == "Кредитная карта":
#             return f"{name}, кредитная карта с кешбэком 10% в ваших любимых категориях. Пользуйтесь без процентов до 2 месяцев. Оформить?"
        
#         elif best_product == "Обмен валют":
#             return f"{name}, меняйте валюту в приложении по выгодному курсу без комиссии. Автопокупка по целевому курсу. Настроить?"
        
#         elif best_product == "Кредит наличными":
#             return f"{name}, нужны деньги на цели? Кредит наличными до 2 000 000 ₸ по ставке от 12%. Решение за 5 минут. Узнать условия?"
        
#         elif best_product == "Депозит Мультивалютный":
#             yearly_income = best_score * 4
#             return f"{name}, разместите средства на мультивалютном депозите под 14.5%. Заработайте до {format_amount(yearly_income)} ₸ в год. Открыть вклад?"
        
#         elif best_product == "Депозит Сберегательный":
#             yearly_income = best_score * 4
#             return f"{name}, максимальный доход на сбережениях — 16.5% годовых. Защита KDIF. Заработайте до {format_amount(yearly_income)} ₸. Открыть?"
        
#         elif best_product == "Депозит Накопительный":
#             yearly_income = best_score * 4
#             return f"{name}, копите с доходностью 15.5%. Пополняйте когда удобно. Заработайте до {format_amount(yearly_income)} ₸ в год. Начать?"
        
#         elif best_product == "Инвестиции":
#             return f"{name}, начните инвестировать с любой суммы. Покупка акций без комиссий в первый год. Это проще, чем кажется! Открыть счёт?"
        
#         elif best_product == "Золотые слитки":
#             return f"{name}, золото — надёжный способ сохранить капитал. Покупайте слитки онлайн от 1 грамма. Диверсифицируйте сбережения. Подробнее?"
        
#         return f"{name}, у нас для вас специальное предложение! Посмотреть?"
    
#     # Создание финального DataFrame с push-уведомлениями
#     final_results = []
    
#     for _, scoring_row in df_scoring.iterrows():
#         client_code = scoring_row["client_code"]
#         client_data = df[df["client_code"] == client_code].iloc[0]
        
#         push_text = generate_push_notification(client_data, scoring_row)
        
#         final_row = {
#             "client_code": client_code,
#             "product": scoring_row["best_product"],
#             "push_notification": push_text
#         }
        
#         # # Добавляем все скоринговые баллы
#         # for product in scoring_row.index:
#         #     if product not in ["client_code", "product", "best_score"]:
#         #         final_row[f"score_{product}"] = scoring_row[product]
        
#         final_results.append(final_row)
    
#     # Сохранение финального файла
#     df_final = pd.DataFrame(final_results)
#     df_final.to_csv("client_product_recommendations.csv", index=False, encoding="utf-8-sig")
    
#     print("✅ Персонализированные рекомендации созданы!")
#     print("✅ Финальный файл: client_product_recommendations.csv")
#     print(f"✅ Обработано клиентов: {len(df_final)}")
#     print(f"✅ Создан один файл со всей информацией")

# if __name__ == "__main__":
#     main()
import pandas as pd
import numpy as np
import os

def main():
    # Шаг 1: Сбор данных из файлов
    folder = "data"
    clients_df = pd.DataFrame()
    
    # Поиск файла с клиентами
    for f in os.listdir(folder):
        if "clients" in f and f.endswith(".csv"):
            clients_df = pd.read_csv(os.path.join(folder, f))
            clients_df["client_code"] = clients_df["client_code"].astype(str)
            break
    
    results = []
    
    # Обработка данных по клиентам
    for client_num in range(1, 61):
        client_code = str(client_num)
        client_info = clients_df[clients_df["client_code"] == client_code] if not clients_df.empty else pd.DataFrame()
        
        # Извлечение информации о клиенте
        name = client_info.iloc[0]["name"] if not client_info.empty and "name" in client_info.columns else ""
        status = client_info.iloc[0]["status"] if not client_info.empty and "status" in client_info.columns else ""
        age = client_info.iloc[0]["age"] if not client_info.empty and "age" in client_info.columns else ""
        city = client_info.iloc[0]["city"] if not client_info.empty and "city" in client_info.columns else ""
        avg_balance = client_info.iloc[0]["avg_monthly_balance_KZT"] if not client_info.empty and "avg_monthly_balance_KZT" in client_info.columns else 0
        
        # Обработка транзакций
        t_file = os.path.join(folder, f"client_{client_code}_transactions_3m.csv")
        if os.path.exists(t_file):
            df_t = pd.read_csv(t_file)
            total_transaction_amount = df_t["amount"].sum()
            category_sums = df_t.groupby("category")["amount"].sum().to_dict()
        else:
            total_transaction_amount = 0
            category_sums = {}
        
        # Обработка переводов
        tr_file = os.path.join(folder, f"client_{client_code}_transfers_3m.csv")
        if os.path.exists(tr_file):
            df_tr = pd.read_csv(tr_file)
            incoming = df_tr[df_tr["direction"].str.lower().str.contains("in")]["amount"].sum() if "direction" in df_tr.columns else 0
            outgoing = df_tr[df_tr["direction"].str.lower().str.contains("out")]["amount"].sum() if "direction" in df_tr.columns else 0
            total_transfer_amount = df_tr["amount"].sum()
        else:
            incoming = 0
            outgoing = 0
            total_transfer_amount = 0
        
        # Формирование строки результата
        result_row = {
            "client_code": client_code,
            "name": name,
            "status": status,
            "age": age,
            "city": city,
            "avg_monthly_balance_KZT": avg_balance,
            "total_transaction_amount": total_transaction_amount,
            "total_transfer_amount": total_transfer_amount,
            "incoming_transfer": incoming,
            "outgoing_transfer": outgoing,
        }
        
        # Добавление сумм по категориям
        for cat, val in category_sums.items():
            result_row[f"sum_{cat}"] = val
        
        results.append(result_row)
    
    # Создание DataFrame с данными клиентов
    df = pd.DataFrame(results)
    
    # Функции скоринга продуктов с персонализированным кэшбеком
    def score_travel_card(row):
        travel = row.get("sum_Путешествия", 0)
        taxi = row.get("sum_Такси", 0)
        hotels = row.get("sum_Отели", 0)
        
        # Персонализированный кэшбек: чем больше траты, тем выше процент
        total_travel_spend = travel + taxi + hotels
        
        if total_travel_spend > 500000:
            cashback_rate = 0.05  # 5% для активных путешественников
        elif total_travel_spend > 200000:
            cashback_rate = 0.04  # 4% для умеренных
        else:
            cashback_rate = 0.03  # 3% для остальных
            
        score = cashback_rate * total_travel_spend
        return round(score, 2), cashback_rate
    
    def score_premium_card(row):
        deposit = row.get("avg_monthly_balance_KZT", 0)
        total_spend = row.get("total_transaction_amount", 0)
        
        # Базовый кэшбек в зависимости от депозита
        if deposit >= 6000000:
            base_rate = 0.04
        elif deposit >= 1000000:
            base_rate = 0.03
        else:
            base_rate = 0.02
            
        base_score = base_rate * total_spend
        
        # Бонусный кэшбек для премиальных категорий
        jewelry = row.get("sum_Ювелирные украшения", 0)
        perfume = row.get("sum_Косметика и Парфюмерия", 0)
        restaurant = row.get("sum_Кафе и рестораны", 0)
        
        premium_spend = jewelry + perfume + restaurant
        bonus_rate = 0.05 if premium_spend > 300000 else 0.04
        bonus_score = bonus_rate * premium_spend
        
        total_score = min(base_score + bonus_score, 100000 * 3)
        avg_rate = (base_rate + bonus_rate) / 2 if total_spend + premium_spend > 0 else 0
        
        return round(total_score, 2), avg_rate
    
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
        
        # Персонализированный кэшбек: чем больше траты в топ-категориях, тем выше процент
        total_relevant_spend = online_services + top_categories
        
        if total_relevant_spend > 400000:
            cashback_rate = 0.12  # 12% для активных пользователей
        elif total_relevant_spend > 200000:
            cashback_rate = 0.10  # 10% для умеренных
        else:
            cashback_rate = 0.08  # 8% для остальных
            
        score = cashback_rate * total_relevant_spend
        return round(score, 2), cashback_rate
    
    def score_currency_exchange(row):
        return 1 if row.get("total_transfer_amount", 0) > 1000000 else 0, 0
    
    def score_cash_loan(row):
        return 1 if row.get("outgoing_transfer", 0) > 1500000 else 0, 0
    
    def score_multi_deposit(row):
        deposit_amount = row.get("avg_monthly_balance_KZT", 0)
        interest_rate = 0.145  # 14.5%
        if deposit_amount > 5000000:
            interest_rate = 0.15  # 15% для крупных вкладов
        return round(interest_rate * deposit_amount, 2), interest_rate
    
    def score_save_deposit(row):
        if row.get("outgoing_transfer", 0) < 100000:
            deposit_amount = row.get("avg_monthly_balance_KZT", 0)
            interest_rate = 0.165  # 16.5%
            if deposit_amount > 3000000:
                interest_rate = 0.17  # 17% для крупных сбережений
            return round(interest_rate * deposit_amount, 2), interest_rate
        return 0, 0
    
    def score_accum_deposit(row):
        if row.get("incoming_transfer", 0) > 100000:
            deposit_amount = row.get("avg_monthly_balance_KZT", 0)
            interest_rate = 0.155  # 15.5%
            if row.get("incoming_transfer", 0) > 500000:
                interest_rate = 0.16  # 16% для активных пополнений
            return round(interest_rate * deposit_amount, 2), interest_rate
        return 0, 0
    
    def score_invest(row):
        balance = row.get("avg_monthly_balance_KZT", 0)
        outgoing = row.get("outgoing_transfer", 0)
        return 1 if (balance > 100000 and outgoing < balance * 0.8) else 0, 0
    
    def score_gold(row):
        return 1 if row.get("avg_monthly_balance_KZT", 0) > 2000000 else 0, 0
    
    # Скоринг продуктов с сохранением персонализированных ставок
    product_scores = []
    cashback_rates = {}
    
    for _, row in df.iterrows():
        scores = {}
        rates = {}
        
        travel_score, travel_rate = score_travel_card(row)
        premium_score, premium_rate = score_premium_card(row)
        credit_score, credit_rate = score_credit_card(row)
        exchange_score, exchange_rate = score_currency_exchange(row)
        loan_score, loan_rate = score_cash_loan(row)
        multi_score, multi_rate = score_multi_deposit(row)
        save_score, save_rate = score_save_deposit(row)
        accum_score, accum_rate = score_accum_deposit(row)
        invest_score, invest_rate = score_invest(row)
        gold_score, gold_rate = score_gold(row)
        
        scores = {
            "Карта для путешествий": travel_score,
            "Премиальная карта": premium_score,
            "Кредитная карта": credit_score,
            "Обмен валют": exchange_score,
            "Кредит наличными": loan_score,
            "Депозит Мультивалютный": multi_score,
            "Депозит Сберегательный": save_score,
            "Депозит Накопительный": accum_score,
            "Инвестиции": invest_score,
            "Золотые слитки": gold_score,
        }
        
        rates = {
            "Карта для путешествий": travel_rate,
            "Премиальная карта": premium_rate,
            "Кредитная карта": credit_rate,
            "Обмен валют": exchange_rate,
            "Кредит наличными": loan_rate,
            "Депозит Мультивалютный": multi_rate,
            "Депозит Сберегательный": save_rate,
            "Депозит Накопительный": accum_rate,
            "Инвестиции": invest_rate,
            "Золотые слитки": gold_rate,
        }
        
        best_product = max(scores.items(), key=lambda x: x[1])[0]
        best_rate = rates[best_product]
        
        product_scores.append({
            "client_code": row["client_code"],
            "name": row["name"],
            "best_product": best_product,
            "best_score": scores[best_product],
            "best_rate": best_rate,
            **scores
        })
        
        # Сохраняем ставки для генерации уведомлений
        cashback_rates[row["client_code"]] = rates
    
    df_scoring = pd.DataFrame(product_scores)
    
    # Генерация персонализированных push-уведомлений
    def generate_push_notification(client_row, scoring_row, rates):
        name = client_row["name"]
        best_product = scoring_row["best_product"]
        best_score = scoring_row["best_score"]
        best_rate = scoring_row["best_rate"]
        
        # Замена NaN на 0
        if pd.isna(best_score):
            best_score = 0
        if pd.isna(best_rate):
            best_rate = 0
        
        taxi = client_row.get("sum_Такси", 0) or 0
        travel = (client_row.get("sum_Путешествия", 0) or 0) + (client_row.get("sum_Отели", 0) or 0)
        restaurant = client_row.get("sum_Кафе и рестораны", 0) or 0
        balance = client_row.get("avg_monthly_balance_KZT", 0) or 0
        
        def format_amount(amount):
            if pd.isna(amount) or amount is None:
                amount = 0
            return f"{amount:,.0f}".replace(",", " ").replace("nan", "0")
        
        def format_rate(rate):
            return f"{rate*100:.1f}%".replace(".", ",")
        
        if best_product == "Карта для путешествий":
            cashback_rate = format_rate(rates["Карта для путешествий"])
            if taxi > 100000:
                return f"{name}, вы часто ездите на такси — {format_amount(taxi)} ₸ за 3 месяца. Карта для путешествий вернёт {cashback_rate} кешбэка. Оформить?"
            elif travel > 100000:
                return f"{name}, с картой для путешествий вы получите {cashback_rate} кешбэк на отели и перелёты. Идеально для ваших поездок. Открыть карту?"
            else:
                return f"{name}, карта для путешествий с кешбэком {cashback_rate} на такси и отели. Начните экономить на поездках. Посмотреть?"
        
        elif best_product == "Премиальная карта":
            cashback_rate = format_rate(rates["Премиальная карта"])
            if restaurant > 300000:
                return f"{name}, с вашими тратами в ресторанах ({format_amount(restaurant)} ₸) премиальная карта вернёт до {format_amount(best_score)} ₸ ({cashback_rate}) кешбэка. Оформить?"
            elif balance > 1000000:
                return f"{name}, с вашим остатком {format_amount(balance)} ₸ премиальная карта даст {cashback_rate} кешбэк и привилегии. Подключить?"
            else:
                return f"{name}, премиальная карта с кешбэком {cashback_rate} и эксклюзивными предложениями. Улучшите ваш банкинг. Открыть?"
        
        elif best_product == "Кредитная карта":
            cashback_rate = format_rate(rates["Кредитная карта"])
            return f"{name}, кредитная карта с кешбэком {cashback_rate} в ваших любимых категориях. Пользуйтесь без процентов до 2 месяцев. Оформить?"
        
        elif best_product == "Обмен валют":
            return f"{name}, меняйте валюту в приложении по выгодному курсу без комиссии. Автопокупка по целевому курсу. Настроить?"
        
        elif best_product == "Кредит наличными":
            return f"{name}, нужны деньги на цели? Кредит наличными до 2 000 000 ₸ по ставке от 12%. Решение за 5 минут. Узнать условия?"
        
        elif best_product == "Депозит Мультивалютный":
            yearly_income = best_score * 4
            interest_rate = format_rate(rates["Депозит Мультивалютный"])
            return f"{name}, разместите средства на мультивалютном депозите под {interest_rate}. Заработайте до {format_amount(yearly_income)} ₸ в год. Открыть вклад?"
        
        elif best_product == "Депозит Сберегательный":
            yearly_income = best_score * 4
            interest_rate = format_rate(rates["Депозит Сберегательный"])
            return f"{name}, максимальный доход на сбережениях — {interest_rate} годовых. Защита KDIF. Заработайте до {format_amount(yearly_income)} ₸. Открыть?"
        
        elif best_product == "Депозит Накопительный":
            yearly_income = best_score * 4
            interest_rate = format_rate(rates["Депозит Накопительный"])
            return f"{name}, копите с доходностью {interest_rate}. Пополняйте когда удобно. Заработайте до {format_amount(yearly_income)} ₸ в год. Начать?"
        
        elif best_product == "Инвестиции":
            return f"{name}, начните инвестировать с любой суммы. Покупка акций без комиссий в первый год. Это проще, чем кажется! Открыть счёт?"
        
        elif best_product == "Золотые слитки":
            return f"{name}, золото — надёжный способ сохранить капитал. Покупайте слитки онлайн от 1 грамма. Диверсифицируйте сбережения. Подробнее?"
        
        return f"{name}, у нас для вас специальное предложение! Посмотреть?"
    
 # Создание финального DataFrame с push-уведомлениями
    final_results = []
    
    for _, scoring_row in df_scoring.iterrows():
        client_code = scoring_row["client_code"]
        client_data = df[df["client_code"] == client_code].iloc[0]
        client_rates = cashback_rates[client_code]
        
        push_text = generate_push_notification(client_data, scoring_row, client_rates)
        
        final_row = {
            "client_code": client_code,
            "product": scoring_row["best_product"],
            "push_notification": push_text
        }
        
        final_results.append(final_row)
    
    # Сохранение финального файла
    df_final = pd.DataFrame(final_results)
    
    # Создаем папку для результатов, если её нет

    output_path = os.path.join("client_product_recommendations.csv")
    df_final.to_csv(output_path, index=False, encoding="utf-8-sig")
    
    print("✅ Персонализированные рекомендации созданы!")
    print(f"✅ Финальный файл: {output_path}")
    print(f"✅ Обработано клиентов: {len(df_final)}")
    print("✅ Создан файл с тремя колонками: client_code, product, push_notification")

if __name__ == "__main__":
    main()