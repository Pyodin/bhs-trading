import numpy as np
import pandas_datareader as pdr
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt

start = dt.datetime(2020, 1, 1)
data = pdr.get_data_yahoo("AAPL", start)

plt.plot(data["Close"])
plt.grid()
plt.show()