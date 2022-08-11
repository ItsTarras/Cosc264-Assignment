#Assignment
import sys
import socket
import struct
import time
def packet_to_dates(packet):
    """This turns a bytearray packet into the date, time, etc variables."""
    bin_MagicNo, bin_MagicNo2 = bin(packet[0])[2:][::-1], bin(packet[1])[2:][::-1]
    PacketType = packet[3]
    Language = packet[5]
    bin_year, bin_year2 = bin(packet[6])[2:][::-1], bin(packet[7])[2:][::-1]
    month = packet[8]
    day = packet[9]
    hour = packet[10]
    minute = packet[11]
    length = packet[12]
    

    
    #Everything is sent in byte arrays of 8, so only the first 4 bytes need to be binary checked.
    lists = [bin_MagicNo, bin_MagicNo2, bin_year, bin_year2]
    for i in range(len(lists)):
        while len(lists[i]) < 8:
            lists[i] += '0'
        lists[i] = lists[i][::-1]
    
    #Convert the binary into decimals
    MagicNo = int((lists[0] + lists[1]), 2)
    year = int((lists[2] + lists[3]), 2)
    

    text = packet[13:].decode()
    
    
    
    return MagicNo, PacketType, Language, year, month, day, hour, minute, length, text
         

def main():
    
    #Reads the inputs and converts them into variables
    date_or_time = sys.argv[1]
    ip_address = sys.argv[2]
    port = sys.argv[3]
    
    #Checks if the date_or_time field actually asks for the date or time, otherwise exit system.
    if date_or_time not in ['date', 'time']:
        print('Request field invalid. Please specify "date" or "time"')
        sys.exit()
    
    #Prepare the packet variables:
    MagicNo = 0x497E
    PacketType = 0x0001
    
    if date_or_time == 'date':
        request_hex = 0x0001
    elif date_or_time == 'time':
        request_hex = 0x0002
    
    
    
    #Attempt to create a socket to the ip address. Also checks if it's a domain name, or a decimal notation.
    try:
        #try to turn the ip address into a packet. 
        socket.inet_aton(ip_address)
    except:
        try:
            #If a domain name, collect info from it if it exists.
            ip_info = socket.getaddrinfo(ip_address, port)
            ip_address = ip_info[0][4][0]
        except:
            print("Domain name invalid. Please try again.")
            sys.exit()
                
    #Checks the validity of the port type, and number.
    if port.isnumeric():
        port = int(port)
    else:
        print("Port must be numeric!")
        sys.exit()
    
    if port > 64000 or port < 1024:
        print("Port must be within range! Please set it between 1024 and 64000 (inclusive).")
        sys.exit()
    
    #The inputs are working, so open a udp socket and prepare a packet request.
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        print("Error in establishing ports! Request Terminated...")
        sys.exit()

    while True:
        #Assemble the request packet
        packet = struct.pack('>HHH', MagicNo, PacketType, request_hex)
        
        #Try to send the packet to the server.
        try:
            sock.sendto(packet, (ip_address, port))
        except:
            print("Error sending packet to server.")
            break
        
        #Socket options changed to only have a timeout of 1 second.
        sock.settimeout(1)
        
        #Now we need to have a timeout for a response from the server, otherwise it'll assume the server failed.
        print('\n', ' ' * 14, '[Sending Request...]', ' ' * 15)
        
        #Slowly sending the packet shows progress.
        time.sleep(0.5)
        print('\n')

        try:
            #Try to receive data from the port
            data, addr = sock.recvfrom(4096)
            
            #Now we need to decode the bytearray, and turn it into a number of variables.
            MagicNo, PacketType, Language, year, month, day, hour, minute, length, text = packet_to_dates(data)
            
            #Print in a neat, readable format.
            print(' ' * 15, "[Packet received!]", ' ' * 15)
            print('\n')
            print('-' * 14, f"[Packet Information]", '-' * 14)
            print(f'Magic Number: {MagicNo}')
            print(f'Packet Type: {PacketType}')
            print(f'Language Code: {Language}')
            print('-' * 50)
            print('-' * 16, '[Time Variables]', '-' * 16)
            print(f'Year: {year}')
            print(f'Month: {month}')
            print(f'Day: {day}')
            print(f'Hour: {hour}')
            print(f'Minute: {minute}')
            print('-' * 50)
            print('-' * 19, '[Message]', '-' * 20)
            print(f'Length: {length}')
            print(f'Text: {text}')
            print('-' * 50)
            print('\n')

            #Leaves the loop if there's a success.
            break
        
        except socket.timeout:
            print("Request timed out! Request Terminated...")
            sys.exit()
            
        
    #Once the packet has been received:
    sys.exit()
            
main()