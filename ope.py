import dash
import dash_core_components as dcc
import dash_html_components as html
import flask
from model import Model
import numpy as np
import os

value_model = Model(W=[0.5, 1.5, 3])
param_list1 = ['Liquidity','Cost','Processing time']
param_list2 = ['Liquidité','Coût','Temps de traitement']


server = flask.Flask(__name__)
# server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(__name__, server=server)
app.config.supress_callback_exceptions = True

# Displaying
#external_css = ["https://fonts.googleapis.com/css?family=Overpass:300,300i",
#                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/dab6f937fd5548cebf4c6dc7e93a10ac438f5efb/dash-technical-charting.css"]

#for css in external_css:
#    app.css.append_css({"external_url": css})

#app.css.append_css({
#    'external_url': (
#        'https://cdn.rawgit.com/plotly/dash-app-stylesheets/8485c028c19c393e9ab85e1a4fafd78c489609c2/dash-docs-base.css',
#        'https://cdn.rawgit.com/plotly/dash-app-stylesheets/30b641e2e89753b13e6557b9d65649f13ea7c64c/dash-docs-custom.css',
#        'https://fonts.googleapis.com/css?family=Dosis'
#    )
#})

css_directory = os.getcwd()
stylesheets = ['ownest.css']
static_css_route = '/static/'


@app.server.route('{}<stylesheet>'.format(static_css_route))
def serve_stylesheet(stylesheet):
    if stylesheet not in stylesheets:
        raise Exception(
            '"{}" is excluded from the allowed static files'.format(
                stylesheet
            )
        )
    return flask.send_from_directory(css_directory, stylesheet)


for stylesheet in stylesheets:
    app.css.append_css({"external_url": "/static/{}".format(stylesheet)})




# Displaying
external_css = ["https://fonts.googleapis.com/css?family=Overpass:300,300i",
                "https://fonts.googleapis.com/css?family=Dosis", 
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/dab6f937fd5548cebf4c6dc7e93a10ac438f5efb/dash-technical-charting.css",
                'https://cdn.rawgit.com/plotly/dash-app-stylesheets/8485c028c19c393e9ab85e1a4fafd78c489609c2/dash-docs-base.css']

for css in external_css:
    app.css.append_css({"external_url": css})

# Header
header = html.Div(
    className='header',
    children=html.Div(
        className='container-width',
        style={'height': '80%','text-align': 'left'},
        children=[
            html.A(html.Img(
                src="https://ownest.io/images/ownest.png",
                className="logo"
            ), href='https://Ownest.io/', className="logo-link"),

            html.Div(className="links", children=[
                #html.A('Variables', className="link active", href="/variables"),
                html.A('Valeur Opérationnelle', className="link", href="/valprob"),
                #html.A('Evolution', className="link", href="/valprobevo"),
            ])
        ]
    )
)

# Body
app.layout = html.Div(children=
[
    header,
    html.H1(children='Ownest Dashboard',
            style={'text-align': 'center'}
            ),

    html.H3(children='Valeur operationnelle'
            ),

    html.Div(style={'columnCount': 3}, children =[html.P('Liquidité'),
              dcc.Slider(
                  min=0,
                  max=5,
                  step=0.5,
                  marks={i: '' for i in np.arange(0.0, 5.5, 0.5)},
                  value=value_model.W[0],
                  id='liquidity-slider'
              ),
      html.P('Coût'),
              dcc.Slider(
                  min=0,
                  max=5,
                  step=0.5,
                  marks={i: '' for i in np.arange(0.0, 5.5, 0.5)},
                  value=value_model.W[1],
                  id='cost-slider'
              ),
      html.P('Temps de traitement'),
              dcc.Slider(
                  min=0,
                  max=5,
                  step=0.5,
                  marks={i: '' for i in np.arange(0.0, 5.5, 0.5)},
                  value=value_model.W[2],
                  id='time-slider'
              )]),

    html.Hr(style={'margin': '0', 'margin-bottom': '20'}),

    dcc.Graph(id='val_ope_graph',
              figure={
                  # grouped bar plots with the score grouped per crypto and for different number of days
                  'data': [
                      {'x': value_model.models[1].loc['Score'].index, 'y': value_model.models[1].loc['Score'].values,
                       'type': 'bar', 'name': '1 jour'},
                      {'x': value_model.models[2].loc['Score'].index, 'y': value_model.models[2].loc['Score'].values,
                       'type': 'bar', 'name': '2 jours'},
                      {'x': value_model.models[5].loc['Score'].index, 'y': value_model.models[5].loc['Score'].values,
                       'type': 'bar', 'name': '5 jours'},
                      {'x': value_model.models[10].loc['Score'].index, 'y': value_model.models[10].loc['Score'].values,
                       'type': 'bar', 'name': '10 jours'},
                  ],
                  'layout': {
                      'title': 'Valeur Operationnelle'
                  }
              }),

    # Tabs  
    html.Hr(style={'margin': '0', 'margin-bottom': '30'}),
    dcc.Tabs(
        tabs=[
            {'label': param_list2[i], 'value': param_list1[i]} for i in range(3)
        ],
        value=param_list1[0],
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
    """
    Content for grouped bar plot for the different parameters
    :return: Graph format for grouped bar plot
    """
    return html.Div([
        dcc.Graph(
            id='graph',
            figure={
                'data':
                    [
                      {'x': value_model.models[1].loc[value].index, 'y': value_model.models[1].loc[value].values,
                       'type': 'bar', 'name': '1 jour'},
                      {'x': value_model.models[2].loc[value].index, 'y': value_model.models[2].loc[value].values,
                       'type': 'bar', 'name': '2 jours'},
                      {'x': value_model.models[5].loc[value].index, 'y': value_model.models[5].loc[value].values,
                       'type': 'bar', 'name': '5 jours'},
                      {'x': value_model.models[10].loc[value].index, 'y': value_model.models[10].loc[value].values,
                       'type': 'bar', 'name': '10 jours'},
                  ],
                'layout': {
                }
            }
        ),
        #html.Div("Explication de la variable")
    ])


@app.callback(
    dash.dependencies.Output('val_ope_graph', 'figure'),
    [dash.dependencies.Input('liquidity-slider', 'value'),
     dash.dependencies.Input('cost-slider', 'value'),
     dash.dependencies.Input('time-slider', 'value')])
def update_time(liquidity, cost, time):
    """
    Update model when we update the weights for the model
    :return: json format for a grouped bar plots 
    """
    value_model.W = [liquidity, cost, time]
    value_model.update_model()
    return {
        'data': [
                      {'x': value_model.models[1].loc['Score'].index, 'y': value_model.models[1].loc['Score'].values,
                       'type': 'bar', 'name': '1 jour'},
                      {'x': value_model.models[2].loc['Score'].index, 'y': value_model.models[2].loc['Score'].values,
                       'type': 'bar', 'name': '2 jours'},
                      {'x': value_model.models[5].loc['Score'].index, 'y': value_model.models[5].loc['Score'].values,
                       'type': 'bar', 'name': '5 jours'},
                      {'x': value_model.models[10].loc['Score'].index, 'y': value_model.models[10].loc['Score'].values,
                       'type': 'bar', 'name': '10 jours'},
                  ],
        'layout': {
            'title': 'Valeur Operationnelle'
        }
    }


if __name__ == '__main__':
    app.run_server(debug=False, threaded=False, port=8060)
