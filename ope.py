import dash
#import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import flask
import os
import pandas as pd

tab = pd.read_csv('model.csv')
score = tab.iloc[-1].to_dict()
del score['Unnamed: 0']

cost = tab.iloc[-2].to_dict()
del cost['Unnamed: 0']

process_time = tab.iloc[-3].to_dict()
del process_time['Unnamed: 0']

liquidity = tab.iloc[-4].to_dict()
del liquidity['Unnamed: 0']

## To test
param_list = tab.iloc[:,0]
#del L[15]
#del L[16]
#del L[17]
## To test

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
    className='header', style={'background-color' : '#1B61A4'},
    children=html.Div(
        className='container-width',
        style={'background-color' : '#1B61A4', 'height': '100%'},
        children=[
            html.A(html.Img(
                src="https://ownest.io/images/header-logo.png",
                className="logo"
            ), href='https://ownest.io/', className="logo-link"), 

            html.Div(className="links", children=[
                html.A('Valeur Operationnelle', className="link active", href="/", style={'background-color' : '#1B61A4'}),
                html.A('Variables', className="link", href="/variables", style={'background-color' : '#1B61A4'}),
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
                      {'x': list(score.keys()), 'y': list(score.values()), 'type': 'bar', 'name': 'SF'},
                  ],
                  'layout': {
                      'title': 'Valeur Operationnelle'
                  }
              }),
    # Tabs
    html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
    #dcc.Tabs(
    #   tabs=[
    #       {'label': i, 'value': i} for i in param_list
    #   ],
    #   value=param_list[0],
    #   id='tabs'
    #),
    
    html.H3(children='Temps de processing'
            ),

    html.Hr(style={'margin': '0', 'margin-bottom': '5'}),

    dcc.Graph(id='cout_graph',
              figure={
                  'data': [
                      {'x': list(cost.keys()), 'y': list(cost.values()), 'type': 'bar', 'name': 'SF'},
                  ],
                  'layout': {
                      'title': 'Cout'
                  }
              }),

    html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
    html.H3(children='Cout'
            ),

    html.Hr(style={'margin': '0', 'margin-bottom': '5'}),

    dcc.Graph(id='process_graph',
              figure={
                  'data': [
                      {'x': list(process_time.keys()), 'y': list(process_time.values()), 'type': 'bar', 'name': 'SF'},
                  ],
                  'layout': {
                      'title': 'Temps de processing'
                  }
              }),

    html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
    html.H3(children='Liquidité'
            ),

    html.Hr(style={'margin': '0', 'margin-bottom': '5'}),

    dcc.Graph(id='liquidity_graph',
              figure={
                  'data': [
                      {'x': list(liquidity.keys()), 'y': list(liquidity.values()), 'type': 'bar', 'name': 'SF'},
                  ],
                  'layout': {
                      'title': 'Liquidité'
                  }
              }),
    
        
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
            #figure={
            #    'data':
            #    [
            #        {'x': tab.df[value].index, 'y': tab.df[value].values, 'type': 'bar', 'name': 'SF'},
            #    ],
            #    'layout': {
            #    }
            #}
        ),
        html.Div("Explication de la variable")
    ])

if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
