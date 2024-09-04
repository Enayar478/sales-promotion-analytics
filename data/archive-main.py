   
        # Historique des campagnes
        campaigns = df[(df['product_id'] == product_id) & (df['on_operation'] == 1)][['operation_name', 'startdate_op', 'enddate_op']].drop_duplicates()
        campaign_history = [
            html.Div([
                html.Strong(row['operation_name']),
                html.Span(f" ({row['startdate_op']} - {row['enddate_op']})"),
            ], className="campaign-item")
            for _, row in campaigns.iterrows()
        ]
        
        # Graphique de performance
        performance_data = df[df['product_id'] == product_id]
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=performance_data['order_date'], 
            y=performance_data['nb_new_customers'],
            name='Nouveaux clients',
            marker_color='blue'
        ))

        fig.add_trace(go.Bar(
            x=performance_data['order_date'], 
            y=performance_data['total_customers'],
            name='Clients totaux',
            marker_color='green'
        ))

        fig.update_layout(
            barmode='group',  
            title='Performance du produit au fil du temps',
            xaxis_title='Date',
            yaxis_title='Nombre de clients',
            xaxis_tickformat='%d<br>%B',
            legend_title_text='Type de clients',
            margin=dict(l=40, r=20, t=40, b=20),
            height=400
        )
        
        return f"{prediction_op:.2f} nouveaux clients", f"{prediction_no_op:.2f} nouveaux clients", campaign_history, fig
    
    return "En attente...", "En attente...", "Aucun historique disponible", {}

if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='0.0.0.0')



Sauvegarde de l'amélioration du code

# Layout de l'application
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Dashboard de Prédiction E-commerce", className="dashboard-title"),
    ], className="header"),
    
    # Conteneur principal
    html.Div([
        # Sidebar
        html.Div([
            html.H2("Filtres", className="sidebar-title"),
            html.Label("Modèle de prédiction"),
            dcc.Dropdown(
                id="model-dropdown", 
                options=[
                    {'label': 'Random Forest', 'value': 'rf'},
                    {'label': 'Logistic Regression', 'value': 'lr'},
                    {'label': 'Gradient Boosting', 'value': 'gbc'}
                ],
                placeholder="Sélectionnez un modèle",
                className="input-box"
            ),
            html.Br(),
            html.Label("ID du produit"),
            dcc.Dropdown(
                id="product-id-input", 
                options=product_id_options, 
                placeholder="Entrez l'ID du produit", 
                searchable=True, 
                clearable=True, 
                className="input-box"
            ),
            html.Br(),
            html.Label("Catégorie"),
            dcc.Input(id="category-input", type="text", placeholder="Catégorie", readOnly=True, className="input-box"),
            html.Br(),
            html.Label("Prix"),
            dcc.Input(id="avg-price-input", type="number", placeholder="Entrez le prix moyen", className="input-box"),
            html.Br(),
            html.Label("Indice Prix Moyen"),
            dcc.Input(id="indice-avg-price-input", type="number", placeholder="Entrez l'indice prix moyen", className="input-box"),
            html.Br(),
            html.Label("Impressions"),
            dcc.Slider(
                id='impression-gs-slider', 
                min=0, 
                max=df['impression_gs'].max(), 
                step=10000, 
                tooltip={"placement": "bottom", "always_visible": True}, 
                marks=None, 
                value=10000, 
                className="slider"
            ),
            html.Div(id="impression-gs-output", className="output-box"),
            html.Br(),
            html.Label("Mise en avant Home Page"),
            dcc.Dropdown(
                id="click-on-front-dropdown", 
                options=[{'label': 'Oui', 'value': 1}, {'label': 'Non', 'value': 0}], 
                placeholder="Sélectionnez Oui ou Non", 
                className="input-box"
            ),
            html.Br(),
            html.Label("Date de Lancement de l'Opération"),
            dcc.DatePickerSingle(
                id='launch-date-picker', 
                placeholder='Sélectionnez une date', 
                display_format='DD/MM/YYYY', 
                className="input-box"
            ),
            html.Br(),
            html.Button("Lancer la prédiction", id="predict-button", n_clicks=0, className="predict-button"),
        ], className="sidebar"),
        
        # Contenu principal
        html.Div([
            # Prévisions de Performance
            html.Div([
                html.H2("Prévisions de Performance", className="section-title"),
                html.Div([
                    html.Div([
                        html.H3("En Opération Commerciale"),
                        html.Div(id="prediction-op", className="prediction-value"),
                    ], className="prediction-box"),
                    html.Div([
                        html.H3("Hors Opération Commerciale"),
                        html.Div(id="prediction-no-op", className="prediction-value"),
                    ], className="prediction-box"),
                ], className="predictions-container"),
            ], className="main-section"),
            
            # Historique des Campagnes
            html.Div([
                html.H2("Historique des Campagnes", className="section-title"),
                html.Div(id="campaign-history", className="campaign-history"),
            ], className="main-section"),
            
            # Graphique de Performance
            html.Div([
                html.H2("Graphique de Performance", className="section-title"),
                dcc.Graph(id="performance-graph"),
            ], className="main-section"),
        ], className="dashboard-content"),
    ], className="main-container"),
])

