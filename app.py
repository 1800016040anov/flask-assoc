from ast import dump
import datetime
from dbm import dumb
from distutils.command.upload import upload
from distutils.log import error
from flask import Flask, render_template, url_for, redirect,request,session
import os
from werkzeug.utils import secure_filename
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

# Define folder to save uploaded files to process further
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
# Define allowed files (for this example I want only csv file)
ALLOWED_EXTENSIONS = {'csv','xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'super secret key'


@app.route('/')
def hello():
    return render_template('index.html', utc_dt=datetime.datetime.now(datetime.timezone.utc))

@app.route('/data_transaksi', methods=['GET', 'POST'])
def data_transaksi():
    
    if request.method == 'POST':
        # upload file flask
        uploaded_df = request.files['uploaded-file']

        # Extracting uploaded data file name
        data_filename = secure_filename(uploaded_df.filename)

        # flask upload file to database (defined uploaded folder in static path)
        uploaded_df.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))

        # Storing uploaded file path in flask session
        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
    
       
        
    return render_template('Data_Transaksi.html')


@app.route('/data_transaksi_after', methods=['GET', 'POST'])
def data_transaksi_after():
    if request.method == 'POST':
        # # upload file flask
        # uploaded_df = request.files['uploaded-file']

        uploaded_df = request.files['uploaded-file']

        # Extracting uploaded data file name
        data_filename = secure_filename(uploaded_df.filename)

        # flask upload file to database (defined uploaded folder in static path)
        uploaded_df.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))
        data_file_path = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
        uploaded_df = pd.read_excel(data_file_path)
        data_dsc =uploaded_df.isna().sum()
        total_data = len(uploaded_df)
        data_dsc = {"Data Kosong " : data_dsc}
        data_dsc = pd.DataFrame(data_dsc)
        name_file = f"success get file :   {os.path.basename(data_file_path)}"
        session['uploaded_data_file_path'] = data_file_path
        # # Extracting uploaded data file name
        # data_filename = secure_filename(data_file_path.filename)

        # # flask upload file to database (defined uploaded folder in static path)
        # uploaded_df.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))
        # session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)

        # # Storing uploaded file path in flask session
        
    return render_template('Data_Transaksi_show.html',tables=[uploaded_df.to_html(classes='data')], titles=uploaded_df.columns.values,dts=[data_dsc.to_html(classes='data')],tot = total_data ,dt = name_file)


# @app.route('/apriori', methods=['GET', 'POST'])
# def apriori():
#     if request.method == 'POST':
#         # do stuff when the form is submitted
#         # redirect to end the POST handling
#         # the redirect can be to the same route or somewhere else
#         return redirect(url_for('index'))

#     # show the form, it wasn't submitted
#     return render_template('apriori.html')

@app.route('/pengaturan', methods=['GET', 'POST'])
def pengaturan():
    if request.method == 'POST':
        # do stuff when the form is submitted
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('pengaturan.html')

# @app.route('/show_data')
# def showData():
#     # Retrieving uploaded file path from session
#     try:
#         data_file_path = session.get('uploaded_data_file_path', None)
#     except:
#         print(error)

#     # read csv file in python flask (reading uploaded csv file from uploaded server location)
#     uploaded_df = pd.read_excel(data_file_path)
#     data_dsc =uploaded_df.isna().sum()
#     total_data = len(uploaded_df)
#     data_dsc = {"Data Kosong " : data_dsc}
#     data_dsc = pd.DataFrame(data_dsc)



    # return render_template('show_data.html',tables=[uploaded_df.to_html(classes='data')], titles=uploaded_df.columns.values,dts=[data_dsc.to_html(classes='data')],tot = total_data )

