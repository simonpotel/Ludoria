from src.network.server.game_server import GameServer

if __name__ == "__main__":
    print("Starting Smart Games Server...")
    server = GameServer()
    server.start() 