# Callback pour faire les prédictions
@app.callback(
    [Output("prediction-op", "children"),
     Output("prediction-no-op", "children"),
     Output("campaign-history", "children"),
     Output("performance-graph", "figure")],
    [Input("predict-button", "n_clicks")],
    [State("model-dropdown", "value"),
     State("product-id-input", "value"),
     State("avg-price-input", "value"),
     State("indice-avg-price-input", "value"),
     State("impression-gs-slider", "value"),
     State("click-on-front-dropdown", "value"),
     State("launch-date-picker", "date")]
)
def make_predictions(n_clicks, model_choice, product_id, avg_price, indice_avg_price, impression_gs, on_front, launch_date):
    if n_clicks > 0:
        # Sélection des modèles en fonction du choix de l'utilisateur
        model_op = f'{model_choice}_op'
        model_no_op = f'{model_choice}_hors_op'
        
        # Récupération des données d'entrée
        input_data = setup.load_data_model(
            df,
            product_id,
            launch_date,
            avg_price,
            indice_avg_price,
            impression_gs,
            on_front
        )

        # Prédictions
        prediction_op = models[model_op].predict(input_data)[0]
        prediction_no_op = models[model_no_op].predict(input_data)[0]       

        # Historique des campagnes
        campaigns = df[(df['product_id'] == product_id) & (df['on_operation'] == 1)][['operation_name', 'startdate_op', 'enddate_op']].drop_duplicates()
        campaign_history = [
            html.Div([
                html.Strong(row['operation_name']),
                html.Span(f" ({row['startdate_op']} - {row['enddate_op']})"),
            ], className="campaign-item")
            for _, row in campaigns.iterrows()
        ]
        
        # Graphique de performance
        performance_data = df[df['product_id'] == product_id]
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=performance_data['order_date'], 
            y=performance_data['nb_new_customers'],
            name='Nouveaux clients',
            marker_color='blue'
        ))

        fig.add_trace(go.Bar(
            x=performance_data['order_date'], 
            y=performance_data['total_customers'],
            name='Clients totaux',
            marker_color='green'
        ))

        # Mise en page du graphique
        fig.update_layout(
            barmode='group',
            title='Performance du produit au fil du temps',
            xaxis_title='Date',
            yaxis_title='Nombre de clients',
            xaxis_tickformat='%d<br>%B',
            legend_title_text='Type de clients',
            margin=dict(l=40, r=20, t=40, b=20),
            height=400
        )
        
        return f"{prediction_op:.2f} nouveaux clients", f"{prediction_no_op:.2f} nouveaux clients", campaign_history, fig

# Lancement de l'application
if __name__ == "__main__":
    app.run_server(debug=True)




# Callback pour faire les prédictions
@app.callback(
    [Output("prediction-op", "children"),
     Output("prediction-no-op", "children")],
    [Input("predict-button", "n_clicks")],
    [State("model-op-dropdown", "value"),
     State("model-no-op-dropdown", "value"),
     State("product-id-input", "value"),
     State("avg-price-input", "value"),
     State("indice-avg-price-input", "value"),
     State("impression-gs-slider", "value"),
     State("click-on-front-dropdown", "value"),
     State("launch-date-picker", "date")]
)
def make_predictions(n_clicks, model_op, model_no_op, product_id, avg_price, indice_avg_price, impression_gs, on_front, launch_date):
    if n_clicks > 0:
        # 1. Récupération de la catégorie pour le product_id sélectionné
        category_for_sku = get_category_for_sku(df, product_id)
        
        # 2. Transformation des données d'entrée en DataFrame
        '''
        input_data = pd.DataFrame([{
            'product_id': product_id,
            'avg_price': avg_price,
            'indice_avg_price': indice_avg_price,
            'impression_gs': impression_gs,
            'on_front': on_front,
            'launch_date': launch_date,
            'Category_1': category_for_sku,
        }])
        '''

        '''
        TODO: load pickles instead of querying from BQ
        '''
                            
        input_data = setup.load_data_model(
                            df,
                            product_id,
                            launch_date,
                            avg_price,
                            indice_avg_price,
                            impression_gs,
                            on_front
                            )
        # 3. Encodage de la catégorie
        #input_data = encode_category(input_data, category_for_sku)
        
        # 4. Extraire les informations temporelles de la date de lancement
        #jour_semaine, semaine_mois = infos_date(launch_date)
        #input_data['jour_semaine'] = jour_semaine
        #input_data['semaine_mois'] = semaine_mois
        
        # 5. Prédictions
        prediction_op = models[model_op].predict(input_data)[0]
        prediction_no_op = models[model_no_op].predict(input_data)[0]
        
        return f"{prediction_op} nouveaux clients", f"{prediction_no_op} nouveaux clients"
    return "Aucune prédiction", "Aucune prédiction"

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='0.0.0.0')
