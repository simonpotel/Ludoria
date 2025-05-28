import json
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, Dict, List

class PacketType(Enum):
    # CtS (Client to Server)
    CONNECT = 0x1
    GAME_ACTION = 0x5
    DISCONNECT = 0x8
    CHAT_SEND = 0x9
    GET_GAME_LIST = 0xB 
    # StC (Server to Client)
    PLAYER_ASSIGNMENT = 0x2
    YOUR_TURN = 0x3
    WAIT_TURN = 0x4
    GAME_STATE = 0x6
    PLAYER_DISCONNECTED = 0x7
    CHAT_RECEIVE = 0xA
    GAME_LIST = 0xC  


def create_connect_dict(player_name: str, game_name: str, game_type: str) -> Dict[str, Any]:
    return {
        "type": PacketType.CONNECT.value,
        "data": {
            "player_name": player_name,
            "game_name": game_name,
            "game_type": game_type
        }
    }

def create_game_action_dict(action: Dict[str, Any], game_id: Optional[str] = None) -> Dict[str, Any]:
    data = action.copy()
    if game_id:
        data["game_id"] = game_id
    return {
        "type": PacketType.GAME_ACTION.value,
        "data": data
    }

def create_player_assignment_dict(player_number: int, game_id: str, game_type: str) -> Dict[str, Any]:
    return {
        "type": PacketType.PLAYER_ASSIGNMENT.value,
        "data": {
            "player_number": player_number,
            "game_id": game_id,
            "game_type": game_type
        }
    }

def create_wait_turn_dict(game_id: str) -> Dict[str, Any]:
    return {
        "type": PacketType.WAIT_TURN.value,
        "data": {"game_id": game_id}
    }

def create_your_turn_dict(game_id: str) -> Dict[str, Any]:
    return {
        "type": PacketType.YOUR_TURN.value,
        "data": {"game_id": game_id}
    }

def create_disconnect_dict(message: str, game_id: Optional[str] = None) -> Dict[str, Any]:
    data = {"message": message}
    if game_id:
        data["game_id"] = game_id
    return {
        "type": PacketType.DISCONNECT.value,
        "data": data
    }

def create_player_disconnected_dict(message: str, game_id: str) -> Dict[str, Any]:
    return {
        "type": PacketType.PLAYER_DISCONNECTED.value,
        "data": {"message": message, "game_id": game_id}
    }

def create_game_state_dict(state: Dict[str, Any], game_id: str) -> Dict[str, Any]:
    return {
        "type": PacketType.GAME_STATE.value,
        "data": state
    }

def create_chat_send_dict(sender_name: str, message: str, player_number: int, game_id: str) -> Dict[str, Any]:
    return {
        "type": PacketType.CHAT_SEND.value,
        "data": {
            "sender_name": sender_name,
            "message": message,
            "player_number": player_number,
            "game_id": game_id
        }
    }

def create_chat_receive_dict(sender_name: str, message: str, player_number: int, game_id: str) -> Dict[str, Any]:
    return {
        "type": PacketType.CHAT_RECEIVE.value,
        "data": {
            "sender_name": sender_name,
            "message": message,
            "player_number": player_number,
            "game_id": game_id
        }
    }

def create_get_game_list_dict() -> Dict[str, Any]:
    return {
        "type": PacketType.GET_GAME_LIST.value,
        "data": {}
    }

def create_game_list_dict(games: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "type": PacketType.GAME_LIST.value,
        "data": {"games": games}
    }