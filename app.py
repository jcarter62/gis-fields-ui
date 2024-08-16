import tempfile
from flask import Flask, render_template, send_file, send_from_directory, request
from dotenv import load_dotenv
import pandas as pd
import requests
import os

load_dotenv()

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    title = 'Home'
    context = {
        'title': title,
        'heading': 'Welcome to the Flask App',
        'subheading': 'This is the home page',
        'content': 'This is the content of the home page',
#        'apiurl': os.getenv('APIURL', ''),
    }
    return render_template('home.html', context=context)


@app.route('/view1')
def view1():  # put application's code here
    title = 'View Results - Part 1'

    apiurl = os.getenv('APIURL', '')
    if apiurl == '':
        return {"message": "API URL not set"}, 401
    url = f'{apiurl}/data/load-part1'
    response = requests.get(url)
    if response.status_code != 200:
        return {"message": "API call failed"}, 401

    response_data = response.json()
    data = response_data[0]['data']

    context = {
        'title': title,
        'content': data,
    }
    return render_template('view1.html', context=context)

@app.route('/view1-download')
def view1Download():
    apiurl = os.getenv('APIURL', '')
    if apiurl == '':
        return {"message": "API URL not set"}, 401
    url = f'{apiurl}/data/load-part1'
    response = requests.get(url)
    if response.status_code != 200:
        return {"message": "API call failed"}, 401

    response_data = response.json()
    data = response_data[0]['data']

    # create temp file.xlsx
    tempfolder = os.getenv('TEMPFOLDER', '')
    if tempfolder == '':
        return {"success": False, "message": "Temp folder not set"}

    # remove all .xlsx files in tempfolder
    for file in os.listdir(tempfolder):
        if file.endswith('.xlsx'):
            file_path = os.path.join(tempfolder, file)
            os.remove(file_path)

    # create tempfilename
    tmpFile = tempfile.NamedTemporaryFile(delete=False, dir=tempfolder, suffix='.xlsx')

    # Convert data to DataFrame
    df = pd.DataFrame(data)

    shtName = 'GIS_Cmp_Results_01'
    df.to_excel(tmpFile.name, index=False, sheet_name=shtName)

    return send_file(tmpFile.name, download_name='gis_compare_results.xlsx', as_attachment=True)


@app.route('/view2')
def view2():  # put application's code here
    title = 'View Results - Part 2'

    apiurl = os.getenv('APIURL', '')
    if apiurl == '':
        return {"message": "API URL not set"}, 401
    url = f'{apiurl}/data/load-part2'
    response = requests.get(url)
    if response.status_code != 200:
        return {"message": "API call failed"}, 401

    response_data = response.json()
    data = response_data[0]['data']

    context = {
        'title': title,
        'content': data,
    }
    return render_template('view2.html', context=context)


### @app.post('/api/clear-old-data')
def clear_old_data():
    apiurl = os.getenv('APIURL', '')
    if apiurl == '':
        return 401
    url = f'{apiurl}/data/trunc-table'
    response = requests.get(url)
    code = response.status_code

    return code

@app.post('/api/process-data')
def process_data():
    apiurl = os.getenv('APIURL', '')
    if apiurl == '':
        return {"message": "API URL not set"}, 401
    url = f'{apiurl}/data/process-data'
    response = requests.post(url)

    code = response.status_code
    if code == 200:
        msg = "File uploaded successfully"
    else:
        msg = "File upload failed"

    return {"message": msg}, code

@app.post('/api/upload')
def upload_file():
    if 'file' not in request.files:
        return {"message": "No file part"}, 400

    file = request.files['file']
    if file.filename == '':
        return {"message": "No selected file"}, 400

    # Remove all data in the table before uploading new data.
    clear_old_data()

    # Save file to memory
    file_content = file.read()

    # You can now process the file_content as needed
    # For example, you can save it to a database or process it in-memory

    apiurl = os.getenv('APIURL', '')
    url = f'{apiurl}/upload/{file.filename}'
    files = {'file': file_content }
    response = requests.post(url, files=files)

    code = response.status_code
    if code == 200:
        msg = "File uploaded successfully"
    else:
        msg = "File upload failed"

    return {"message": msg}, code


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon'), 200

@app.route('/static/<path>')
def send_static(path):
    return send_from_directory('static', path), 200


if __name__ == '__main__':
    hostip = os.getenv('HOST', '')
    port_number = os.getenv('PORT', '')
    if hostip == '' or port_number == '':
        print('HOST or PORT not set in .env file')
        exit()

    app.run(host=hostip, port=int(port_number), debug=False)
