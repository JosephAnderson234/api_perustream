import datetime
import pymysql
import os
from dotenv import load_dotenv

# Cargar las variables desde el archivo .env
load_dotenv()


host = os.getenv("HOST")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
database = os.getenv("DATABASE")
port = 3306

def obtener_contraseña(correo):    
    consulta_sql = """
        SELECT contraseña 
        FROM cuentas 
        WHERE correo = %s;
    """
    
    try:
        # Conexión a la base de datos
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )

        # Crear cursor y ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(consulta_sql, (correo,))
            resultado = cursor.fetchone()  # Obtener un solo resultado
            if resultado:
                #print(f"La contraseña asociada al correo {correo} es: {resultado[0]}")
                connection.close()
                return resultado[0]
            else:
                connection.close()
                return f"No se encontró una contraseña asociada al correo {correo}"

    except Exception as e:
        print("Error:", e)

def validar_credenciales_vendedores(nombre, celular, correo, service):
    consulta_sql = """
        SELECT id_vendedor
        FROM vendedores 
        WHERE username = %s AND telefono = %s;
    """
    
    consulta_para_correos_servicios = """
        SELECT id_cuenta
        FROM cuentas_servicios 
        WHERE correo = %s AND id_vendedor = %s AND servicio = %s;    
    """
    
    try:
        # Conexión a la base de datos
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )

        # Crear cursor y ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(consulta_sql, (nombre, celular))
            id_vendedor = cursor.fetchone()  #validar si hay un vendedor
            #print(id_vendedor)
            if id_vendedor:
                cursor.execute(consulta_para_correos_servicios, (correo, id_vendedor[0], service))
                id_cuenta = cursor.fetchone()
                if id_cuenta:
                    fecha_actual = datetime.date.today()
                    print(fecha_actual, end=" - ")
                    print(f"El vendedor {nombre} accedió a la bandeja del correo {correo} en el servicio {service}")
                    return True
                return False
            return False
    except Exception as e:
        print("Error:", e)
    finally:
        connection.close()

def validar_token(token):
    consulta_sql = """
        SELECT id_usuario, token 
        FROM usuarios 
        WHERE token = %s;
    """
    
    try:
        # Conexión a la base de datos
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )

        # Crear cursor y ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(consulta_sql, (token))
            resultado = cursor.fetchone()  # Obtener un solo resultado
        return resultado
    except Exception as e:
        print("Error:", e)
    finally:
        connection.close()

def validar_correo(email):
    consulta_sql = """
        SELECT correo 
        FROM cuentas 
        WHERE correo = %s;
    """
    
    try:
        # Conexión a la base de datos
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )

        # Crear cursor y ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(consulta_sql, (email))
            resultado = cursor.fetchone()  # Obtener un solo resultado
            if resultado:
                return True
            return False
    except Exception as e:
        print("Error:", e)
    finally:
        connection.close()

def obtener_data_dasboard():
    consulta_sql = """
        SELECT * 
        FROM cuentas_servicios;
    """
    try:
        # Conexión a la base de datos
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )

        # Crear cursor y ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(consulta_sql)
            resultado = cursor.fetchall() 
            if resultado:
                return resultado
        
    except Exception as e:
        print("Error:", e)
    finally:
        connection.close()

def obtener_data_vendedores():
    consulta_sql = """
        SELECT * 
        FROM vendedores;
    """
    try:
        # Conexión a la base de datos
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )

        # Crear cursor y ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(consulta_sql)
            resultado = cursor.fetchall() 
            if resultado:
                return resultado
        
    except Exception as e:
        print("Error:", e)
    finally:
        connection.close()

def probar_login(usuario, contraseña):
    consulta_sql = """
        SELECT id_usuario, tipo_usuario, name, token 
        FROM usuarios 
        WHERE usuario = %s AND contrasena = %s;
    """
    
    try:
        # Conexión a la base de datos
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )

        # Crear cursor y ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(consulta_sql, (usuario, contraseña))
            resultado = cursor.fetchone()  # Obtener un solo resultado
        return resultado
        
    except Exception as e:
        print("Error:", e)
    finally:
        connection.close()

