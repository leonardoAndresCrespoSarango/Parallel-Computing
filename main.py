import plotly.express as px
import pandas as pd
data = pd.DataFrame({
    'experiment': range(10),
    'result': [1.2, 2.3, None, 4.5, 5.1, None, 7.8, 8.2, 9.5, 10.1]
})
fig = px.scatter(data, x='experiment', y='result')
fig.show()