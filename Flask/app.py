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
import cv2 as cv
from skimage import io

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 00:50:04 2020

@author: khadiravana.belagavi
"""

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

external_scripts = [
    {'src':'/dashboard/Flask/assets/custom-script.js'}
]

galleryApp = dash.Dash(
    __name__,
    server=server, 
    routes_pathname_prefix="/galleryDash/",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    external_scripts=external_scripts
    
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


def collection_layout():
    return html.Div([
        html.H1('Collections'),
        html.Br(),
        html.H3('Static Data'),
        html.Button("Reload","dial_btn",hidden=True),
        html.Div([
            dcc.Graph(
            id='collections_static',
            figure=fig_collections_dial
        )
        ]),
        html.Button("Reload","pie_btn",hidden=True),

        html.Div([
            dcc.Graph(
            id='collections_static2',
            figure=fig_annot_pie
        )
        ]) ,

        html.Button("Reload","col_dropdown_btn",hidden=True),

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

collectionsApp.layout = collection_layout

@collectionsApp.callback(
    Output(component_id='collection', component_property='options'),
    Input(component_id='col_dropdown_btn', component_property='n_clicks')
)

def update_col_dropdown(n_clicks):
    collections_list = sql.get_collection_names()
    options = [{'label': i, 'value': i} for i in collections_list]

    return options


@collectionsApp.callback(
    Output(component_id='collections_static2', component_property='figure'),
    Input(component_id='pie_btn', component_property='n_clicks')
)

def update_col_pie(n_clicks):
    collections_count_ind = sql.count_ind_collections()
    db_array = {'collections':list(collections_count_ind.keys()),'count':list(collections_count_ind.values())}
    df = pd.DataFrame(db_array)
    fig_annot_pie = px.pie(df, values='count', names='collections')
    fig_annot_pie.update_traces(hole=.4, hoverinfo="label+percent+name")
    fig_annot_pie.update_layout(
        title_text="Collections Distribution",
        annotations=[dict(text=str(len(collections_count_ind)), font_size=50, showarrow=False)
                    ])
    
    return fig_annot_pie


@collectionsApp.callback(
    Output(component_id='collections_static', component_property='figure'),
    Input(component_id='dial_btn', component_property='n_clicks')
)

def update_col_dial(n_clicks):
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
    
    return fig_collections_dial


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

num_collections = len(sql.count_ind_collections())
collection_db = sql.count_ind_collections()
collection_completion = sql.count_ind_completion()
# inp_dict = {}
if (not collection_completion):
    not_annotated = {i:collection_db[i] for i in collection_db}
else:
    not_annotated = {i:collection_db[i]-collection_completion[i] for i in collection_completion}

percentages_annotated = [str(int(collection_completion[i]/(not_annotated[i]+collection_completion[i])*100))+'% of '+i for i in collection_completion]
colls = list(collection_db.keys())
annotated = []
remaining = []
for coll in colls:
    annotated.append(collection_completion[coll])
    remaining.append(not_annotated[coll])

fig_annotated_dial_num = go.Figure()

fig_annotated_dial_num.add_trace(
    go.Indicator(
    mode = "number",
    value = int(sql.collectionCountAnnot()), # changed
        
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

fig_annotated_dial_num.update_layout(
    grid = {'rows': 1, 'columns': 3, 'pattern': "independent"})

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

fig_annotated_dial.update_layout(
    grid = {'rows': 1, 'columns': 3, 'pattern': "independent"})

def annotations_layout():
    return html.Div([
        html.H1('Annotations'),
        html.H3('Annotation Status'),
        
        html.Button("Reload",id="num",hidden=True),
        html.Div([
            dcc.Graph(
            id='annot_num',
            figure=fig_annotated_dial_num
        )
        ]),
        html.Button("Reload",id="perc",hidden=True),
        html.Div([
            dcc.Graph(
            id='annot_perc',
            figure=fig_annotated_dial
        )
        ]),

        html.Button("Reload",id="annot",hidden=True),
       
        html.Div([
            dcc.Graph(
            id='Annotations',
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
   
annotationsApp.layout = annotations_layout

@annotationsApp.callback(
    Output("Annotations","figure"),
    Input("annot","n_clicks")
)

def update_annot_graph(button):
    collection_db = sql.count_ind_collections()
    collection_completion = sql.count_ind_completion()
    # inp_dict = {}
    if (not collection_completion):
        not_annotated = {i:collection_db[i] for i in collection_db}
    else:
        not_annotated = {i:collection_db[i]-collection_completion[i] for i in collection_completion}

    percentages_annotated = [str(int(collection_completion[i]/(not_annotated[i]+collection_completion[i])*100))+'% of '+i for i in collection_completion]
    colls = list(collection_db.keys())
    annotated = []
    remaining = []
    for coll in colls:
        annotated.append(collection_completion[coll])
        remaining.append(not_annotated[coll])
    # print(percentages)
    fig = go.Figure(data=[
        go.Bar(name='Annotated', x=colls, y=annotated),
        go.Bar(name='Remaining', x=colls, y=remaining)
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

    return fig

@annotationsApp.callback(
            Output("annot_num", "figure"),
            Input("num","n_clicks")
)


def update_num_annotations_dial(button):
    
    fig_annotated_dial_num = go.Figure()

    fig_annotated_dial_num.add_trace(
        go.Indicator(
        mode = "number",
        value = int(sql.collectionCountAnnot()), # changed
        
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

    fig_annotated_dial_num.update_layout(
        grid = {'rows': 1, 'columns': 3, 'pattern': "independent"})
    
    return fig_annotated_dial_num


@annotationsApp.callback(
            Output("annot_perc", "figure"),
            Input("perc","n_clicks")
)

def update_percent_annotations_dial(button):

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

    fig_annotated_dial.update_layout(
        grid = {'rows': 1, 'columns': 3, 'pattern': "independent"})
    
    return fig_annotated_dial


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
    # print(annotated['jain']['Chandibazaar'])
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
    width = 1500
    if col_name == 'pih':
        width = 50000
    
    fig1.update_layout(
        autosize=False,
        width = width,
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

try:
    avg_annotated = int(num_annotated_pages/num_users)
except ZeroDivisionError:
    avg_annotated = 0
fig_annotaters_dial.add_trace(
    go.Indicator(
    mode = "number",
    value = avg_annotated,
    title = {'text':'Average Pages Annotated Per User'},
    domain = {'row': 0, 'column': 2}
))

fig_annotaters_dial.update_layout(
    grid = {'rows': 1, 'columns': 3, 'pattern': "independent"})

users_list = sql.getUsers()
if len(users_list) == 0:
    users_list = ['No Users Yet!']
users_info_annotated , users_info_served = sql.all_users_info()

annotatorsApp.layout = html.Div([

    html.H3('General User Stats:'),
    html.Button("Reload",id="annotaters_btn",hidden=True),

    html.Div([
        dcc.Graph(
        id='annotaters',
        figure=fig_annotaters_dial
    )
    ]),
    html.Button("Reload","dropdown_btn",hidden=True),
    html.Div([
        dcc.Dropdown(
            id = 'user_annot_details',
            options = [{'label': i, 'value': i} for i in users_list],
            value = list(users_list)[0],
            # style={'width':'50%'}
        )
    ]), 
    html.Button("Reload","usr_annot_btn",hidden=True),
    html.Div([
        dcc.Graph(
        id='usr_annot',    
    )
    ])

])


@annotatorsApp.callback(
    Output("user_annot_details","options"),
    Input("dropdown_btn","n_clicks")
)

def update_dropdown(n_clicks):
    users_list = sql.getUsers()
    if len(users_list) == 0:
        users_list = ['No Users Yet!']
    
    options = [{'label': i, 'value': i} for i in users_list]
    return options



@annotatorsApp.callback(
    Output("annotaters","figure"),
    Input("annotaters_btn","n_clicks")
)

def update_annotators_graph(n_clicks):
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

    try:
        avg_annotated = int(num_annotated_pages/num_users)
    except ZeroDivisionError:
        avg_annotated = 0
    fig_annotaters_dial.add_trace(
        go.Indicator(
        mode = "number",
        value = avg_annotated,
        title = {'text':'Average Pages Annotated Per User'},
        domain = {'row': 0, 'column': 2}
    ))

    fig_annotaters_dial.update_layout(
        grid = {'rows': 1, 'columns': 3, 'pattern': "independent"})

    return fig_annotaters_dial


@annotatorsApp.callback(
    Output(component_id='usr_annot', component_property='figure'),
    Input(component_id='user_annot_details', component_property='value')
)

def update_output(user_name):
    # all_users_info()
    users_info_annotated , users_info_served = sql.all_users_info()
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

RANGE=[0,1]

doc_list = sql.get_document_by_date()

i=0
# for i in range(len(doc_list)):
while i < len(doc_list):   
    reviewed = sql.check_reviewed(doc_list[i])[0]
    print(reviewed)

    if reviewed == 1 or reviewed == -1:
        print("success")
        del doc_list[i]
    else:
        i+=1

curr_ind = -1

# print('/annotations/' + doc_list[curr_ind][29:])
# sql.reviewed_image_annotation(doc_list[curr_ind])

#img = io.imread('/annotations/' + doc_list[curr_ind][29:])
#fig = px.imshow(img)


galleryApp.layout = html.Div(children=[

    html.Div(children=[
        html.H1(children='Annotation Viewer',style={"text-align":"left"}),
    ]),

    html.Button("prev",id="prev_btn"),
    html.Button("next",id="next_btn"),
    html.Br(),
    html.Br(),
    # html.Button("✓",id="approve_btn",style={"background-color":"#4CAF50",
    # "color": "white"}),
    html.H6("Reject annotation"),
    html.Button("x",id="reject_btn",style={"background-color":"#FF0000",
    "color": "white"}),
    html.P(id="dummy"),

    html.Button("Reload","doc_list_btn",hidden=True),
    

    html.Div([

        dcc.Graph(
            id='doc-img'
        )

        # html.H6("Hole(virtual)",id="hole-virtual"),
        # html.H6("Hole(physical)",id="hole-phy"),
        # html.H6("Character line segment",id="cls"),
        # html.H6("Boundary line",id="bl"),
        # html.H6("Physical Degradation",id="pd"),
        # html.H6("Page Boundary",id="pb"),
        # html.H6("Character Component",id="cc"),
        # html.H6("Library marker",id="lm"),
        # html.H6("Picture/Decorator",id="pic"),
    ]),

    html.Br(),
    
])

@galleryApp.callback(
            Output("dummy", "children"),
            Input("doc_list_btn","n_clicks")
)

def update_doc_list(n_clicks):
    global doc_list
    doc_list = sql.get_document_by_date()

    i=0
    while i < len(doc_list):   
        reviewed = sql.check_reviewed(doc_list[i])[0]
        print(reviewed)

        if reviewed == 1 or reviewed == -1:
            print("success")
            del doc_list[i]
        else:
            i+=1


    return

@galleryApp.callback(
            Output("doc-img", "figure"),
            [Input("next_btn","n_clicks"),Input("prev_btn","n_clicks")
            ,Input("reject_btn","n_clicks")]
)

def on_click_next(next_btn,prev_btn,reject_btn):
    ctx = dash.callback_context

    button_id=""
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        print(button_id)

    global curr_ind

    if len(doc_list) == 0:
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "No images left to review",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ]
            }
        }
    
    print("curr"+str(curr_ind))

    if curr_ind > len(doc_list):
        curr_ind = len(doc_list)-1

    if button_id == "next_btn":
        #implicit annotation approval
        if curr_ind >= 0:
            sql.accept_image_annotation(doc_list[curr_ind])
        
        # sql.reviewed_image_annotation(doc_list[curr_ind])
        del doc_list[curr_ind]
        curr_ind = min(len(doc_list),curr_ind+1)
        
    
    elif button_id=="prev_btn":
        curr_ind = max(0,curr_ind-1)
    
    elif button_id=="reject_btn":
        sql.reject_image_annotation(doc_list[curr_ind])
        del doc_list[curr_ind]
        curr_ind = min(len(doc_list),curr_ind+1)
    
    if len(doc_list) == 0:
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "No images left to review",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ]
            }
        }

        
    curr_img = base64.b64encode(open('/annotations' + doc_list[curr_ind][29:], 'rb').read()).decode('ascii')
    print('/annotations/' + doc_list[curr_ind][29:])

    img = cv.imread('/annotations/' + doc_list[curr_ind][29:])
    h,w,_ = img.shape
    h = min(max(h,400),500)
    w = min(max(w/1.5,3000),3000)
    print(h,w)

    
    return {'data': [],
        'layout': {
            'xaxis': {
                'range': RANGE,
                'showgrid' : False,
                'visible' : False,
                'zeroline' : False
            },
            'yaxis': {
                'range': RANGE,
                'showgrid' : False,
                'visible' : False,
                'zeroline' : False
            },
            'height': min(h,500),
            'width' : min(w/2,4500),
            'images': [{
                'xref': 'x',
                'yref': 'y',
                'x': RANGE[0],
                'y': RANGE[1],
                'sizex': RANGE[1] - RANGE[0],
                'sizey': RANGE[1] - RANGE[0],
                'sizing': 'stretch',
                'layer': 'below',
                'source': 'data:image/jpeg;base64,{}'.format(curr_img)
            }],
            'dragmode': 'select'  # or 'lasso'
        }
    }



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

@server.route('/annotationsDash/')
def annotationsDash():
    return annotationsApp.layout()
