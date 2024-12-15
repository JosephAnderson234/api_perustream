from flask import Flask, jsonify, request
import sql, mails, json
from flask_cors import CORS
import os
from dotenv import load_dotenv


app = Flask(__name__)
CORS(app)

import requests
load_dotenv()

headers = {
    'Authorization': f'cpanel {os.getenv("USER_API")}:{os.getenv("TOKEN_API")}'
}

url1 = f'https://peru4stream.com:{os.getenv("PORT_API")}/execute/Email/'
url2 = f'https://peru4stream.com:{os.getenv("PORT_API")}/execute/Mailboxes/'



# Ruta principal de la API
@app.route('/get_mails', methods=['GET'])
def home():
    response = requests.get(url1+'list_pops', headers=headers)
    return response.json(), 200

@app.route('/create_mail', methods=['GET'])
def create_mail():
    data = request.get_json()
    response = requests.get(url1+'add_pop', headers=headers, data=data)
    return response.json(), 200

@app.route('/return_messages', methods=['POST'])
def return_message():
    data = request.get_json()
    #response = requests.get(url2+'get_mailbox_status_list', headers=headers, data=data)
    pws = sql.obtener_contraseña(data["email"])
    
    response = mails.get_last_mails(data["email"], pws)
    
    return json.dumps(response), 200

@app.route('/validate', methods=['GET'])
def validate_pwsd():
    data = request.get_json()
    response = requests.get(url1+'verify_password', headers=headers, data=data)
    return response.json(), 200

# Iniciar el servidor
if __name__ == '__main__':
    app.run()