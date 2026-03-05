import streamlit as st
from data_refactoring import Params, get_prices, simulate_dca, metrics
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px 

st.title("Stock Simulator (DCA)")

ticker = st.text_input("Ticker", "AAPL")
start = st.date_input("Start", value = pd.to_datetime("2019-01-01")).isoformat()
initial = st.number_input("Initial Cash ($)", value=1000.0, step=100.0)
dca = st.number_input("Recurring Contribution ($)", value=100.0, step=10.0)
frequency = st.number_input("Contribution Frequency (business days)", min_value=0, value=5, step=1)

if st.button("Run"):
    p = Params(
        ticker = ticker, 
        start_date = start, 
        initial_cash = initial, 
        dca_monthly_amount = dca, 
        dca_frequency = frequency  # number of business days between trades
    )
    df = get_prices(p.ticker, p.start_date, pd.Timestamp.today())
    if df.empty:
        st.error(f"No data found for {p.ticker} from {p.start_date} to today.")
    else:
        eq = simulate_dca(df, p)
    fig = px.line(
        eq, 
        x=eq.index, 
        y="equity", 
        title=f"{p.ticker} DCA Simulation Equity Curve",
        labels={"equity": "Total Assets", "date": "Date"}
    )
    
    fig.update_traces(
    hovertemplate="Date: %{x}<br>Equity: $%{y:.2f}<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)

    m = metrics(eq, p.initial_cash)
    st.subheader("Simulation Metrics")
    for key, value in m.items():
        st.write(f"**{key}:** {value}")
