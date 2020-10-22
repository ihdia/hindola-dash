from flask import Flask, render_template
import dash 
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import sql_functions as sql
import plotly.graph_objects as go
import base64
server = Flask(__name__,template_folder='templates')

collectionsApp = dash.Dash(
    __name__,
    server=server, 
    routes_pathname_prefix="/colDash/",
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

annotatorsApp = dash.Dash(
    __name__,
    server=server, 
    routes_pathname_prefix="/annotatorsDash/",
    external_stylesheets=[dbc.themes.BOOTSTRAP]
    
)

annotationsApp = dash.Dash(
    __name__,
    server=server, 
    routes_pathname_prefix="/annotationsDash/",
    external_stylesheets=[dbc.themes.BOOTSTRAP]
    
)

galleryApp = dash.Dash(
    __name__,
    server=server, 
    routes_pathname_prefix="/galleryDash/",
    external_stylesheets=[dbc.themes.BOOTSTRAP]
    
)

num_collections,num_books,num_pages= sql.get_db_stats()

fig_collections_dial = go.Figure()

# Collections

fig_collections_dial.add_trace(
    go.Indicator(
    mode = "number",
    value = num_collections,
    title = {'text':'Collections'},
    domain = {'row': 0, 'column': 0}
))
# books
fig_collections_dial.add_trace(
    go.Indicator(
    mode = "number",
    value = num_books,
    title = {'text':'Books'},
    domain = {'row': 0, 'column': 1}
    )
)

fig_collections_dial.add_trace(
    go.Indicator(
    mode = "number",
    value = num_pages,
    title = {'text':'Pages'},
    domain = {'row': 0, 'column': 2}
    )
)



fig_collections_dial.update_layout(
    grid = {'rows': 1, 'columns': 3, 'pattern': "independent"})

# Pie Charts:

collections_count_ind = sql.count_ind_collections()
db_array = {'collections':list(collections_count_ind.keys()),'count':list(collections_count_ind.values())}
df = pd.DataFrame(db_array)
fig_annot_pie = px.pie(df, values='count', names='collections')
fig_annot_pie.update_traces(hole=.4, hoverinfo="label+percent+name")
fig_annot_pie.update_layout(
    title_text="Collections Distribution",
    annotations=[dict(text=str(len(collections_count_ind)), font_size=50, showarrow=False)
                ])
# fig.show()



# Create subplots: use 'domain' type for Pie subplot

collections_list = sql.get_collection_names()

collectionsApp.layout = html.Div([
    html.H1('Collections'),
    html.Br(),
    html.H3('Static Data'),
    html.Div([
        dcc.Graph(
        id='collections_static',
        figure=fig_collections_dial
    )
    ]),

    html.Div([
        dcc.Graph(
        id='collections_static2',
        figure=fig_annot_pie
    )
    ]) ,

    html.Div([
        dcc.Dropdown(
            id = 'collection',
            options = [{'label': i, 'value': i} for i in collections_list],
            value = list(collections_list)[0],
            style={'width':'50%'}
        )
    ]), 

    html.Div([
        dcc.Graph(
        id='books_distribution',
        
    )
    ])    
])

@collectionsApp.callback(
    Output(component_id='books_distribution', component_property='figure'),
    Input(component_id='collection', component_property='value')
)

def update_output(col_name):
    # print(col_name)
    book_details = sql.get_only_books(col_name)
    db_array = {'book':list(book_details.keys()),'count':list(book_details.values())}
    df = pd.DataFrame(db_array)
    fig_annot_pie = px.pie(df, values='count', names='book')
    fig_annot_pie.update_traces(hole=.4, hoverinfo="label+percent+name")
    fig_annot_pie.update_layout(
        title_text="Books Distribution",
        annotations=[dict(text=str(len(book_details)), font_size=50, showarrow=False)
                    ])
    
    return fig_annot_pie

# Annotations

# num_collections = len(sql.count_ind_collections())
collection_db = sql.count_ind_collections()
collection_completion = sql.count_ind_completion()
# inp_dict = {}
not_annotated = {i:collection_db[i]-collection_completion[i] for i in collection_db}
percentages_annotated = [str(int(collection_completion[i]/(not_annotated[i]+collection_completion[i])*100))+'% of '+i for i in collection_db]
# print(percentages)
fig = go.Figure(data=[
    go.Bar(name='Annotated', x=list(collection_db.keys()), y=list(collection_completion.values())),
    go.Bar(name='Remaining', x=list(collection_db.keys()), y=list(not_annotated.values()))
])
fig.update_layout(
    autosize=False,
    width=700,
    height=750,
    title = 'Annotated and Not-Annotated across collections',
    xaxis_title = 'Collections',
    yaxis_title = 'Number of Pages (Images)'
)
fig.update_layout(barmode='stack')

fig_annotated_dial = go.Figure()

# Collections
fig_annotated_dial.add_trace(
    go.Indicator(
    mode = "number",
    value = int(sql.collection_percentage()),
    number = {'suffix': "%"},
    title = {'text':'Collections'},
    domain = {'row': 0, 'column': 0}
))
# books
fig_annotated_dial.add_trace(
    go.Indicator(
    mode = "number",
    value = int(sql.book_percentage()),
    number = {'suffix': "%"},
    title = {'text':'Books'},
    domain = {'row': 0, 'column': 1}
    )
)

fig_annotated_dial.add_trace(
    go.Indicator(
    mode = "number",
    value = int(sql.page_percentage()),
    number = {'suffix': "%"},
    title = {'text':'Pages'},
    domain = {'row': 0, 'column': 2}
    )
)
fig_annotated_dial_num = go.Figure()

fig_annotated_dial_num.add_trace(
    go.Indicator(
    mode = "number",
    value = int(sql.collectionCountAnnot()),
    
    title = {'text':'Collections'},
    domain = {'row': 0, 'column': 0}
))
# books
fig_annotated_dial_num.add_trace(
    go.Indicator(
    mode = "number",
    value = int(sql.bookCountAnnot()),
    
    title = {'text':'Books'},
    domain = {'row': 0, 'column': 1}
    )
)

fig_annotated_dial_num.add_trace(
    go.Indicator(
    mode = "number",
    value = int(sql.pagesPercentage()),
    
    title = {'text':'Pages'},
    domain = {'row': 0, 'column': 2}
    )
)

# fig_annotated_dial.update_layout(
#     autosize=False,
#     width=800,
#     height=800)

fig_annotated_dial.update_layout(
    grid = {'rows': 1, 'columns': 3, 'pattern': "independent"})

fig_annotated_dial_num.update_layout(
    grid = {'rows': 1, 'columns': 3, 'pattern': "independent"})

annotationsApp.layout = html.Div([
    html.H1('Annotations'),
    html.H3('Annotation Status'),
    
    html.Div([
        dcc.Graph(
        id='Annotations3',
        figure=fig_annotated_dial
    )
    ]),
    html.Div([
        dcc.Graph(
        id='Annotations4',
        figure=fig_annotated_dial_num
    )
    ]),
    html.Div([
        dcc.Graph(
        id='Annotations',
        figure=fig
    )
    ]),
    html.Div([
        dcc.Dropdown(
            id = 'col',
            options = [{'label': i, 'value': i} for i in list(collection_db.keys())],
            value = list(collection_db.keys())[0],
            style={'width':'50%'}
        )
    ]),
    html.Div([
        dcc.Graph(
        id='Annotations2',
        
    )
    ])
])

@annotationsApp.callback(
    Output(component_id='Annotations2', component_property='figure'),
    Input(component_id='col', component_property='value')
)

def update_output(col_name):
    # print(col_name)
    book_db_details = sql.detailed_count_collections()
    book_db_annotated = sql.detailed_annot_count()
    annotated = {}
    for collection in book_db_details:
        annotated[collection] = {}
        for book in book_db_details[collection]:
            try:
                annotated[collection][book] = book_db_annotated[collection][book]
            except:
                annotated[collection][book] = 0
    # print(annotated)
    # print(book_db_details)
    book_not_annotated = {}
    for collection in book_db_details:
        book_not_annotated[collection] = {}
        for book in book_db_details[collection]:
            book_not_annotated[collection][book] = book_db_details[collection][book] - annotated[collection][book]
    fig1 = go.Figure(data=[
        go.Bar(name='Annotated', x=list(book_db_details[col_name]), y=list(annotated[col_name].values())),
        go.Bar(name='Remaining', x=list(book_db_details[col_name]), y=list(book_not_annotated[col_name].values())),
        
        
    ])
    fig1.update_layout(barmode='stack')
    fig1.update_layout(
        autosize=False,
        width = 1500,
        height=900,
        title = 'Annotated and Not-Annotated across books of {}'.format(col_name),
        xaxis_title = 'Books',
        yaxis_title = 'Number of Pages'
    )
    return fig1


# Annotators:

fig_annotaters_dial = go.Figure()
num_users = sql.get_num_users()
num_annotated_pages = sql.users_annot_count()[0]
# Collections
fig_annotaters_dial.add_trace(
    go.Indicator(
    mode = "number",
    value = num_users,
    title = {'text':'Users'},
    domain = {'row': 0, 'column': 0}
))
fig_annotaters_dial.add_trace(
    go.Indicator(
    mode = "number",
    value = num_annotated_pages,
    title = {'text':'Pages Annotated'},
    domain = {'row': 0, 'column': 1}
))

fig_annotaters_dial.add_trace(
    go.Indicator(
    mode = "number",
    value = int(num_annotated_pages/num_users),
    title = {'text':'Average Pages Annotated Per User'},
    domain = {'row': 0, 'column': 2}
))

fig_annotaters_dial.update_layout(
    grid = {'rows': 1, 'columns': 3, 'pattern': "independent"})
users_list = sql.getUsers()
users_info_annotated , users_info_served = sql.all_users_info()
annotatorsApp.layout = html.Div([

    html.H3('General User Stats:'),

    html.Div([
        dcc.Graph(
        id='annotaters',
        figure=fig_annotaters_dial
    )
    ]),
    html.Div([
        dcc.Dropdown(
            id = 'user_annot_details',
            options = [{'label': i, 'value': i} for i in users_list],
            value = list(users_list)[0],
            # style={'width':'50%'}
        )
    ]), 
    html.Div([
        dcc.Graph(
        id='usr_annot',
        
    )
    ])

])
@annotatorsApp.callback(
    Output(component_id='usr_annot', component_property='figure'),
    Input(component_id='user_annot_details', component_property='value')
)

def update_output(user_name):
    # all_users_info()
    fig = go.Figure()
    user_name = user_name.lower()
    num_annotated_pages = users_info_annotated[user_name]
    num_served = users_info_served[user_name]
    # Collections
    fig.add_trace(
        go.Indicator(
        mode = "number",
        value = num_annotated_pages,
        title = {'text':'Pages Annotated'},
        domain = {'row': 0, 'column': 0}
    ))
    fig.add_trace(
        go.Indicator(
        mode = "number",
        value = num_served,
        title = {'text':'Pages Served'},
        domain = {'row': 0, 'column': 1}
    ))


    fig.update_layout(
        grid = {'rows': 1, 'columns': 2, 'pattern': "independent"})
    return fig

#VIEWER

im1 = "../../annot_test_dataset/penn_in_hand/illustrations/238.jpg"
im2 = "../../annot_test_dataset/penn_in_hand/illustrations/126.jpg"
im_64_1 = base64.b64encode(open(im1, 'rb').read()).decode('ascii')
im_64_2 = base64.b64encode(open(im2, 'rb').read()).decode('ascii')


galleryApp.layout = html.Div([
    html.H1(children='Gallery Viewer'),

    html.Div([
        html.Img(
            src='data:image/jpeg;base64,{}'.format(im_64_1),
            style = {
                'height': '40%',
                'width': '40%',
                'float': 'left',
                'position': 'relative',
                'padding-top': 0,
                'padding-right': 0
            }
        )
    ]),
    html.Div([
        html.Img(
            src='data:image/jpeg;base64,{}'.format(im_64_2),
            style = {
                'height': '40%',
                'width': '40%',
                'float': 'left',
                'position': 'relative',
                'padding-top': 0,
                'padding-right': 0
            }
        )
    ])
    
])


@server.route('/')
def index():
    return render_template('index.html')

#remove redundancy
@server.route('/index.html')
def ind():
    return render_template('index.html')

@server.route('/collections.html')
def collections():
    return render_template('collections.html')

@server.route('/annotators.html')
def annotators():
    return render_template('annotators.html')

@server.route('/annotations.html')
def annotations():
    return render_template('annotations.html')

@server.route('/gallery.html')
def viewer():
    return render_template('gallery.html')

@server.route('/colDash/')
def collectionsDash():
    return collectionsApp.layout()

@server.route('/annotatorsDash/')
def annotatorsDash():
    return annotatorsApp.layout()

@server.route('/galleryDash/')
def galleryDash():
    return galleryApp.layout()