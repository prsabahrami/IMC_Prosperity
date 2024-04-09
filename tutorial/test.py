import pandas as pd
import matplotlib.pyplot as plt

# df = pd.read_csv('/home/alireza/Desktop/IMC_Prosperity/tutorial/data.csv', sep=';', dtype={'timestamp': int, 'mid_price': float})


# filter = (df['product'] == 'AMETHYSTS')

# plt.plot(df[filter]['timestamp'], df[filter]['mid_price'])
# plt.show()


df = pd.read_csv('data.csv', sep=';')

with open('data.txt', 'w') as f:
    f.write(str(df[["product", "timestamp", "mid_price"]].to_dict()))