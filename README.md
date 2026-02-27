# SocketVault
SocketBox is a Python client-server application that allows file transfers.
The server can handle multiple clients, supports uploading and downloading files, and includes 
username/password authentication. Future enhancements may include file tagging and filtering using a database.

# Features
- Username and password authentication
- Upload and download files
- List files on the server
- Modular design for easy expansion (e.g., tagging files)

# Requirements
- Python 3.10+ (tested on 3.14)
- Tkinter (for file selection dialogs)

Run pip install -r requirements.txt

# Setup
### Server
1. Place `server.py` and the `server_files/` folder on the server machine.
2. Run the server:
    python server.py

### Client
1. Place `client.py` on the client machine.
2. Update SERVER_HOST in client.py to the server`s IP address.
3. Run the client:
    python client.py

# USAGE

Enter the username and password when promoted.
(Default is User1, 12345 and admin, admin123)

List of commands will appear. 
- LIST: Show all files on the server
- UPLOAD <filename>: Upload a file to the server
- DOWNLOAD <filename>: Download a file from the server
- EXIT: Close the client connection


# Notes/Future Improvements
- Consider using a database for file tagging and filtering.






