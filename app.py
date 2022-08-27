from ast import dump
import datetime
from dbm import dumb
from distutils.command.upload import upload
from distutils.log import error
from email import message
from pipes import Template
from flask import Flask, render_template, url_for, redirect,request,session,send_file,app
import os
from werkzeug.utils import secure_filename
import numpy as np
import pandas as pd
import os
import pdfkit
from pathlib import Path
import os

app = Flask(__name__)





path = os.path.join(os.getcwd(), 'storage')

def get_files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file  



kitoptions = {
  "enable-local-file-access": None
}





app = Flask(__name__)

# Define folder to save uploaded files to process further
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
# Define allowed files (for this example I want only csv file)
ALLOWED_EXTENSIONS = {'csv','xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'super secret key'


@app.route('/')
def hello():
    return render_template('index.html',)

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
        
        
    return render_template('Data_Transaksi_show.html',tables=[uploaded_df.to_html(classes='data')], titles=uploaded_df.columns.values,dts=[data_dsc.to_html(classes='data')],tot = total_data ,dt = name_file)


@app.route('/rekomendasi', methods=['GET', 'POST'])
def rekomendasi():
    items=[]
    file_list = list(get_files(path))
    for item in file_list:
        file_ext = item.split('.')
        if file_ext[1] in '.pdf':
            items.append(item)
    return render_template('download_page.html', files = items)   


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
    return render_template('preprocessing.html',tables=[data_view.to_html(classes='data')], titles=uploaded_df.columns.values,dts=[data_dsc.to_html(classes='data')],tot = total )



@app.route('/apriori')
def apriori():

    try:
        dict_obj = session['data_view'] if 'data_group' in session else ""  
        data_view = pd.DataFrame(dict_obj)
    except:
        return render_template('apriori.html',)


    return render_template('apriori.html',tables=[data_view.to_html(classes='data')], titles=data_view.columns.values)


@app.route('/apriori', methods=['POST'])
def apriori_refresh():
    from apyori import apriori
    data_file_path = session.get('uploaded_data_file_path', None)
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
    association_rules = apriori(records,min_support = sup,min_confidence = co,min_lift = 2,min_length = 2)
    association_results = list(association_rules)
    dtf = []
    for item in association_results:
        pair = item[0]
        items = [x for x in pair]
        ds = {'Item1': f"{items[0]}", "Rekomendasi": f"{items[1]}", 'Support': f"{str(round(item[1], 3))}", 'Confidence:': f"{str(int(item[2][0][2] * 100))}%", 'lift': f"{str(round(item[2][0][3], 3))}"}

        dtf.append(ds)
    result = pd.DataFrame(dtf)
    association_rules_pdf = apriori(records,min_support = sup,min_confidence = co,min_lift = 2,min_length = 2)
    association_results_pdf = list(association_rules_pdf)
    dtf_pdf = []
    for item in association_results_pdf:
        pair = item[0]
        items = [x for x in pair]
        ds_pdf = {'Item1': f"{items[0]}", "Rekomendasi": f"{items[1]}", 'lift': f"{str(round(item[2][0][3], 3))}"}

        dtf_pdf.append(ds_pdf)
    result_pdf = pd.DataFrame(dtf_pdf)
    folder = os.path.join(os.getcwd(), 'storage')

    # demo_df = pd.DataFrame(np.random.random((10,3)), columns = ("col 1", "col 2", "col 3"))

    nama_file = Path(f'{data_file_path}').stem
    
    
    html = render_template('dataframe.html', tables=[result_pdf.to_html(classes='data')], titles=result.columns.values)
    pdfkit.from_string(html, f'/{folder}/{nama_file}_sup:{min_support}%_co:{min_confidence}%.pdf', options=kitoptions)

    message = f"succesfully save pdft at {folder}"
    
    return render_template('apriori.html', tables=[result.to_html(classes='data')], titles=result.columns.values, mes= message)

@app.route('/clr')
def ab():
    session.clear()

    
    return render_template('index.html')


@app.route('/download_page/<file>',methods=['GET', 'POST'])
def download_page(file):
    path_folder = os.path.join(os.getcwd(), 'storage')
    path = f"{path_folder}/{file}"
    return send_file(path, as_attachment=True)
