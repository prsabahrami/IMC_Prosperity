import pandas as pd
import matplotlib.pyplot as plt

# df = pd.read_csv('/home/alireza/Desktop/IMC_Prosperity/tutorial/data.csv', sep=';', dtype={'timestamp': int, 'mid_price': float})


# filter = (df['product'] == 'AMETHYSTS')

# plt.plot(df[filter]['timestamp'], df[filter]['mid_price'])
# plt.show()

dc = {'AMETHYSTS': 1, 'STARFRUIT': 2}

print(str(dc))
print(sorted({2:3, 1:5}.items()))

X = eval(str(dc))

print(X)