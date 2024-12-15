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
if __name__ == "__main__":
    print(obtener_contraseña("joseph@peru4stream.com"))