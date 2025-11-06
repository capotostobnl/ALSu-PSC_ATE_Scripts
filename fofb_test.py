""" Fast Orbit Feedback UDP Packet Test Scripts
M. Capotosto 11/6/2025"""

import subprocess

ip_address_list = ["10.0.142.100"]  # Set IP Addresses of all DUTs
mac_address_list = ["00:11:22:33:44:55"]  # Set MAC Addresses of all DUTs

NET_INTERFACE = "enp115s0"  # Set the network NET_INTERFACE to be used for the
#                       # FOFB Loopback

UDP_PORT = "12345"  # UDP Port number

PACKET_COUNT = "1"  # Set the expected number of packets to be recieved during
#                # the test.


def arp_static_init(ip_address_list, mac_address_list):
    for ip_address, mac_address in zip(ip_address_list, mac_address_list):
        cmd = ["sudo", "arp", "-s", ip_address, mac_address]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"ARP static entry added successfully for {ip_address}")

        except subprocess.CalledProcessError as e:
            print(f"Error adding ARP entry. Command failed with return code "
                  f"{e.returncode}")
            print(f"Error output: {e.stderr}")


def arp_static_destroy(ip_address_list):
    """
    Deletes static ARP entries added during the test using 'arp -d'.
    """
    print("\n--- Cleaning up Static ARP Entries ---")
    for ip_address in ip_address_list:
        cmd = ["sudo", "arp", "-d", ip_address]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Removed static entry for {ip_address}")
            else:
                print(f"Warning: Failed to delete ARP entry for {ip_address}."
                      f"Status: {result.stderr.strip()}")
        except FileNotFoundError:
            print("Error: 'arp' command not found during cleanup.")
            return


def capture_udp_packets(NET_INTERFACE, UDP_PORT, PACKET_COUNT):
    # The tcpdump command
    cmd = cmd = ["sudo", "tcpdump", "-i", NET_INTERFACE, "udp", "port",
                 UDP_PORT, "-c", PACKET_COUNT, "-n", "-v"]
#               # -C 5 kill after 5 packets received...

    try:
        result = subprocess.run(
            cmd, check=True,  # Raise Error for non-zero exit codes
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"\n\n***********************TCP Dump: \n {result.stdout}")

        print(f"\nPacket capture finished successfully. Output:\n"
              f"{result.stderr}")

        # Set the success flag
        test_passed = True

    except subprocess.CalledProcessError as e:
        # This catches if tcpdump failed to run or exited with an error code
        print(f"\nError running tcpdump (Exit Code {e.returncode}):")
        print(f"Error output: {e.stderr}")

    except FileNotFoundError:
        print("\nError: tcpdump command not found. Ensure it is installed and"
              " in the system PATH.")

    print(f"\nTest Result: {'PASS' if test_passed else 'FAIL'}")
    return test_passed


if __name__ == "__main__":
    arp_static_init(ip_address_list, mac_address_list)
    capture_udp_packets(NET_INTERFACE, UDP_PORT, PACKET_COUNT)
    arp_static_destroy(ip_address_list)
