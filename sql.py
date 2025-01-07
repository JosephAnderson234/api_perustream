import datetime
import pymysql
import os
from dotenv import load_dotenv

# Cargar las variables desde el archivo .env
load_dotenv()

# Variables de entorno
host = os.getenv("HOST")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
database = os.getenv("DATABASE")
port = 3306


# Función genérica para ejecutar consultas
def ejecutar_consulta(consulta_sql, parametros=None, fetchone=False):
    try:
        # Conexión a la base de datos
        connection = pymysql.connect(
            host=host, user=user, password=password, database=database, port=port
        )
        with connection.cursor() as cursor:
            cursor.execute(consulta_sql, parametros)
            connection.commit()
            return cursor.fetchone() if fetchone else cursor.fetchall()
    except Exception as e:
        print("Error:", e)
        return None
    finally:
        if "connection" in locals():
            connection.close()


# Funciones específicas
def obtener_contraseña(correo):
    consulta_sql = "SELECT contraseña FROM cuentas WHERE correo = %s;"
    resultado = ejecutar_consulta(consulta_sql, (correo,), fetchone=True)
    return (
        resultado[0]
        if resultado
        else f"No se encontró una contraseña asociada al correo {correo}"
    )


def validar_credenciales_vendedores(nombre, celular, correo, service):
    consulta_vendedor = (
        "SELECT id_vendedor FROM vendedores WHERE username = %s AND telefono = %s;"
    )
    id_vendedor = ejecutar_consulta(consulta_vendedor, (nombre, celular), fetchone=True)

    if id_vendedor:
        consulta_servicio = """
            SELECT id_cuenta 
            FROM cuentas_servicios 
            WHERE correo = %s AND id_vendedor = %s AND servicio = %s;
        """
        id_cuenta = ejecutar_consulta(
            consulta_servicio, (correo, id_vendedor[0], service), fetchone=True
        )
        if id_cuenta:
            fecha_actual = datetime.date.today()
            print(
                f"{fecha_actual} - El vendedor {nombre} accedió a la bandeja del correo {correo} en el servicio {service}"
            )
            return True
    return False


def validar_token(token):
    consulta_sql = "SELECT id_vendedor, token FROM vendedores WHERE token = %s;"
    return ejecutar_consulta(consulta_sql, (token,), fetchone=True)


def validar_correo(email):
    consulta_sql = "SELECT correo FROM cuentas WHERE correo = %s;"
    resultado = ejecutar_consulta(consulta_sql, (email,), fetchone=True)
    return bool(resultado)


def obtener_data_dashboard():
    consulta_sql = "SELECT * FROM cuentas_servicios;"
    return ejecutar_consulta(consulta_sql)


def obtener_data_vendedores():
    consulta_sql = """SELECT 
                        v.*,
                        COALESCE(cs.veces_aparece, 0) AS veces_aparece
                    FROM 
                        vendedores v
                    LEFT JOIN (
                        SELECT 
                            id_vendedor, 
                            COUNT(*) AS veces_aparece
                        FROM 
                            cuentas_servicios
                        WHERE 
                            fecha_vencimiento > CURRENT_DATE -- Validar que la fecha de vencimiento no haya pasado
                        GROUP BY 
                            id_vendedor
                    ) cs 
                    ON v.id_vendedor = cs.id_vendedor;"""
    return ejecutar_consulta(consulta_sql)


def probar_login(usuario, contraseña):
    consulta_sql = """
        SELECT id_vendedor, tipo_cuenta, name, token  
        FROM vendedores 
        WHERE username = %s AND contrasena = %s;
    """
    return ejecutar_consulta(consulta_sql, (usuario, contraseña), fetchone=True)


def editar_fecha_de_vencimiento(id_cuenta, fecha):
    consulta_sql = """
        UPDATE cuentas_servicios
        SET fecha_vencimiento = %s
        WHERE id_cuenta = %s;
    """
    return ejecutar_consulta(consulta_sql, (fecha, id_cuenta))

def asginar_cuenta_completa_a_vendedor(id_cuenta, id_vendedor, fecha_vencimiento):
    consulta_sql = """
        UPDATE cuentas_servicios
        SET id_vendedor = %s , fecha_vencimiento = %s, tipo='completa', perfil = 0
        WHERE id_cuenta = %s;
    """
    print(ejecutar_consulta(consulta_sql, (int(id_vendedor), fecha_vencimiento, int(id_cuenta))))


def asginar_cuenta_perfil_a_vendedor(id_cuenta, id_vendedor, fecha_vencimiento, perfil):
    consulta_sql = """
        UPDATE cuentas_servicios
        SET id_vendedor = %s , fecha_vencimiento = %s, tipo='perfil', perfil = %s
        WHERE id_cuenta = %s;
    """
    return ejecutar_consulta(consulta_sql, (id_vendedor, fecha_vencimiento, perfil, id_cuenta))

def actualizar_tokens_vendedores():
    consulta_sql = """
        UPDATE usuarios
    SET token = MD5(CONCAT(id_usuario, CURDATE()))
    """
    return ejecutar_consulta(consulta_sql)

if __name__ == "__main__":
    
    print(ejecutar_consulta("UPDATE cuentas_servicios SET id_vendedor = 1 WHERE id_cuenta = 1"))
    print(ejecutar_consulta("SELECT * FROM cuentas_servicios;"))
