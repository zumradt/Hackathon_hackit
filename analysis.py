import os
import pandas as pd

folder = "data"
transaction_files = [f for f in os.listdir(folder) if f.endswith("_transactions_3m.csv")]
transfer_files = [f for f in os.listdir(folder) if f.endswith("_transfers_3m.csv")]

clients_file = None
for f in os.listdir(folder):
    if "clients" in f and f.endswith(".csv"):
        clients_file = os.path.join(folder, f)
        break

if clients_file:
    clients_df = pd.read_csv(clients_file)
    clients_df["client_code"] = clients_df["client_code"].astype(str)
else:
    clients_df = pd.DataFrame()

results = []

for client_num in range(1, 61):
    client_code = str(client_num)
    client_info = clients_df[clients_df["client_code"] == client_code] if not clients_df.empty else pd.DataFrame()
    name = client_info.iloc[0]["name"] if not client_info.empty and "name" in client_info.columns else ""
    status = client_info.iloc[0]["status"] if not client_info.empty and "status" in client_info.columns else ""
    age = client_info.iloc[0]["age"] if not client_info.empty and "age" in client_info.columns else ""
    city = client_info.iloc[0]["city"] if not client_info.empty and "city" in client_info.columns else ""
    avg_balance = client_info.iloc[0]["avg_monthly_balance_KZT"] if not client_info.empty and "avg_monthly_balance_KZT" in client_info.columns else ""

    t_file = f"client_{client_code}_transactions_3m.csv"
    if t_file in transaction_files:
        df_t = pd.read_csv(os.path.join(folder, t_file))
        total_transaction_amount = df_t["amount"].sum()
        category_sums = df_t.groupby("category")["amount"].sum().to_dict()
    else:
        total_transaction_amount = 0
        category_sums = {}

    tr_file = f"client_{client_code}_transfers_3m.csv"
    if tr_file in transfer_files:
        df_tr = pd.read_csv(os.path.join(folder, tr_file))
        incoming = df_tr[df_tr["direction"].str.lower().str.contains("in")]["amount"].sum() if "direction" in df_tr.columns else 0
        outgoing = df_tr[df_tr["direction"].str.lower().str.contains("out")]["amount"].sum() if "direction" in df_tr.columns else 0
        total_transfer_amount = df_tr["amount"].sum()
    else:
        incoming = 0
        outgoing = 0
        total_transfer_amount = 0

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
    for cat, val in category_sums.items():
        result_row[f"sum_{cat}"] = val

    results.append(result_row)

df_results = pd.DataFrame(results)
df_results.to_csv("client_money_summary.csv", index=False, encoding="utf-8-sig")
print("✅ Итоговая таблица по 60 клиентам сохранена в client_money_summary.csv")
