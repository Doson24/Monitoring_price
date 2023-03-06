import pandas as pd
import matplotlib.pyplot as plt


parser = lambda date: pd.datetime.strptime(date, '%d-%m-%Y')
df = pd.read_csv('Data.csv', error_bad_lines=False, parse_dates=[2], date_parser=parser)

search_name = 'Lenovo'
rez = df[df['name'].str.contains(search_name, regex=False)]
df['active_price'].astype(float)

# print(rez[['name', 'active_price', 'date_create']].describe())
# rez[['active_price', 'date_create']].plot()
# plt.show()

plt.scatter(rez['date_create'], rez['active_price'])
plt.show()

# print(rez['date_create'])
print(rez[['name', 'active_price']])
