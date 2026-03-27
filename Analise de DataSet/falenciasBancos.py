import pandas as pd
import matplotlib.pyplot as plt

failures = pd.read_csv('Falencias_Bancos.csv', sep=',', encoding='latin-1')
failures.columns = failures.columns.str.replace('\xa0', '', regex=True).str.strip()
print (failures.columns)
close_timestamps= pd.to_datetime(failures['Closing Date'], errors='coerce')
close_timestamps = close_timestamps.dropna()
failures_by_year = close_timestamps.dt.year.value_counts().sort_index()

failures_by_year.plot(kind='bar', color='skyblue')
plt.xlabel('Ano')
plt.ylabel('Número de Falências')
plt.title('Número de Falências de Bancos por Ano')
plt.show()