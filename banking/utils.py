def analyze_data(df):
    df["type"] = df["amount"].apply(lambda x: "Credit" if x > 0 else "Debit")
    return df


def generate_summary(df):
    income = df[df["type"] == "Credit"]["amount"].sum()
    expense = abs(df[df["type"] == "Debit"]["amount"].sum())

    return {
        "income": income,
        "expense": expense,
        "savings": income - expense
    }