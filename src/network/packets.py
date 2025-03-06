import struct
from enum import Enum
import json
from dataclasses import dataclass
from typing import Optional, Any, Dict, Tuple

class PacketType(Enum):
    CONNECT = 0x01
    DISCONNECT = 0x02
    GAME_ACTION = 0x03
    PLAYER_ASSIGNMENT = 0x04
    GAME_STATE = 0x05
    WAIT_TURN = 0x06
    YOUR_TURN = 0x07

@dataclass
class Packet:
    type: PacketType
    data: Dict[str, Any]
    game_id: Optional[str] = None

    HEADER_FORMAT = "!BH"  # 1 byte for type, 2 bytes for size
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def to_bytes(self) -> bytes:
        payload = json.dumps({
            "data": self.data,
            "game_id": self.game_id
        }).encode('utf-8')
        header = struct.pack(self.HEADER_FORMAT, self.type.value, len(payload))
        return header + payload

    @staticmethod
    def from_bytes(data: bytes) -> Tuple['Packet', int]:
        if len(data) < Packet.HEADER_SIZE:
            raise ValueError("Incomplete packet header")
        
        packet_type, payload_size = struct.unpack(Packet.HEADER_FORMAT, data[:Packet.HEADER_SIZE])
        
        if len(data) < Packet.HEADER_SIZE + payload_size:
            raise ValueError("Incomplete packet payload")
            
        payload = data[Packet.HEADER_SIZE:Packet.HEADER_SIZE + payload_size]
        payload_data = json.loads(payload.decode('utf-8'))
        
        return (Packet(
            type=PacketType(packet_type),
            data=payload_data["data"],
            game_id=payload_data.get("game_id")
        ), Packet.HEADER_SIZE + payload_size)

def create_connect_packet(player_name: str, game_name: str) -> Packet:
    return Packet(PacketType.CONNECT, {"player_name": player_name, "game_name": game_name}, game_name)

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

def create_disconnect_packet(message: str, game_id: Optional[str] = None) -> Packet:
    return Packet(PacketType.DISCONNECT, {"message": message}, game_id) 