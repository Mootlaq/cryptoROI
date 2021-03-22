import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import pandas as pd
import numpy as np
import requests
from pycoingecko import CoinGeckoAPI
import datetime
import time
import altair as alt
from altair.expr import datum, if_
from datetime import date


cg = CoinGeckoAPI()

@st.cache
def get_price(coin):
    price_dict = cg.get_price(ids=coin, vs_currencies='usd')
    return price_dict[coin]['usd']


@st.cache
def get_history(coin, days):
    coin_history = cg.get_coin_market_chart_by_id(id=coin, vs_currency='usd', days=days)

    days = [i[0] for i in coin_history['prices']]
    days = pd.to_datetime(days, unit='ms')

    prices = [i[1] for i in coin_history['prices']]

    days = days[:-1]
    prices = prices[:-1]

#    data = 
    df = pd.DataFrame(data={'price': prices}, index=days)
    
    return df


st.title("ROI since March 13, 2020!")
st.text("Choose your coins from the list below and see how each performed since March 13, 2020!")
coins_list = ['bitcoin', 'chainlink', 'ethereum', 'cardano', 'vechain', 'ripple', 'litecoin', 
             'stellar', 'monero', 'cosmos', 'binancecoin', 'bitcoin-cash']

default_coins_list = ['bitcoin', 'ethereum', 'cardano', 'ripple', 'litecoin']

selected_coins = st.multiselect('Coins', coins_list, default_coins_list)

@st.cache
def get_roi(coins_list):
    from_date = date(2020,3,13)
    to_date = date.today()
    days_range = to_date - from_date

    Bitcoin = get_history('bitcoin', days_range)

    Date = list(Bitcoin.index)

    df = pd.DataFrame(index=Date)

    df['Bitcoin Price'] = list(Bitcoin['price'])

    for coin in coins_list:
        if coin != 'bitcoin':
            coin_df = get_history(coin, days_range)
            df['{} Price'.format(coin.capitalize())] = list(coin_df['price'])
        price_at13March = float(df.loc[df.index == '2020-03-13', '{} Price'.format(coin.capitalize())])
        df['{} ROI'.format(coin.capitalize())] = df['{} Price'.format(coin.capitalize())] / price_at13March
        df['{} ROI'.format(coin.capitalize())] = df['{} ROI'.format(coin.capitalize())].round(4)

    return df

@st.cache
def get_selected_ROI(selected_coins, df):
    ROI_columns = ['{} ROI'.format(coin.capitalize()) for coin in selected_coins]
    ROI_df = df[ROI_columns]
    final_df = ROI_df.reset_index().melt('index')

    latest_ROI = roi_df.loc[roi_df.index == roi_df.index[-1],:]
    latest_ROI = latest_ROI[ROI_columns]
    latest_ROI_df = latest_ROI.reset_index().melt('index')

    return final_df, latest_ROI_df

roi_df = get_roi(coins_list)
selected_df, latest_ROI = get_selected_ROI(selected_coins, roi_df)
#st.write(latest_ROI)
#st.dataframe(selected_df)

################### Chart ###################

nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['index'], empty='none')

line = alt.Chart(selected_df).mark_line().encode(
    alt.Y('value', title='ROI from March 13th, 2020', scale=alt.Scale(type='log', domain=(1,100))),
    alt.X('index', title='Date'),
    color=alt.Color('variable', legend=alt.Legend(title=None, orient="top-left", fillColor='#EEEEEE', strokeColor='gray', cornerRadius=5, padding=5)))
    


selectors = alt.Chart(selected_df).mark_point().encode(
    x='index',
    opacity=alt.value(0),
).add_selection(
    nearest
)

# Draw points on the line, and highlight based on selection
points = line.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

# Draw text labels near the points, and highlight based on selection
text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'value', alt.value(' '))
)

# Draw a rule at the location of the selection
rules = alt.Chart(selected_df).mark_rule(color='gray').encode(
    x='index',
).transform_filter(
    nearest
)

# Put the five layers into a chart and bind the data
final_chart = alt.layer(
    line, selectors, points, rules, text
).properties(
    width=760, height=400
).interactive()

st.altair_chart(final_chart, use_container_width=True)



# latest_ROI = roi_df.loc[roi_df.index == roi_df.index[-1],:]
# latest_ROI = latest_ROI[ROI_columns]
# ddd.reset_index().melt('index')

#st.dataframe(latest_ROI)

qq = alt.Chart(latest_ROI, title="ROI Against Last Close Price").mark_bar(color='#E85450').encode(
    alt.X('variable', title='Date'),
    alt.Y('value', title='ROI'),
    tooltip=['variable', 'value']
).interactive()

qq.configure_view(
    # continuousHeight=200,
    # continuousWidth=200,
    strokeWidth=4,
    fill='#FFEEDD',
    stroke='red',
)

#st.altair_chart(qq, )

col1, col2 = st.beta_columns([1, 2])

col1.subheader("What's the ROI as of today?")
col1.write("The chart to your right shows you the ROI for each coins as of the last close price.")

#col2.subheader('Chart')
col2.altair_chart(qq, use_container_width=True)





with st.beta_expander("About this website..."):
    st.markdown('''
                This simple tool helps you see the ROI of your favorite coins.
                I made sure I made the charts interactive so make sure you take advantage of that.
                If you have any feedback I would love to know! you can contact me on Telegram [here](https://t.me/motlaaq).
                If you like what you see, you can always [buy me a coffee](https://www.buymeacoffee.com/Motlaq)! 
                                                
                                                
                                                
                                                ''')