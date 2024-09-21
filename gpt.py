import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import json
import os
import zipfile

# Crear una carpeta para guardar las gráficas y los resultados
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Cargar los datos
df = pd.read_csv("dataframePreprocesado.csv")

# Verificar si hay valores nulos
nan_check = df.isna().any()
nan_check_column = df['cyberbullying_type_numerico'].isna().any()

# Eliminar filas con valores nulos
df_cleaned = df.dropna()

# Vectorizar los tweets lematizados
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(df_cleaned['tweet_lemmatized']).toarray()
y = df_cleaned['cyberbullying_type_numerico']

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Definir y entrenar el modelo con los mejores parámetros
best_params = {'max_depth': None, 'min_samples_leaf': 4, 'min_samples_split': 2, 'n_estimators': 150}
best_model = RandomForestClassifier(**best_params, random_state=42)
best_model.fit(X_train, y_train)
y_pred = best_model.predict(X_test)

# Calcular la matriz de confusión
conf_matrix = confusion_matrix(y_test, y_pred)
z_text = [[str(y) for y in x] for x in conf_matrix]

# Crear la figura de Plotly para la matriz de confusión
fig = go.Figure(data=go.Heatmap(
    z=conf_matrix,
    x=['0', '1', '2', '3', '4', '5'],  # Etiquetas predichas
    y=['0', '1', '2', '3', '4', '5'],  # Etiquetas verdaderas
    hoverongaps=False,
    colorscale='Blues'
))

# Añadir anotaciones a la matriz de confusión
annotations = []
for i, row in enumerate(conf_matrix):
    for j, value in enumerate(row):
        annotations.append(
            dict(
                x=j, y=i,
                text=str(value),
                showarrow=False,
                font=dict(color="black")
            )
        )

fig.update_layout(
    title='Matriz de Confusión',
    xaxis=dict(title='Predicted Labels'),
    yaxis=dict(title='True Labels'),
    annotations=annotations,
    autosize=False,
    width=600,
    height=600
)

# Guardar la matriz de confusión como un archivo HTML
confusion_matrix_path = os.path.join(output_dir, 'confusion_matrix.html')
fig.write_html(confusion_matrix_path)

# Calcular el reporte de clasificación
class_report = classification_report(y_test, y_pred, output_dict=True)
class_report_df = pd.DataFrame(class_report).transpose()
class_metrics_df = class_report_df.iloc[:-3, :].reset_index()

# Crear la gráfica de métricas por clase
fig_metrics = px.bar(class_metrics_df, x='index', y=['precision', 'recall', 'f1-score'],
                     barmode='group', height=400)

# Añadir título y etiquetas a la gráfica de métricas
fig_metrics.update_layout(
    title='Metrics per Class',
    xaxis_title='Class',
    yaxis_title='Score',
    legend_title='Metrics',
    xaxis=dict(type='category')
)

# Guardar la gráfica de métricas como un archivo HTML
metrics_path = os.path.join(output_dir, 'metrics.html')
fig_metrics.write_html(metrics_path)

# Calcular la exactitud
accuracy = accuracy_score(y_test, y_pred)

# Guardar la exactitud en un archivo JSON
accuracy_path = os.path.join(output_dir, 'accuracy.json')
with open(accuracy_path, 'w') as f:
    json.dump({'accuracy': accuracy}, f)

# Imprimir la exactitud
print("Exactitud (Accuracy):", accuracy)

# Comprimir los archivos en un ZIP
zip_path = 'output.zip'
with zipfile.ZipFile(zip_path, 'w') as zipf:
    for root, _, files in os.walk(output_dir):
        for file in files:
            zipf.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(output_dir, '..')))

print(f'Files saved and compressed into {zip_path}')
