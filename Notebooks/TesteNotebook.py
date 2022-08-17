# Databricks notebook source
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt

# COMMAND ----------

x = pd.DataFrame({'val': np.linspace(0, 10, 10)})
y = x.val

# COMMAND ----------

print('mod')

# COMMAND ----------

rf = RandomForestRegressor(50)
rf.fit(x, y)

# COMMAND ----------

# Predições da random forest
x_pred = np.linspace(0, 10, 100).reshape(-1, 1)
y_pred = rf.predict(x_pred)

# predições das duas primeiras árvores do nosso modelo
y_pred0 = rf.estimators_[0].predict(x_pred)
y_pred1 = rf.estimators_[1].predict(x_pred)

plt.plot(x_pred, y_pred)
plt.title('Random Forest')
plt.show()

# COMMAND ----------


