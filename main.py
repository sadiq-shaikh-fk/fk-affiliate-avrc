from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_cors import CORS
import tempfile
from all_functions import start

app = Flask(__name__)

# Ensure CORS is enabled
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# ------------------------------------ Adding all Routes ------------------------------------
@app.route("/")
def index():
    return render_template('uploadPage.html')

@app.route('/fetch', methods=['POST'])
def fetch():
    if 'file' not in request.files:
        print('Uplaod a file to First')
        socketio.emit('upload_status', {'status':'Uplaod a file to First'}, namespace='/')
        return '', 400
    
    file = request.files['file']

    if file.filename == '':
        print('No File Selected')
        socketio.emit('upload_status', {'status':'No File Selected'}, namespace='/')
        return '', 400
    
    if file:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_file = temp_file.name

        #session['data'] = temp_file
        
        # Store upload process in the session
        #session['search_params'] = {'process': 'upload', 'data': temp_file}
        #output_data_path = start(temp_file)
        print(type(temp_file))
        print('File uploaded successfully')
        socketio.emit('upload_status', {'status': 'File uploaded successfully'}, namespace='/')

        return '', 400
    
if __name__ == '__main__':
    socketio.run(app, debug=True)