import imaplib
import email
from email.header import decode_header
import html
import os
from dotenv import load_dotenv


load_dotenv()

# Configuración
IMAP_SERVER = os.getenv("IMAP_SERVER")


def filtrar_correos_de_servicios(subject, sender, servicio):
    """
    Filtra los correos basados en el asunto y el remitente (servicio).
    :param subject: Asunto del correo.
    :param sender: Dirección del remitente.
    :param servicio: Nombre del servicio (como Disney, Netflix, etc.).
    :return: True si el correo cumple con los criterios, False en caso contrario.
    """
    # Palabras clave para identificar correos relacionados con códigos
    palabras_clave ={"netflix":[] , "max":[] , "disney":["código de acceso único para Disney+"] , "amazon":["intento de inicio de sesión"] }
    if servicio == "prime":
        servicio = "amazon"
    # Comprobamos si el remitente contiene el nombre del servicio
    if servicio.lower() in sender.lower():
        #print(subject)
        # Comprobamos si el asunto contiene alguna palabra clave
        for palabra in palabras_clave[servicio]:
            if palabra.lower() in subject.lower():
                return True
    return False




# Conectar al servidor IMAP

def get_last_mails(email_address, password, service):
    try:
        # Conectar al servidor IMAP con SSL
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(email_address, password)

        # Seleccionar la bandeja de entrada
        mail.select("inbox")

        # Buscar todos los correos
        status, messages = mail.search(None, "ALL")

        if status != "OK":
            raise Exception("No se pudieron recuperar los correos.")

        # Convertir resultados en una lista de IDs
        email_ids = messages[0].split()

        # Diccionario para almacenar los correos
        res = {}

        # Leer los 5 correos más recientes
        for count, email_id in enumerate(email_ids[-2:], start=1):
            body = ""
            status, msg_data = mail.fetch(email_id, "(RFC822)")

            if status != "OK":
                print(f"No se pudo recuperar el correo con ID {email_id}.")
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Decodificar mensaje
                    msg = email.message_from_bytes(response_part[1])

                    # Decodificar asunto
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    # Emisor
                    sender = msg.get("From")

                    # Procesar el cuerpo del correo
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            elif content_type == "text/html" and "attachment" not in content_disposition:
                                html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                body += html.escape(html_body)  # Escapar para evitar inyección de código
                    else:
                        content_type = msg.get_content_type()
                        if content_type == "text/plain":
                            body += msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        elif content_type == "text/html":
                            html_body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                            body += html.escape(html_body)  # Escapar para evitar inyección

                    # Construir el diccionario
                    if filtrar_correos_de_servicios(subject, sender, service):
                        res[count] = {
                            "Asunto": subject,
                            "Emisor": sender,
                            "Cuerpo": body,  # Texto plano
                            "CuerpoHtml": html_body,  # HTML sin escapar
                        }

        mail.logout()
        return res

    except Exception as e:
        print(f"Error: {e}")
        return {}