@app.route('/preprocessing')
def preprocessing():
    data_file_path = session.get('uploaded_data_file_path', None)
    # read csv file in python flask (reading uploaded csv file from uploaded server location)
    uploaded_df = pd.read_excel(data_file_path)
    data_cleaning = uploaded_df.dropna(subset=['No Transaksi', 'Nama Item'])
    data_cleaning.reset_index(inplace=True)
    data_dsc =data_cleaning.isna().sum()
    data_dsc = {"Data Kosong " : data_dsc}
    data_dsc = pd.DataFrame(data_dsc)
    data_selection = data_cleaning[["No Transaksi","Nama Item"]]
    data_group=data_selection.groupby("No Transaksi", as_index=False).agg({"Nama Item": lambda d: ",".join(d.astype(str))})
    total = len(data_group)
    data_view= data_group[["Nama Item"]]

    dict_obj = data_view.to_dict('list')
    session['data_view'] = dict_obj

    dict_obj = data_group.to_dict('list')
    session['data_group'] = dict_obj
    # return render_template('show_data.html', data_var = uploaded_df_html)
    return render_template('preprocessing.html',tables=[data_view.to_html(classes='data')], titles=uploaded_df.columns.values,dts=[data_dsc.to_html(classes='data')],tot = total )

# @app.route('/select_column')
# def select_column():
#     # Retrieving uploaded file path from session
#     data_file_path = session.get('uploaded_data_file_path', None)

#     # read csv file in python flask (reading uploaded csv file from uploaded server location)
#     uploaded_df = pd.read_excel(data_file_path)
#     uploaded_df = uploaded_df
#     dtvw = uploaded_df.head()
#     return render_template('select_column.html',tables=[uploaded_df.to_html(classes='data')], titles=uploaded_df.columns.values)


# @app.route('/select_column', methods=['POST'])
# def group():
#     Item = request.form['Item']
#     Id = request.form["Id"]
#     # data_file_path = session.get('uploaded_data_file_path', None)
#     # uploaded_df = pd.read_excel(data_file_path)
#     # data_cleaning = uploaded_df.dropna(subset=['No Transaksi', 'Nama Item'])
#     # data_cleaning.reset_index(inplace=True)
#     dict_obj = session['data_cleaning'] if 'data_cleaning' in session else ""  
#     data_cleaning = pd.DataFrame(dict_obj)
#     data_dsc =data_cleaning.isna().sum()
#     data_selection = data_cleaning[[f'{Id}',f'{Item}']]
#     data_group=data_selection.groupby(f"{Id}", as_index=False).agg({f"{Item}": lambda d: ",".join(d.astype(str))})
#     total = len(data_group)
#     dtvw =  data_group.head()
#     dict_obj = data_group.to_dict('list')
#     session['data_group'] = dict_obj

#     return render_template('select_column.html',tables=[data_group.to_html(classes='data')], titles=dtvw.columns.values, tot=total)


@app.route('/apriori')
def apriori():
    dict_obj = session['data_view'] if 'data_group' in session else ""  
    data_view = pd.DataFrame(dict_obj)
    # Retrieving uploaded file path from session
    # data_file_path = session.get('uploaded_data_file_path', None)

    # read csv file in python flask (reading uploaded csv file from uploaded server location)
    # uploaded_df = pd.read_excel(data_file_path)
    # uploaded_df = uploaded_df
    # dtvw = data_group.head()
    return render_template('apriori.html',tables=[data_view.to_html(classes='data')], titles=data_view.columns.values)


@app.route('/apriori', methods=['POST'])
def apriori_refresh():
    from apyori import apriori
    dict_obj = session['data_group'] if 'data_group' in session else ""
    data_group = pd.DataFrame(dict_obj)
    min_support = request.form['min_support']
    min_confidence = request.form["min_confidence"]
    sup = float(float(min_support)/100)
    co = float(float(min_confidence)/100)
    records = []
    dtgr = data_group.iloc[:, 0]
    for i in range(len(dtgr)):
        x = dtgr[i].split(",")
        records.append(x)
    association_rules = apriori(records,min_support = sup,min_confidence = co,min_lift = 3,min_length = 2)
    association_results = list(association_rules)
    dtf = []
    for item in association_results:
        pair = item[0]
        items = [x for x in pair]
        ds = {'Item1': f"{items[0]}", "Rekomendasi": f"{items[1]}", 'Support': f"{str(round(item[1], 3))}", 'Confidence:': f"{str(int(item[2][0][2] * 100))}%", 'lift': f"{str(round(item[2][0][3], 3))}"}

        dtf.append(ds)
    result = pd.DataFrame(dtf)
    return render_template('apriori.html', tables=[result.to_html(classes='data')], titles=result.columns.values)


@app.route('/clr')
def ab():
    session.clear()

    
    return render_template('index.html')

