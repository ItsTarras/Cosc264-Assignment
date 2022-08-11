import socket
import threading
import time
import datetime
import sys
import select
import struct
#-----------------------------------------------------------------------------------------------------------------
#Verify_Packet Section

def verify_request(request_packet):
    """Checks the packet for validity. If invalid, throw an error - otherwise, send the packet back."""
    #Starting variables
    index = 0
    iterable = []

    #Checking if the packet byte_array length is 6. If not, return an error.

    if len(request_packet) != 6:
        return "Incorrect length of packet! Please ensure it is EXACTLY 6 bytes in length."   
        
    #Updates the bytearray into binary, so we can check for bits, and add zeroes to the start if required.
    while index < len(request_packet) - 1:
        X = request_packet[index]
        Y = request_packet[index + 1]
        number1 = bin(X)[2:]
        number2 = bin(Y)[2:]
        number1 = number1[::-1]
        number2 = number2[::-1]
        while len(number1) < 8:
            number1 += '0'
        while len(number2) < 8:
            number2 += '0'
        number1 = number1[::-1]
        number2 = number2[::-1]
        index += 2
        iterable.append(int(number1 + number2, 2))
    
    #Create some variables for readability.
    MagicNo = iterable[0]
    PacketType = iterable[1]
    RequestType = iterable[2]
    
    #Checking if the inputs are valid:
    if MagicNo != 0x497E:
        return 'MagicNo field is not equal to 0x497E! (18814 in decimal.)'
    if PacketType != 0x0001:
        return 'Incorrect input for Packet Type! Please ensure it is set to 1 for a Client packet setting.'
    if RequestType != 0x0001 and RequestType != 0x0002:
        return 'Incorrect input for Request Type! Please ensure it is set to 1 or 2.'
    
    #If everything is valid:
    return [MagicNo, PacketType, RequestType]

# Verify_Packet section
#------------------------------------------------------------------------------------------------------------------
# Main section

