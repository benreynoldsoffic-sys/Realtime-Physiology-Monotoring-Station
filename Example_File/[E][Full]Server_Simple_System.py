import socket
import csv
import time

def send_csv_data(filename, client_socket):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            message = ','.join(row) + '\n'
            client_socket.sendall(message.encode('utf-8'))
            time.sleep(0.0005)  # Set 2000hz sample rate

def start_server(host, port, filename):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        try:
            send_csv_data(filename, client_socket)
        except:
            print("An Error Occured")
            server_socket.close()
            client_socket.close()
        finally:
            server_socket.close()
            client_socket.close()

if __name__ == '__main__':
    host = 'localhost'
    port = 12345
    filename = "C:\\Users\\brhei\\Desktop\\PythonWork\\Realtime_Work\\Threaf&feature\\liveData.csv"  # Replace with your CSV file name
    start_server(host, port, filename)
