from datetime import datetime

import streamlit as st
import pandas as pd


@st.cache_data
def open_file():
    dateparse = lambda x: datetime.strptime(x, '%d-%m-%Y')
    df = pd.read_csv("Data.csv", parse_dates=['date_create'], date_parser=dateparse)
    #Очистка\преобразование данных
    # df.drop_duplicates(ignore_index=True, inplace=True)
    df.active_price = df.active_price.str.replace('нет в наличии', '0')
    df.prev_price = df.prev_price.str.replace('нет в наличии', '0')
    df.active_price = df.active_price.str.replace(' ', '')
    df.prev_price = df.prev_price.str.replace(' ', '')
    df[['active_price', 'prev_price']] = df[['active_price', 'prev_price']].astype(float)

    return df


data = open_file()

select = st.selectbox('Name', options=data.name.unique())
select_data = data[data.name == select]
select_data.index = select_data['date_create']

# col1, col2 = st.columns(2)
st.line_chart(select_data[['active_price', 'prev_price']])
button_data = st.checkbox('Open data')
if button_data:
    st.dataframe(select_data)
