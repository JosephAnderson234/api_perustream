from flask import Flask, jsonify, request, abort
import sql, mails, json
from flask_cors import CORS
import os
from dotenv import load_dotenv
import re, time

app = Flask(__name__)
CORS(app)

def es_correo_alfanumerico(email):
    # Expresión regular para correos alfanuméricos
    patron = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))

import requests
load_dotenv()

headers = {
    'Authorization': f'cpanel {os.getenv("USER_API")}:{os.getenv("TOKEN_API")}'
}

allowed_ips = os.getenv("ALLOWED_IPS")

# Convertir la cadena en una lista
if allowed_ips:
    allowed_ips_list = allowed_ips.split(",")
else:
    allowed_ips_list = []

url1 = f'https://peru4stream.com:{os.getenv("PORT_API")}/execute/Email/'
url2 = f'https://peru4stream.com:{os.getenv("PORT_API")}/execute/Mailboxes/'



# Ruta principal de la API

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "API de correos"
    })

@app.route('/get_mails', methods=['GET'])
def home():
    try: 
        response = requests.get(url1+'list_pops', headers=headers)
        return response.json(), 200
    except Exception as e:
        print(e)
        return json.dumps({
            "Error": e
            }), 500


"""@app.route('/create_mail', methods=['GET'])
def create_mail():
    data = request.get_json()
    response = requests.get(url1+'add_pop', headers=headers, data=data)
    return response.json(), 200"""



@app.before_request
def limit_remote_addr():
    print(request.remote_addr)
    """if not request.remote_addr in allowed_ips_list:
        abort(403)"""


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    res = sql.probar_login(data["username"], data["password"])
    if res:
        return json.dumps({
                "ok":"yes",
                "data" : res
            }), 200
    else: 
        return json.dumps({
            "Error": "Credenciales inválidas"
            }), 200

@app.route('/getDashboard', methods=['POST'])
def getDasboard():
    #get the token from the request in the headers
    token = request.headers.get('Authorization')
    data = sql.validar_token(token)
    if data:
        return {
            "ok": "yes",
            "data":sql.obtener_data_dashboard()
        }, 200
    else:
        return json.dumps({
            "Error": "Token inválido"
            }), 200

@app.route('/getSellers', methods=['POST'])
def getSellers():
    #get the token from the request in the headers
    token = request.headers.get('Authorization')
    data = sql.validar_token(token)
    if data:
        return {
            "ok": "yes",
            "data":sql.obtener_data_vendedores()
        }, 200
    else:
        return json.dumps({
            "Error": "Token inválido"
            }), 200


@app.route('/return_messages', methods=['POST'])
def return_message():
    data = request.get_json()
    #response = requests.get(url2+'get_mailbox_status_list', headers=headers, data=data)
    if (not es_correo_alfanumerico(data["email"])):
        return json.dumps({
            "1": {
                "Asunto": "Correo inválido"
            }
            }), 400
    time.sleep(3)
    if (not sql.validar_correo(data["email"])):
        return json.dumps({
            "1": {
                "Asunto": "Correo no registrado"
            }
            }), 400
    
    if (not sql.validar_credenciales_vendedores(data["username"], data["cellphone"], data["email"], data["service"])):
        return json.dumps({
            "1": {
                "Asunto": "Usuario inválido o no tienes acceso a este correo"
            }
            }), 400
    pws = sql.obtener_contraseña(data["email"])
    
    response = mails.get_last_mails(data["email"], pws, data["service"])

    return json.dumps(response), 200

@app.route('/edit_expiration_date', methods=['POST'])
def edit_expiration_date():
    data = request.get_json()
    #get the token from the request in the headers
    token = request.headers.get('Authorization')
    data_token = sql.validar_token(token)
    if data_token:
        sql.editar_fecha_de_vencimiento(data["id_cuenta"], data["date"])
        return json.dumps({
            "ok": "yes"
        }), 200
    else:
        return json.dumps({
            "Error": "Token inválido"
            }), 200
        
@app.route('/setUpAnAccount', methods=['POST'])
def asignar_vendedor():
    data = request.get_json()
    #get the token from the request in the headers
    token = request.headers.get('Authorization')
    data_token = sql.validar_token(token)
    if data_token:
        if data["tipo"] != "completa":
            sql.asginar_cuenta_perfil_a_vendedor(data["id_cuenta"], data["date"], data["id_vendedor"], data["numero_cuenta"])
        else:
            sql.asginar_cuenta_completa_a_vendedor(data["id_cuenta"], data["id_vendedor"], data["date"])
        return json.dumps({
            "ok": "yes"
        }), 200
    else:
        return json.dumps({
            "Error": "Token inválido"
            }), 200


@app.route('/updateToken', methods=['POST'])
def updateToken():
    
    sql.actualizar_tokens_vendedores()
    
    return json.dumps({
        'ok':'yes'}), 200
""" 
@app.route('/validate', methods=['GET'])
def validate_pwsd():
    data = request.get_json()
    response = requests.get(url1+'verify_password', headers=headers, data=data)
    return response.json(), 200 """

# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True)