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
from datetime import date, datetime, timedelta


cg = CoinGeckoAPI()

@st.cache
def get_price(coin):
    price_dict = cg.get_price(ids=coin, vs_currencies='usd')
    return price_dict[coin]['usd']


@st.cache(show_spinner=False)
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


st.title("Cryptocurrencies' ROI")
st.markdown("Visualize the ROI of different cryptocurrencies from a certain date (the default date is March 13th, 2020.)")


coins_list = ['bitcoin', 'chainlink', 'ethereum', 'cardano', 'vechain', 'ripple', 'litecoin', 
             'stellar', 'binancecoin', 'bitcoin-cash', 'eos', 'tron', 'dash', 'neo', 'tezos']

default_coins_list = ['bitcoin', 'ethereum', 'cardano', 'ripple', 'litecoin']

selected_coins = st.multiselect('Coins', coins_list, default_coins_list)
selected_date = st.date_input("Choose a date", date(2020,3,13), date(2019,1,1))

@st.cache(show_spinner=False)
def get_roi(coins_list): # This func creates the main first df.
    from_date = date(2019,1,1)
    to_date = date.today()
    days_range = to_date - from_date

    Bitcoin = get_history('bitcoin', days_range)

    Date = list(Bitcoin.index)

    df = pd.DataFrame(index=Date)

    df['Bitcoin Price'] = list(Bitcoin['price'])

    for coin in coins_list:
        if coin != 'bitcoin':

#            with st.spinner(text="Fetching measures"):
            coin_df = get_history(coin, days_range)
            df['{} Price'.format(coin.capitalize())] = list(coin_df['price'])
        #price_at13March = float(df.loc[df.index == '2019-01-01', '{} Price'.format(coin.capitalize())])
        # df['{} ROI'.format(coin.capitalize())] = df['{} Price'.format(coin.capitalize())] / price_at13March
        # df['{} ROI'.format(coin.capitalize())] = df['{} ROI'.format(coin.capitalize())].round(4)

    return df

def calc_ROI(df, selected_date, selected_coins): # This func calculates roi based on date and coins.
    df = df[df.index >= str(selected_date)]
    for coin in selected_coins:
        normalized_price = float(df.loc[df.index == str(selected_date), '{} Price'.format(coin.capitalize())])
        df['{} ROI'.format(coin.capitalize())] = df['{} Price'.format(coin.capitalize())] / normalized_price
        df['{} ROI'.format(coin.capitalize())] = df['{} ROI'.format(coin.capitalize())].round(4)
    return df


# from_date = date(2020,3,13)
# st.write(str(from_date))


def get_selected_ROI(selected_coins, df):
    ROI_columns = ['{} ROI'.format(coin.capitalize()) for coin in selected_coins]
    ROI_df = df[ROI_columns]
    final_df = ROI_df.reset_index().melt('index')

    latest_ROI = roi_df.loc[roi_df.index == roi_df.index[-1],:]
    latest_ROI = latest_ROI[ROI_columns]
    latest_ROI_df = latest_ROI.reset_index().melt('index')

    return final_df, latest_ROI_df


#df = get_roi(coins_list)
#a = df.loc[df.index==selected_date:df.index==df.index[-1],:]
#st.write(a)

main_df = get_roi(coins_list)
roi_df = calc_ROI(main_df, selected_date, selected_coins)
selected_df, latest_ROI = get_selected_ROI(selected_coins, roi_df)
#st.write(latest_ROI)
#st.dataframe(selected_df)
################### Chart ###################

nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['index'], empty='none')
    
date_formated = selected_date.strftime("%B %d, %Y")

line = alt.Chart(selected_df).mark_line().encode(
    alt.Y('value', title='ROI from {}'.format(date_formated), scale=alt.Scale(type='log', domain=(1,100))),
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
col1.write("The chart to the right shows a comparison of each coin's ROI as of the last close price.")

#col2.subheader('Chart')
col2.altair_chart(qq, use_container_width=True)

#df_button = st.button("Show me the data")
with st.beta_expander("Show me the data..."):
    st.dataframe(roi_df)
# if df_button:
#     st.dataframe(roi_df)


with st.beta_expander("About this website..."):
    st.markdown('''
                This simple tool helps you see the ROI of your favorite coins from a certain date.
                I made sure I made the charts interactive so make sure you take advantage of that.
                If you have any feedback I would love to know! you can contact me on Telegram [here](https://t.me/motlaaq).
                If you like what you see, you can always [buy me a coffee](https://www.buymeacoffee.com/Motlaq)! 
                                                
                                                
                                                
                                                ''')