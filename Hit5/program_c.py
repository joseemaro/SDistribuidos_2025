import socket
import threading
import time
import os
import json
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Cargar variables de entorno
load_dotenv()

NODE_NAME = os.getenv('NODE_NAME')
LISTEN_HOST = os.getenv('LISTEN_HOST')
LISTEN_PORT = int(os.getenv('LISTEN_PORT'))
PEER_HOST = os.getenv('PEER_HOST')
PEER_PORT = int(os.getenv('PEER_PORT'))

RETRY_INTERVAL = 5  # Tiempo entre intentos de reconexión
MESSAGE_INTERVAL = 5  # Tiempo entre cada mensaje enviado
SECONDS_TO_AWAIT_SERVER_START = 2


# Configuración de logs
class NodeNameFilter(logging.Filter):
    def filter(self, record):
        record.NODE_NAME = NODE_NAME
        return True

log_file = f"logs/output.log"
log_handler = RotatingFileHandler(
    log_file, 
    maxBytes=500 * 1024 * 1024,  
    backupCount=2,
    encoding="utf-8"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s, [%(levelname)s], [%(NODE_NAME)s], [%(filename)s]: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    handlers=[log_handler]
)
logging.getLogger().addFilter(NodeNameFilter())


# Serializar y enviar mensajes en JSON
def send_json(socket, message_dict):
    json_message = json.dumps(message_dict)
    socket.sendall(json_message.encode())


# Recibir y deserializar mensajes en JSON
def receive_json(socket):
    data = socket.recv(1024).decode()
    if not data:
        return None
    try:
        return json.loads(data)  # Convertir de JSON a diccionario
    except json.JSONDecodeError:
        logging.error(f"[{NODE_NAME}] Error al decodificar JSON: {data}")
        return None


# Manejo de conexiones entrantes
def handle_connection(conn, addr):
    try:
        while True:
            received_data = receive_json(conn)
            if not received_data:
                break
            
            logging.info(f"[{NODE_NAME}] Mensaje recibido: {received_data}")

            # Responder con un mensaje en JSON
            response = {"node": NODE_NAME, "message": "Hola desde " + NODE_NAME}
            send_json(conn, response)
    finally:
        conn.close()


# Servidor que escucha conexiones
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((LISTEN_HOST, LISTEN_PORT))
        server_socket.listen()
        logging.info(f"[{NODE_NAME}] Escuchando en {LISTEN_HOST}:{LISTEN_PORT}...")
        
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_connection, args=(conn, addr)).start()


# Cliente que envía mensajes
def start_client():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                logging.info(f"[{NODE_NAME}] Intentando conectar con {PEER_HOST}:{PEER_PORT}...")
                client_socket.connect((PEER_HOST, PEER_PORT))

                # Crear mensaje en formato JSON
                message = {"node": NODE_NAME, "message": "Hola desde " + NODE_NAME}
                send_json(client_socket, message)

                # Recibir respuesta
                response = receive_json(client_socket)
                logging.info(f"[{NODE_NAME}] Respuesta recibida: {response}")

                time.sleep(MESSAGE_INTERVAL)
        except:
            logging.error(f"[{NODE_NAME}] Error de conexión. Reintentando en {RETRY_INTERVAL} segundos...")
            time.sleep(RETRY_INTERVAL)


if __name__ == "__main__":
    threading.Thread(target=start_server).start()
    time.sleep(SECONDS_TO_AWAIT_SERVER_START)
    start_client()
