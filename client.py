import socket
import threading
import os
from tkinter import filedialog
import tqdm
import ssl
import time

U_BUFFER_SIZE = 4096
D_BUFFER_SIZE = 4096

SERVER_HOST = '127.0.0.1'
CONTROL_PORT = 5001
DOWLOAD_PORT = 5002
UPLOAD_PORT = 5003



tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((SERVER_HOST, CONTROL_PORT))

print(f"[*] Connected to {SERVER_HOST}:{CONTROL_PORT}")

username = input("Enter username: ")
password = input("Enter password: ")
tcp_sock.sendall(f"AUTH {username} {password}".encode())
response = tcp_sock.recv(D_BUFFER_SIZE).decode()
if response != "Authentication successful.":
    print("Authentication failed. Exiting.")
    tcp_sock.close()
    exit()

while True:
    print("Commands:\n1. LIST - List files on the server\n2. UPLOAD - UPLOAD a file from the server\n3. DOWNLOAD <filename> - DOWNLOAD a file from the server\n4. EXIT - Exit the client")

    command = input("Enter command: ").strip().upper()
    if command == "LIST":
        tcp_sock.send(command.encode())
        files = tcp_sock.recv(D_BUFFER_SIZE).decode()
        print("\nFiles on server:\n")
        for f in files.split("\n"):
            print(f"  - {f}")
        print()  # extra blank line
        
        
        
        
    elif command.startswith("UPLOAD"):
        FILE_PATH = filedialog.askopenfilename(title="Select File to Upload")
        
        if not FILE_PATH:
            print("No file selected. Exiting.")
            tcp_sock.close()
            exit()
            
        tcp_sock.sendall(f"UPLOAD {os.path.basename(FILE_PATH)}".encode())
        upload_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for attempt in range(5):
            try:
                upload_sock.connect((SERVER_HOST, UPLOAD_PORT))
                break
            except(OSError) as e:
                print(f"Connection attempt {attempt+1} failed: {e}")
                time.sleep(0.5)
        else:
            print("Failed to connect to upload port after 3 attempts. Exiting.")
            continue
        
        try:
            filesize = os.path.getsize(FILE_PATH)
            upload_sock.sendall(f"{filesize}\n".encode())
            bytes_sent = 0
            
            with open(FILE_PATH, "rb") as f:
                while True: 
                    chunk = f.read(U_BUFFER_SIZE)
                    if not chunk:
                        break
                    upload_sock.sendall(chunk)
                    bytes_sent += len(chunk)
                    
            upload_sock.shutdown(socket.SHUT_RDWR)
            print(f"File '{os.path.basename(FILE_PATH)}' uploaded successfully ({bytes_sent}/{filesize} bytes sent).")
        
        except Exception as e:
            print(f"Error during file upload: {e}")
        finally:
            upload_sock.close()
            

    
        
    elif command.startswith("DOWNLOAD"):
        DOWNLOAD_FOLDER = filedialog.askdirectory(title="Select Folder to Save FILE")
        
        if not DOWNLOAD_FOLDER:
            print("No folder selected. Exiting.")
            tcp_sock.close()
            exit()
            
        tcp_sock.send(command.encode())
        download_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for attempt in range(3):
            try:
                time.sleep(0.5)  # brief pause to allow server to be ready
                download_sock.connect((SERVER_HOST, DOWLOAD_PORT))
                break
            except(OSError) as e:
                print(f"Download connection attempt {attempt+1} failed: {e}")
                time.sleep(0.5)
        else:
            print("Failed to connect to download port after 3 attempts. Exiting.")
            continue
            
        parts = command.split()
        if len(parts) != 2:
            print("Invalid DOWNLOAD command format.")
            download_sock.close()
            continue
        _, filename = parts
        save_path = os.path.join(DOWNLOAD_FOLDER, filename)
        
        with open(save_path, "wb") as f:
            while True:
                data = download_sock.recv(D_BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
                
        download_sock.close()
        print(f"File '{filename}' downloaded successfully to '{DOWNLOAD_FOLDER}'.")
        
        
        
        
    elif command == "EXIT":
        print("Exiting client.")
        tcp_sock.close()
        exit()
        
        
        
        

        

        


