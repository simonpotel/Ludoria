from src.network.server.game_server import GameServer

if __name__ == "__main__":
    print("Starting Ludoria Server...")
    server = GameServer()
    server.start() 