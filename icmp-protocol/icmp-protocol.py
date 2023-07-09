// Python code snippet that demonstrates how to send an ICMP Echo Request (Ping) using the ping utility and the socket module:
/////////////////////////////////
import os
import socket
import struct
import select
import time

ICMP_ECHO_REQUEST = 8  # ICMP Echo Request type

def checksum(data):
    # Calculate the checksum of a packet
    sum = 0
    countTo = (len(data) // 2) * 2

    count = 0
    while count < countTo:
        thisVal = data[count + 1] * 256 + data[count]
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2

    if countTo < len(data):
        sum = sum + data[len(data) - 1]
        sum = sum & 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    checksum = ~sum & 0xffff

    return checksum

def send_ping(destination_ip, timeout=1):
    # Create a raw socket
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    # Create ICMP Echo Request packet
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, 0, 1)
    data = b'Hello, ICMP!'
    packet = header + data

    # Calculate checksum and update packet
    checksum_value = checksum(packet)
    packet = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, checksum_value, 0, 1) + data

    # Send packet to the destination IP address
    icmp_socket.sendto(packet, (destination_ip, 1))

    # Record the time when the packet was sent
    sent_time = time.time()

    # Wait for the ICMP Echo Reply
    ready = select.select([icmp_socket], [], [], timeout)
    if ready[0]:
        # Receive the reply
        reply_packet, address = icmp_socket.recvfrom(1024)
        received_time = time.time()

        # Extract the ICMP header from the reply packet
        icmp_header = reply_packet[20:28]
        type, code, checksum, packet_id, sequence = struct.unpack('!BBHHH', icmp_header)

        # Calculate the round-trip time (RTT)
        rtt = (received_time - sent_time) * 1000

        print(f'ICMP Echo Reply received from {address[0]}: type={type}, code={code}, RTT={rtt:.2f}ms')
    else:
        print(f'No reply received from {destination_ip} within {timeout} seconds')

    # Close the socket
    icmp_socket.close()

# Example usage
destination_ip = '127.0.0.1'  # Replace with the desired destination IP address
send_ping(destination_ip)
