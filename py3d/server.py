
import socket
import threading
import pickle

# Server settings
HOST = '127.0.0.1'
PORT = 5555

# Player data structure: {address: {'pos': [x, y], 'angle': view_angle}}
players = {}

def handle_client(conn, addr):
    """Handles each connected client."""
    print(f"New connection: {addr}")
    # Initialize the player data
    players[addr] = {'pos': [400, 300], 'angle': 0}  # Initial player position and angle

    try:
        while True:
            # Receive player data from the client
            data = conn.recv(1024)
            if not data:
                break

            # Update player data
            player_data = pickle.loads(data)
            players[addr]['pos'] = player_data['pos']
            players[addr]['angle'] = player_data['angle']

            # Send the updated state back to all players
            game_state = pickle.dumps(players)
            conn.sendall(game_state)
    except:
        pass
    finally:
        print(f"Connection closed: {addr}")
        del players[addr]  # Remove player from the game when they disconnect
        conn.close()

def start_server():
    """Starts the server and listens for incoming connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == '__main__':
    start_server()
