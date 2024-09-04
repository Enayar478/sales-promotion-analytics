# Préparation des données pour le modèle
X = df[['avg_price', 'indice_avg_price', 'impression_gs', 'acquisition_cost_gs', 'click_on_front', 'on_operation']]
y = df['nb_new_customers']

# Imputation des valeurs manquantes
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)

# Division des données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X_imputed, y, test_size=0.2, random_state=42)

# Normalisation des données
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Entraînement du modèle
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

with open('/Users/enayargrh/Library/Mobile Documents/com~apple~CloudDocs/labo_coding/01_projects/07_cdiscount_streamlit_ml/data/fitted_model/fitted_model_rg.pickle','wb') as modelFile:
     pickle.dump(model,modelFile)