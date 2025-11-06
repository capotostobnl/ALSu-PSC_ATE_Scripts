import socket
import struct
import time

def ieee754_float_to_bytes(value):
    """Convert a float to 4 bytes using IEEE 754 format."""
    return struct.pack('>f', value)  # Big-endian IEEE 754 float

def create_packet(setpoints):
    """
    setpoints: list of tuples like [(fast_address, setpoint_value), ...]
    Returns a bytes object for the complete UDP packet.
    """

    # Constants
    FAST_PROTOCOL_ID = 0x7631  # 2 bytes
    COMMAND = 0x0001           # 2 bytes, e.g., enable readback or 0x0000 if unused
    NONCE = int(time.time_ns()) & 0xFFFFFFFFFFFFFFFF  # 8 bytes (timestamp or counter)

    packet = b''

    # Header
    packet += struct.pack('>H', FAST_PROTOCOL_ID)
    packet += struct.pack('>H', COMMAND)
    packet += struct.pack('>Q', NONCE)

    # Add each setpoint (address + value) to the packet
    for fast_addr, value in setpoints:
        packet += struct.pack('>H', fast_addr)         # 2-byte Fast Address
        packet += ieee754_float_to_bytes(value)        # 4-byte IEEE 754 float

    return packet

def send_udp_packet(ip, port, packet):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packet, (ip, port))
    sock.close()

# --- Example usage ---
if __name__ == "__main__":
    # Example: Fast address 1 with setpoint 12.5V, Fast address 2 with 5.0V
    setpoints = [
        (1, 12.5),
        (2, 5.0)
    ]

    packet = create_packet(setpoints)
    print("Sending packet:", packet.hex())

    # Replace with your target IP/port
    send_udp_packet("192.168.1.100", 1234, packet)
