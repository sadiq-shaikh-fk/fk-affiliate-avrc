from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
from all_functions import start
from flask_cors import CORS
from io import BytesIO
import pandas as pd
import traceback
import zipfile
import atexit
import uuid
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit

# Ensure CORS is enabled
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=100 * 1024 * 1024)

# Temporary storage for processed file path
temp_file_path = None

# Store processed data in memory
processed_data = {}

@app.errorhandler(413)
def request_entity_too_large(error):
    return {'status': f'File too large. Please upload a file smaller than 10MB - {error}'}, 413

# ------------------------------------ Adding all Routes ------------------------------------
@app.route("/")
def index():
    return render_template('uploadPage.html')

@app.route('/fetch', methods=['POST', 'GET'])
def fetch():
    global temp_file_path
    if request.method == 'POST':
        if 'file' not in request.files:
            print('Upload a file first')
            socketio.emit('upload_status', {'status': 'Upload a file first'}, namespace='/')
            return '', 400

        file = request.files['file']

        if file.filename == '':
            return {'status': 'No file selected'}, 400        
    
        if not file.filename.lower().endswith('.csv'):
            print('Invalid file type. Please upload a CSV file.')
            socketio.emit('upload_status', {'status': 'Invalid file type. Please upload a CSV file.'}, namespace='/')
            return {'status': 'Invalid file type. Please upload a CSV file.'}, 400

        if file:
            try:
                print('File uploaded successfully')
                socketio.emit('upload_status', {'status': 'File uploaded successfully'}, namespace='/')

                # Process the file in memory
                agency_pivotdf_dict = start(file)
            
                print('File uploaded successfully')
                socketio.emit('upload_status', {'status': 'File uploaded successfully'}, namespace='/')

                # Generate ZIP of Excel files in memory
                zip_of_excel = generate_zip_of_excel(agency_pivotdf_dict)

                #  Generate a unique ID for this processed data
                file_id = str(uuid.uuid4())
                processed_data[file_id] = zip_of_excel

                socketio.emit('upload_status', {'status': 'Files processed and zipped successfully'}, namespace='/')
                return {'status': 'Files processed and zipped successfully', 'file_id': file_id}, 200  # Return file_id to client
            except Exception as e:
                error_msg = f"Error processing file: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)  # Print to server console
                socketio.emit('upload_status', {'status': error_msg}, namespace='/')
                return '', 500

    elif request.method == 'GET':
        file_id = request.args.get('file_id')
        if file_id not in processed_data:
            socketio.emit('upload_status', {'status': 'No processed file available'}, namespace='/')
            return '', 404
        
        else:
            try:
                zip_of_excel = processed_data[file_id]
                zip_of_excel.seek(0)
                return send_file(
                    zip_of_excel,
                    as_attachment=True,
                    download_name='output.zip',
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            except Exception as e:
                error_msg = f"Error downloading file: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)  # Print to server console
                socketio.emit('upload_status', {'status': error_msg}, namespace='/')
                return '', 500
            finally:
                socketio.sleep(1)  # Add a small delay
                # Remove the processed data after sending
                del processed_data[file_id]

    else:
        socketio.emit('upload_status', {'status': 'Unknown error occurred'}, namespace='/')
        return '', 405

@app.route('/cleanup', methods=['POST'])
def cleanup():
    global temp_file_path
    cleanup_temp_file()
    return '', 200

# Update the cleanup function to handle potential errors
def cleanup_temp_file():
    global temp_file_path
    if temp_file_path and os.path.exists(temp_file_path):
        try:
            os.remove(temp_file_path)
            print(f"Cleaned up temporary file: {temp_file_path}")
        except PermissionError:
            print(f"Unable to remove file: {temp_file_path}. It may still be in use.")
        finally:
            temp_file_path = None

atexit.register(cleanup_temp_file)

# ------------------------------------- Other Functions ----------------------------------------
def generate_zip_of_excel(agency_pivotdf_dict):
    excel_files = {}

    # Iterate through the agency_pivotdf_dict to create in-memory Excel files
    for agency_name, dfs in agency_pivotdf_dict.items():
        original_df, pivoted_df = dfs
        
        # Create a BytesIO object to hold the Excel file in memory
        excel_buffer = BytesIO()
        
        # Create an Excel writer object and add the DataFrames as sheets
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            original_df.to_excel(writer, sheet_name='Raw Data', index=False)
            pivoted_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Save the BytesIO object to the dictionary
        excel_files[agency_name] = excel_buffer

    # Create a zip file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for agency_name, excel_buffer in excel_files.items():
            # Seek to the beginning of the BytesIO object before writing
            excel_buffer.seek(0)
            # Write the BytesIO object to the zip file with the agency name as the file name
            zipf.writestr(f"{agency_name}.xlsx", excel_buffer.read())

    # Seek to the beginning of the zip_buffer before returning
    zip_buffer.seek(0)
    return zip_buffer

# ------------------------------------- Run the app! -------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8090))
    socketio.run(app, host='0.0.0.0', port=port)





# from flask import Flask, render_template, request, send_file
# from flask_socketio import SocketIO
# from all_functions import start
# from flask_cors import CORS
# from io import BytesIO
# import pandas as pd
# import traceback
# import atexit
# import uuid
# import os

# app = Flask(__name__)
# app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit

# # Ensure CORS is enabled
# CORS(app, resources={r"/*": {"origins": "*"}})
# socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=100 * 1024 * 1024)

# # Temporary storage for processed file path
# temp_file_path = None

# # Store processed data in memory
# processed_data = {}

# # ------------------------------------ Adding all Routes ------------------------------------
# @app.route("/")
# def index():
#     return render_template('uploadPage.html')

# @app.route('/fetch', methods=['POST', 'GET'])
# def fetch():
#     global temp_file_path
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             print('Uplaod a file to First')
#             socketio.emit('upload_status', {'status':'Uplaod a file to First'}, namespace='/')
#             return '', 400

#         file = request.files['file']
    
#         if file:
#             try:
#                 # Process the file in memory
#                 agency_pivotdf_dict = start(file)
            
#                 print('File uploaded successfully')
#                 socketio.emit('upload_status', {'status': 'File uploaded successfully'}, namespace='/')

#                 # Generate Excel file in memory
#                 excel_file = generate_excel_file(agency_pivotdf_dict)

#                 #  Generate a unique ID for this processed data
#                 file_id = str(uuid.uuid4())
#                 processed_data[file_id] = excel_file

#                 socketio.emit('upload_status', {'status': 'File processed successfully'}, namespace='/')
#                 return {'status': 'File processed successfully', 'file_id': file_id}, 200  # Return file_id to client
#             except Exception as e:
#                 error_msg = f"Error processing file: {str(e)}\n{traceback.format_exc()}"
#                 print(error_msg)  # Print to server console
#                 socketio.emit('upload_status', {'status': error_msg}, namespace='/')
#                 return '', 500

#     elif request.method == 'GET':
#             file_id = request.args.get('file_id')
#             if file_id not in processed_data:
#                 socketio.emit('upload_status', {'status': 'No processed file available'}, namespace='/')
#                 return '', 404
            
#             else:
#                 try:
#                     excel_file = processed_data[file_id]
#                     excel_file.seek(0)
#                     return send_file(
#                         excel_file,
#                         as_attachment=True,
#                         download_name='output.xlsx',
#                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#                     )
#                 except Exception as e:
#                     error_msg = f"Error downloading file: {str(e)}\n{traceback.format_exc()}"
#                     print(error_msg)  # Print to server console
#                     socketio.emit('upload_status', {'status': error_msg}, namespace='/')
#                     return '', 500
#                 finally:
#                     socketio.sleep(1)  # Add a small delay
#                     # Remove the processed data after sending
#                     del processed_data[file_id]

#     else:
#         socketio.emit('upload_status', {'status': 'Unknown error occurred'}, namespace='/')
#         return '', 405

# @app.route('/cleanup', methods=['POST'])
# def cleanup():
#     global temp_file_path
#     cleanup_temp_file()
#     return '', 200
    

# # Update the cleanup function to handle potential errors
# def cleanup_temp_file():
#     global temp_file_path
#     if temp_file_path and os.path.exists(temp_file_path):
#         try:
#             os.remove(temp_file_path)
#             print(f"Cleaned up temporary file: {temp_file_path}")
#         except PermissionError:
#             print(f"Unable to remove file: {temp_file_path}. It may still be in use.")
#         finally:
#             temp_file_path = None

# atexit.register(cleanup_temp_file)

# # ------------------------------------- Other Functions ----------------------------------------
# def generate_excel_file(agency_pivotdf_dict):
#     output = BytesIO()
#     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#         for sheet_name, df in agency_pivotdf_dict.items():
#             df.to_excel(writer, sheet_name=str(sheet_name), index=False)
#     output.seek(0)
#     return output

# # ------------------------------------- Run the app! -------------------------------------
# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 8090))
#     socketio.run(app, host='0.0.0.0', port=port)