def main():
    #System port variable allocations
    #port1 is english, port2 is maori and port3 is german
    port1 = sys.argv[1]
    port2 = sys.argv[2]
    port3 = sys.argv[3]
    localhost = "127.0.0.1"
        
    #--------------------------------------------------------------------------------
    #Checking if ports are all integers
    if (port1.isnumeric() and port2.isnumeric() and port3.isnumeric()) == False:
        print("All ports should be integers!")
        sys.exit()
    #If they're all numeric, change them to their int versions
    port1 = int(port1)
    port2 = int(port2)
    port3 = int(port3)
    
    #Checking if all ports are within the given range.
    if port1 < 1024 or port1 > 64000:
        print("Port 1 is out of range! Please ensure it is set between 1024 and 64000 (inclusive)")
        sys.exit()
    elif port2 < 1024 or port2 > 64000:
        print("Port 2 is out of range! Please ensure it is set between 1024 and 64000 (inclusive)")
        sys.exit()
    elif port3 < 1024 or port3 > 64000:
        print("Port 3 is out of range! Please ensure it is set between 1024 and 64000 (inclusive)")
        sys.exit()
    #Checking if all ports are unique
    if port1 == port2 or port2 == port3 or port1 == port3:
        print("All ports need to be unique values!")
        sys.exit()

    #Turns the ports into sockets, checking for an error by using a try block.
    try:
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except:
        print("Error with socket implementation! Terminating...")
        sys.exit()
    #Enables the SO_REUSEADDR option, allowing address/ports to be - 
    # reused immediately, rather than waiting for late packets.
    try:
        sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock3.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        print("Error with socket modification! Terminating...")
        sys.exit()
    #Binds the sockets, since it's a datagram socket
    try:
        sock1.bind(('', port1))
        sock2.bind(('', port2))
        sock3.bind(('', port3))
    except:
        print("Error with socket binding! Terminating...")
        sys.exit()
    
    #Debug confirmation message

    print('Successfully established sockets! \nStarting server...')
   
    continuing = True
    while continuing is True:   

        #Needs to use a select() call to wait for a request packet on any of the sockets.
        readable, writeable, exceptional = select.select([sock1, sock2, sock3], [], [])
        #Selecting the free socket.
        for sock in readable:
            data, addr = sock.recvfrom(4096)
            
            #Sources the port that was sent.
            sent_from_port = sock.getsockname()[1]
            
            #Prints debug messages to the terminal, including data, address and message
            
            print('-' * 50)
            print(f"Packet received from: {addr[0]}")
            print(f"Sent from: {sent_from_port}") 
            print(f"Packet contents: {data}")
            print('-' * 50)
            
            
            #Checks if the data is correct. If it is, parse it forward. If not, print the error
            output = verify_request(data)
            if isinstance(output, str) == False:
                
                #Prints the verification status
                print("\nPacket is verified to be in correct format!", '\n')
                
                #Variables created from the output
                MagicNo, PacketType, RequestType  = output[0], output[1], output[2]
                
                #Now we need to check the language port to send for a response
                if sent_from_port == port1:
                    language = 0x0001
                elif sent_from_port == port2:
                    language = 0x0002
                elif sent_from_port == port3:
                    language = 0x0003

                #Do they want to know the date or time?
                if RequestType == 0x0001:
                    wanted_type = 'Date'
                else:
                    wanted_type = 'Time'
                
                #Checks the current date and time
                current_time = datetime.datetime.now()
                year = current_time.year
                month = current_time.month
                day = current_time.day
                hour = current_time.hour
                minute = current_time.minute
                
                #Creating a list for the month names, since these are words, not numbers.
                months_eng = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
                months_mri = ['', 'Kohitatea', 'Hui-tanguru', 'Poutu-te-rangi', 'Paenga-whawha', 'Haratua', 'Pipiri', 'Hongongoi', 'Here-turi-koka', 'Mahuru', 'Whiringa-a-nuku', 'Whiringa-a-rangi', 'Hakihea']
                months_ger = ['', 'Januar', 'Februar', 'Marz', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    
                
                #Now we need to create a packet.
                    #We need to calculate the length in bytes. To do this, measure and encode the python string that has all options set.
                if language == 0x0001:
                    date_str = f"Today's date is {months_eng[month]} {day}, {year}"
                    time_str = f"The current time is {hour}:{minute}"
                elif language == 0x0002:
                    date_str = f"Ko te ra o tenei ra ko {months_mri[month]} {day}, {year}"
                    time_str = f"Ko te wa o tenei wa {hour}:{minute}"
                elif language == 0x0003:
                    date_str = f"Heute ist der {day}. {months_ger[month]} {year}"
                    time_str = f"Die Uhrzeit ist {hour}:{minute}"
                
                #Next, encode the string to perform byte checks
                if wanted_type == 'Date':
                    time_or_day = date_str.encode('utf-8')
                else:
                    time_or_day = time_str.encode('utf-8')
                
                #Here's the length of the byte version
                length = len(time_or_day)
                
                #If it follows the length threshold, assemble the packet.
                if length <= 255:
                    
                    packet_list = struct.pack('>HHHHBBBBB', MagicNo, PacketType, language, year, month, day, hour, minute, length)
                    length_pack = struct.pack("%ds" % length, time_or_day)
                    packet = (packet_list + length_pack)
                    print('Assembled Packet!')
                    
                    #------------------------------------------------#
                    # Next, send the completed packet to the client  #
                    #------------------------------------------------#
                    
                    try:
                        sock.sendto(packet, (addr[0], addr[1]))
                        print('Sent packet to: ', addr[0], '\n')
                        print('Awaiting connections...\n')
                    except:
                        print("Error in sending request to client")
                        continue
                    
                else:
                    print('Returned text is too long!')
                    continue
                
            else:
                print('Received packet is invalid!')
                continue
            
    sock1.close()
    sock2.close()
    sock3.close()
    print("Closing Sockets")
    sys.exit()
    
main()