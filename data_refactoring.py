import pandas as pd
import numpy as np
import yfinance as yf
from dataclasses import dataclass

@dataclass
class Params:
    ticker: str = "AAPL"
    start_date: str = "2019-01-01"
    end: str = None  # None = today
    initial_cash: float = 1000.0
    dca_monthly_amount: float = 100.0
    dca_frequency: int = 30  # amount of days per investment
    

def get_prices(ticker, start, end):
    df = yf.download(ticker, start = start, end = end, auto_adjust = True, progress = False)
    df = df.rename(columns=str.title)
    df.index = pd.to_datetime(df.index, utc=True)
    print(df.shape)
    return df

def simulate_dca(df, p: Params):
    cash = p.initial_cash
    shares = 0.0
    equity_curve = []
    total_invested = p.initial_cash

    start = pd.to_datetime(p.start_date).tz_localize("UTC")
    business_days = pd.date_range(start = start, end = df.index[-1], freq="B")
    
    if p.dca_frequency > 0:
        valid_trade_days = set(business_days[::p.dca_frequency].normalize())
    else:
        valid_trade_days = set()

    dates = list(df.index)
    
    first_day_price = df.loc[dates[0], "Open"].item()
    if first_day_price > 0:
        shares += cash / first_day_price
        total_invested += cash
        cash = 0.0
    
    for i, day in enumerate(dates):
        # Execute orders placed YESTERDAY at today's open
        if i > 0 and dates[i-1].normalize() in valid_trade_days and p.dca_monthly_amount > 0:
            price = df.loc[day, "Open"].item()          
            invest = min(cash, p.dca_monthly_amount)
            if price > 0 and invest > 0:
                qty = invest / price
                shares += qty
                cash -= invest
                total_invested += invest

        close_price = df.loc[day, "Close"].item()
        equity = cash + shares * close_price
        equity_curve.append((day, cash, shares, close_price, equity, total_invested))

    eq = pd.DataFrame(equity_curve, columns=["date","cash","shares","price","equity", "total_invested"]).set_index("date")
    return eq

def metrics(eq: pd.DataFrame, initial_cash: float):
    final_return = round(eq["equity"].iloc[-1], 2)
    total_invested = eq["total_invested"].iloc[-1]
    gain =  round(final_return - total_invested, 2)
    total_ret = final_return / initial_cash - 1.0
    percentage_gain = round(gain / total_invested * 100, 2)
    return {
        "Gain": "$" + str(gain),
        "Percentage Return": sign_change(percentage_gain) + str(percentage_gain) + "%",
        "Total Assets": "$" + str(final_return)
    }
    
def sign_change(int):
    if int > 0:
        return "+"
    else:
        return "-"

if __name__ == "__main__":
    p = Params(ticker="AAPL", start_date = "2019-01-01", initial_cash=1000, dca_monthly_amount=100)
    df = get_prices(p.ticker, p.start_date, p.end)
    eq = simulate_dca(df, p)
    print(metrics(eq, p.initial_cash))


