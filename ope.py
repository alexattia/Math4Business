import dash
# import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import flask
import os
import pandas as pd
from model import Model


## uncommment on final product
# import model
# value_model = model.Model()
##


##FOR TEST, delete on final product
# class Model():
#     def __init__(self):
#         tab = pd.read_csv('model.csv')
#         tab = tab.set_index('Unnamed: 0')
#         self.model = tab
#         self.W = []

#     def compute_score(self):
#         pass

W = {'time-slider' : 1, 'cost-slider': 3, 'liquidity-slider' : 5 }
value_model = Model(W=list(W.values()))
##

weights = {
    'Temps de traitement': 'Processing time',
    'Coût': 'Cost',
    'Liquidité': 'Liquidity',
}
param_list = list(weights.values())

server = flask.Flask(__name__)
# server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(__name__, server=server)
app.config.supress_callback_exceptions = True

# Displaying
external_css = ["https://fonts.googleapis.com/css?family=Overpass:300,300i",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/dab6f937fd5548cebf4c6dc7e93a10ac438f5efb/dash-technical-charting.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

app.css.append_css({
    'external_url': (
        'https://cdn.rawgit.com/plotly/dash-app-stylesheets/8485c028c19c393e9ab85e1a4fafd78c489609c2/dash-docs-base.css',
        'https://cdn.rawgit.com/plotly/dash-app-stylesheets/30b641e2e89753b13e6557b9d65649f13ea7c64c/dash-docs-custom.css',
        'https://fonts.googleapis.com/css?family=Dosis'
    )
})

# Header
header = html.Div(
    className='header', style={'background-color': '#1B61A4'},
    children=html.Div(
        className='container-width',
        style={'background-color': '#1B61A4', 'height': '100%'},
        children=[
            html.A(html.Img(
                src="https://ownest.io/images/header-logo.png",
                className="logo"
            ), href='https://ownest.io/', className="logo-link"),

            html.Div(className="links", children=[
                html.A('Valeur Operationnelle', className="link active", href="/",
                       style={'background-color': '#1B61A4', 'color': '#FFFFFF'}),
                html.A('Variables', className="link", href="/variables",
                       style={'background-color': '#1B61A4', 'color': '#FFFFFF'}),
            ])
        ]
    )
)

app.layout = html.Div(children=
[
    header,
    html.H1(children='Ownest Dashboard',
            style={'text-align': 'center'}
            ),

    html.H3(children='Valeur operationnelle'
            ),

    html.Hr(style={'margin': '0', 'margin-bottom': '5'}),

    dcc.Graph(id='val_ope_graph',
              figure={
                  'data': [
                      {'x': value_model.model.loc['Score'].index, 'y': value_model.model.loc['Score'].values,
                       'type': 'bar', 'name': 'SF'},
                  ],
                  'layout': {
                      'title': 'Valeur Operationnelle'
                  }
              }),

    html.Div([html.P('Liquidity:'),
              dcc.Slider(
                  min=0,
                  max=5,
                  step=1,
                  value=0,
                  id='liquidity-slider',
              )]),

    html.Div([html.P('Cost:'),
              dcc.Slider(
                  min=0,
                  max=5,
                  step=1,
                  value=0,
                  id='cost-slider',
              )]),

    html.Div([html.P('Time Processing:'),
              dcc.Slider(
                  min=0,
                  max=5,
                  step=1,
                  value=0,
                  id='time-slider',
              )]),

    # Tabs
    html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
    dcc.Tabs(
        tabs=[
            {'label': i, 'value': i} for i in param_list
        ],
        value=param_list[0],
        id='tabs'
    ),

    html.Div(id='tab_output')
],
    style={
        'width': '85%',
        'max-width': '1200',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'font-family': 'overpass',
        'background-color': '#F3F3F3',
        'padding': '40',
        'padding-top': '20',
        'padding-bottom': '20'
    }
)


@app.callback(dash.dependencies.Output('tab_output', 'children'),
              [dash.dependencies.Input('tabs', 'value')])
def display_content(value):
    return html.Div([
        dcc.Graph(
            id='graph',
            figure={
                'data':
                    [
                        {'x': value_model.model.loc[value].index, 'y': value_model.model.loc[value].values,
                         'type': 'bar', 'name': 'SF'},
                    ],
                'layout': {
                }
            }
        ),
        html.Div("Explication de la variable")
    ])


@app.callback(
    dash.dependencies.Output('val_ope_graph', 'figure'),
    [dash.dependencies.Input('liquidity-slider', 'value'),
     dash.dependencies.Input('cost-slider', 'value'),
     dash.dependencies.Input('time-slider', 'value')])
def update_time(time, cost, liquidity):
    value_model.W = [liquidity, cost, time]
    value_model.compute_score()
    return {
        'data': [
            {'x': value_model.model.loc['Score'].index, 'y': value_model.model.loc['Score'].values, 'type': 'bar',
             'name': 'SF'},
        ],
        'layout': {
            'title': 'Valeur Operationnelle'
        }
    }

if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
