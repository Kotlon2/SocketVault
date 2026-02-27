import socket
import threading
import os
from tkinter import filedialog
import tqdm
import ssl

BUFFER_SIZE = 4096

SERVER_HOST = '127.0.0.1'
CONTROL_PORT = 5001
DOWLOAD_PORT = 5002
UPLOAD_PORT = 5003

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_verify_locations('server.crt')
context.load_cert_chain(certfile="client.crt", keyfile="client.key")
context.check_hostname = False  
context.verify_mode = ssl.CERT_REQUIRED

tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_sock = context.wrap_socket(tcp_sock, server_hostname=SERVER_HOST)
ssl_sock.connect((SERVER_HOST, CONTROL_PORT))

print(f"[*] Connected to {SERVER_HOST}:{CONTROL_PORT}")

username = input("Enter username: ")
password = input("Enter password: ")
ssl_sock.sendall(f"AUTH {username} {password}".encode())
response = ssl_sock.recv(BUFFER_SIZE).decode()
if response != "Authentication successful.":
    print("Authentication failed. Exiting.")
    ssl_sock.close()
    tcp_sock.close()
    exit()

while True:
    print("Commands:\n1. LIST - List files on the server\n2. UPLOAD <filename> - UPLOAD a file from the server\n3. DOWNLOAD <filename> - DOWNLOAD a file from the server\n4. EXIT - Exit the client")

    command = input("Enter command: ").strip().upper()
    if command == "LIST":
        ssl_sock.send(command.encode())
        files = ssl_sock.recv(BUFFER_SIZE).decode()
        print("\nFiles on server:\n")
        for f in files.split("\n"):
            print(f"  - {f}")
        print()  # extra blank line
        
    elif command.startswith("UPLOAD"):
        FILE_PATH = filedialog.askopenfilename(title="Select File to Upload")
        
        if not FILE_PATH:
            print("No file selected. Exiting.")
            tcp_sock.close()
            ssl_sock.close()
            exit()
            
        ssl_sock.sendall(f"UPLOAD {os.path.basename(FILE_PATH)}".encode())
        
        upload_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_upload_sock = context.wrap_socket(upload_sock, server_hostname=SERVER_HOST)
        ssl_upload_sock.connect((SERVER_HOST, UPLOAD_PORT))
            
        with open(FILE_PATH, "rb") as f:
            while chunk := f.read(BUFFER_SIZE):
                upload_sock.sendall(chunk)
                
        upload_sock.close()
        ssl_upload_sock.close()
        print(f"File '{os.path.basename(FILE_PATH)}' uploaded successfully.")
        
        
    elif command.startswith("DOWNLOAD"):
        DOWNLOAD_FOLDER = filedialog.askdirectory(title="Select Folder to Save FILE")
        
        if not DOWNLOAD_FOLDER:
            print("No folder selected. Exiting.")
            ssl_sock.close()
            exit()
            
        ssl_sock.send(command.encode())
        
        download_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_download_sock = context.wrap_socket(download_sock, server_hostname=SERVER_HOST)
        ssl_download_sock.connect((SERVER_HOST, DOWLOAD_PORT))
        
        _, filename = command.split()
        save_path = os.path.join(DOWNLOAD_FOLDER, filename)
        
        with open(save_path, "wb") as f:
            while True:
                data = ssl_download_sock.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
                
        download_sock.close()
        ssl_download_sock.close()
        print(f"File '{filename}' downloaded successfully to '{DOWNLOAD_FOLDER}'.")
        
    elif command == "EXIT":
        print("Exiting client.")
        ssl_sock.close()
        tcp_sock.close()
        exit()
        
        
        
        

        

        


