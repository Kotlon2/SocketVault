import datetime
import socket
from tkinter import filedialog
import os
import threading


SERVER_HOST = '0.0.0.0'

CONTROL_PORT = 5001
DOWLOAD_PORT = 5002
UPLOAD_PORT = 5003

U_BUFFER_SIZE = 4096
D_BUFFER_SIZE = 4096

tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.bind((SERVER_HOST, CONTROL_PORT))
tcp_sock.listen(5)

upload_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
upload_sock.bind((SERVER_HOST, UPLOAD_PORT))
upload_sock.listen(5)

download_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
download_sock.bind((SERVER_HOST, DOWLOAD_PORT))
download_sock.listen(5)

USERS = {
    "User1": "12345",
    "admin": "admin123"
}



def handle_upload(filename):
            
        print(f"[*] Waiting for file upload on port {UPLOAD_PORT}...")
            
        conn, addr = upload_sock.accept()
        try:
            print(f"[+] Connection from {addr} for file upload.")
            
            size_data = b""
            while not size_data.endswith(b"\n"):
                chunk = conn.recv(1)
                if not chunk:
                    raise ValueError("Failed to receive file size.")
                size_data += chunk
            
            filesize = int(size_data.decode().strip())
            bytes_received = 0
            
            os.makedirs("server_files", exist_ok=True)
            file_path = os.path.join("server_files", filename)
            
            with open(file_path, "wb") as f:
                while bytes_received < filesize:
                    bytes_read = conn.recv(U_BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    bytes_received += len(bytes_read)
                    
            if bytes_received == filesize:
                print(f"File '{filename}' uploaded successfully ({bytes_received}/{filesize} bytes received).")
            else:
                print(f"File '{filename}' upload failed. Expected {filesize} bytes, received {bytes_received} bytes.")
                os.remove(file_path)  # remove incomplete file
                
        except Exception as e:
            print(f"Error during file upload: {e}")
        finally:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            conn.close()
 
                
    
def handle_download(filename):
        print(f"[*] Waiting for file download on port {DOWLOAD_PORT}...")
        conn, addr = download_sock.accept()
        try:
            print(f"[+] Connection from {addr} for file download.")
                
            with open(os.path.join("server_files", filename), "rb") as f:
                while chunk := f.read(D_BUFFER_SIZE):
                        conn.sendall(chunk)
                
            print(f"File '{filename}' downloaded successfully.")
        except Exception as e:
            print(f"Error during file download: {e}")
        finally:
            try: 
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            conn.close()
            
def handle_client(client_socket, address):
        
        auth_data = client_socket.recv(D_BUFFER_SIZE).decode().strip()
        try:
            _, username, password = auth_data.split()
            
        except ValueError:
            client_socket.send("Invalid authentication format.".encode())
            print(f"[-] {address} sent invalid authentication data.")
            client_socket.close()
            return
        if USERS.get(username) != password:
            client_socket.send("Invalid credentials.".encode())
            print(f"[-] {address} failed to authenticate.")
            client_socket.close()
            return
        else:
            client_socket.send("Authentication successful.".encode())
            print(f"[+] {address} authenticated successfully.")
        
        while True:
            try:
                command = client_socket.recv(D_BUFFER_SIZE).decode().strip() 
                if not command:
                    print(f"[-] {address} disconnected.")
                    break
            except ConnectionResetError:
                 print(f"[-] {address} connection reset.")
                 break
            except Exception as e:
                 print(f"[-] Error receiving command from {address}: {e}")  
                 break
            
            if command.upper() == "EXIT":
                print(f"[-] {address} requested to exit.")
                client_socket.close()
                break
            

            print(f"Received command: {command}")
                
            if command.startswith("LIST"):
                os.makedirs("server_files", exist_ok=True)
                files = os.listdir("server_files")
                files_list = "\n".join(files)
                client_socket.sendall(files_list.encode())
                    
            elif command.startswith("UPLOAD"):
                try:
                    _, filename = command.split(maxsplit=1)
                except ValueError:
                    client_socket.send("Invalid UPLOAD command format.".encode())
                    print(f"[-] Invalid UPLOAD command format from {address}.") 
                    continue
                filename = os.path.basename(filename)
                handle_upload(filename)
                                   
            elif command.startswith("DOWNLOAD"):
                try:
                    _, filename = command.split(maxsplit=1)
                except ValueError:
                    client_socket.send("Invalid DOWNLOAD command format.".encode())
                    print(f"[-] Invalid DOWNLOAD command format from {address}.") 
                    continue
                filename = os.path.basename(filename)
                handle_download(filename)


try:
    while True:
        print(f"[*] Waiting for incoming connections as {SERVER_HOST} on port {CONTROL_PORT}...")
        client_sock, addr = tcp_sock.accept()
        print(f"[{datetime.datetime.now()}] Connection accepted from {addr}.")
        
        client_thread = threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True)
        client_thread.start()

except KeyboardInterrupt:
    print("\nServer shutting down.")
finally:
    tcp_sock.close()
    print("Server socket closed.")

                
