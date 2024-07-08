from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO
from all_functions import start
from flask_cors import CORS
from io import BytesIO
import pandas as pd
import tempfile
import os

app = Flask(__name__)

# Ensure CORS is enabled
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Temporary storage for processed file path
temp_file_path = None

# ------------------------------------ Adding all Routes ------------------------------------
@app.route("/")
def index():
    return render_template('uploadPage.html')

@app.route('/fetch', methods=['POST', 'GET'])
def fetch():
    global temp_file_path
    if request.method == 'POST':
        if 'file' not in request.files:
            print('Uplaod a file to First')
            socketio.emit('upload_status', {'status':'Uplaod a file to First'}, namespace='/')
            return '', 400

        file = request.files['file']

        if 'file' not in request.files:
            print('Uplaod a file to First')
            socketio.emit('upload_status', {'status':'Uplaod a file to First'}, namespace='/')
            return '', 400
    
        if file:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                file.save(temp_file.name)
                input_file_path = temp_file.name
            
            print('File uploaded successfully')
            socketio.emit('upload_status', {'status': 'File uploaded successfully'}, namespace='/')

            agency_pivotdf_dict = start(input_file_path)

        # Save processed data to a temporary Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for key, value in agency_pivotdf_dict.items():
                value.to_excel(writer, sheet_name=str(key), index=False)
        output.seek(0)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_output:
            temp_output.write(output.getvalue())
            temp_file_path = temp_output.name

            socketio.emit('upload_status', {'status': 'File processed successfully'}, namespace='/')
            return '', 200

    elif request.method == 'GET':
            if temp_file_path is None or not os.path.exists(temp_file_path):
                socketio.emit('upload_status', {'status': 'No processed file available'}, namespace='/')
                return '', 404
            else:
                return send_file(
                    temp_file_path,
                    as_attachment=True,
                    download_name='output.xlsx',
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

    else:
        socketio.emit('upload_status', {'status': 'Unknown error occurred'}, namespace='/')
    

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8090)