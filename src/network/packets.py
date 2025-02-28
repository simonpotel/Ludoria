from enum import Enum
import json
from dataclasses import dataclass
from typing import Optional, Any, Dict

class PacketType(Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    GAME_ACTION = "game_action"
    PLAYER_ASSIGNMENT = "player_assignment"
    GAME_STATE = "game_state"
    WAIT_TURN = "wait_turn"
    YOUR_TURN = "your_turn"

@dataclass
class Packet:
    type: PacketType
    data: Dict[str, Any]
    game_id: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            "data": self.data,
            "game_id": self.game_id
        })

    @staticmethod
    def from_json(json_str: str) -> 'Packet':
        data = json.loads(json_str)
        return Packet(
            type=PacketType(data["type"]),
            data=data["data"],
            game_id=data.get("game_id")
        )

def create_connect_packet(player_name: str) -> Packet:
    return Packet(PacketType.CONNECT, {"player_name": player_name})

def create_disconnect_packet() -> Packet:
    return Packet(PacketType.DISCONNECT, {})

def create_game_action_packet(action: Dict[str, Any], game_id: str) -> Packet:
    return Packet(PacketType.GAME_ACTION, action, game_id)

def create_player_assignment_packet(player_number: int, game_id: str) -> Packet:
    return Packet(PacketType.PLAYER_ASSIGNMENT, {"player_number": player_number}, game_id)

def create_game_state_packet(state: Dict[str, Any], game_id: str) -> Packet:
    return Packet(PacketType.GAME_STATE, state, game_id)

def create_wait_turn_packet(game_id: str) -> Packet:
    return Packet(PacketType.WAIT_TURN, {}, game_id)

def create_your_turn_packet(game_id: str) -> Packet:
    return Packet(PacketType.YOUR_TURN, {}, game_id) 