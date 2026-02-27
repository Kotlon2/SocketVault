import socket
import tqdm
from tkinter import filedialog
import os
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")
context.load_verify_locations("client.crt")
context.check_hostname = False
context.verify_mode = ssl.CERT_REQUIRED

SERVER_HOST = '0.0.0.0'

CONTROL_PORT = 5001
DOWLOAD_PORT = 5002
UPLOAD_PORT = 5003

BUFFER_SIZE = 4096



tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.bind((SERVER_HOST, CONTROL_PORT))
tcp_sock.listen(5)

USERS = {
    "User1": "12345",
    "admin": "admin123"
}



def handle_upload(filename):
        upload_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        upload_sock.bind((SERVER_HOST, UPLOAD_PORT))
        upload_sock.listen(1)
            
        print(f"[*] Waiting for file upload on port {UPLOAD_PORT}...")
            
        conn, addr = upload_sock.accept()
        ssl_upload = context.wrap_socket(conn, server_side=True)
        print(f"[+] Connection from {addr} for file upload.")
            
        with open(os.path.join("server_files", filename), "wb") as f:
            while True:
                bytes_read = ssl_upload.recv(BUFFER_SIZE)
    
                if not bytes_read:
                     break
                f.write(bytes_read)
            
        print(f"File '{filename}' uploaded successfully.")
        ssl_upload.close()
        upload_sock.close()
            
def handle_download(filename):
        download_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        download_sock.bind((SERVER_HOST, DOWLOAD_PORT))
        download_sock.listen(1)
            
        print(f"[*] Waiting for file download on port {DOWLOAD_PORT}...")
            
        conn, addr = download_sock.accept()
        ssl_download = context.wrap_socket(conn, server_side=True)
        
        print(f"[+] Connection from {addr} for file download.")
            
        with open(os.path.join("server_files", filename), "rb") as f:
            while chunk := f.read(BUFFER_SIZE):
                    ssl_download.sendall(chunk)
            
        print(f"File '{filename}' downloaded successfully.")
        ssl_download.close()
        download_sock.close()
        
try:
    while True:
        print(f"[*] Listening as {SERVER_HOST}:{CONTROL_PORT}")

        client_socket, address = tcp_sock.accept()
        sskt = context.wrap_socket(client_socket, server_side=True)
        
        print(f"[+] {address} is connected.")
        
        auth_data = sskt.recv(BUFFER_SIZE).decode().strip()
        try:
            _, username, password = auth_data.split()
            
        except ValueError:
            sskt.send("Invalid authentication format.".encode())
            print(f"[-] {address} sent invalid authentication data.")
            sskt.close()
            continue
        if USERS.get(username) != password:
            sskt.send("Invalid credentials.".encode())
            print(f"[-] {address} failed to authenticate.")
            sskt.close()
            continue
        else:
            sskt.send("Authentication successful.".encode())
            print(f"[+] {address} authenticated successfully.")
        
        while True:
    
            command = sskt.recv(BUFFER_SIZE).decode()
            if not command:
                print(f"[-] {address} disconnected.")
                break
            
            if command.upper() == "EXIT":
                print(f"[-] {address} requested to exit.")
                sskt.close()
                break
            

            print(f"Received command: {command}")
                
            if command.startswith("LIST"):
                files = os.listdir("server_files")
                files_list = "\n".join(files)
                sskt.sendall(files_list.encode())
                    
            elif command.startswith("UPLOAD"):
                filename = command.split()[1]
                handle_upload(filename)
                    
            elif command.startswith("DOWNLOAD"):
                filename = command.split()[1]
                handle_download(filename)

except KeyboardInterrupt:
    print("\nServer shutting down.")
finally:
    tcp_sock.close()
    print("Server socket closed.")

                
