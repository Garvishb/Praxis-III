import serial


def send_serial(grid_cell, serial_connection):
    """Transform grid coordinate to bottom left origin (6-y) and then change it to 36bit binary: 
    000000 000000 000000 000000 000000 000000 where it goes 
    (1,1), (2,1), (3,1)....(6, 1), (1, 2), (2, 2)....(6, 6)"""
    
    binary_string = "0" * 36
    for i in range(len(grid_cell)):
        grid_cell[i][1] = 7 - grid_cell[i][1]
    
        binary_string = coordinate_to_binary(grid_cell[i], binary_string)
    
    for i in range(0, len(binary_string), 6):
        print(binary_string[i:i+6])
    # print(binary_string)
    packet = bytearray()
    for i in range(0, len(binary_string), 6):
        byte = binary_string[i:i+6]
        packet.append(int(byte, 2))
        print(packet)
    
    print("Packet: ", packet)
    serial_connection.write(bytes('<', 'utf-8')) 
    serial_connection.write(packet)
    serial_connection.write(bytes('>', 'utf-8'))
    print("Data sent")
    serial_connection.close()
    
def coordinate_to_binary(grid_cell, binary_string):
    """Convert the grid cell to 36bit binary"""
    # print(binary_string[:(grid_cell[0] + (grid_cell[1]-1)*6 - 1)])
    # print(binary_string[grid_cell[0] + (grid_cell[1]-1)*6:])
    binary_string = binary_string[:(grid_cell[0] + (grid_cell[1]-1)*6 - 1)] + "1" + binary_string[grid_cell[0] + (grid_cell[1]-1)*6:]
    return binary_string

# coordinate_to_binary([3,2], "0"*36)
grid_cell = [[1,1]]
port = "COM20"
baudrate = 9600
serial_connection = serial.Serial(port, baudrate)
send_serial(grid_cell, serial_connection)
# send_serial(grid_cell, 1)