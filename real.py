import socket,sys,select

class client():
    def __init__(self, reqtype, pckttype, port,  ip):
        self.magic_num = 0x497e
        #self.host = 'localhost'
        self.IP_add = ip
        packet_type = 1
        request_type = reqtype
        self.lang_type = None
        self.port = port
        self.ports = [1024,1025,1026]
        self.send_packet(self.make_packet(packet_type, request_type)) 
        
        
        
    def send_packet(self, packet):
        print(self.IP_add, self.port)
        connection = socket.socket()
        connection.connect((self.IP_add, self.port))
        print("connected to %d %d", self.port,self.IP_add)
       # connection.send("BDSFDSF")
      #  connection.send(packet)
    
        received_data = self.receive(connection)
        if self.verify(received_data) == 1:
            print ("goood")
            self.print_representation(received_data)
            
        
        #print ("this one > ", douu, type(douu))
        
    def receive(self,connection):
        connection.setblocking(0)
        ready = select.select([connection],[],[],1)
        if ready[0]:
            data = connection.recv(4096)
            in_array = bytearray(data)
            connection.close()
            #sys.exit()
            return (in_array)
        
    def make_16_bit_binary(self, number):
        return (format(number, '016b'))
    def make_8_bit_binary(self, number):
        return (format(number, '08b'))    
    def concat_bits(self,as_list):
        # returns string of all bits joined up
        return (''.join(str(x) for x in as_list))    
    def two_bytes_to_integer(self,left,right):
        a = self.make_8_bit_binary(left)
        b = self.make_8_bit_binary(right)
        result = (self.concat_bits([a,b]))
        return (int(result,2))
    def one_byte_to_integer(self,byte):
        a = self.make_8_bit_binary(byte)
        return (int(a,2))
       
    def verify (self,data):
        """checks the contents of the packet"""
        self.lang_type = self.two_bytes_to_integer(data[4],data[5])
        if (len(data) <13):
            self.terminate("The packet is missing data")
            received_num = self.two_bytes_to_integer(data[0],data[1])
        elif (self.two_bytes_to_integer(data[2],data[3]) != 2):
            self.terminate("Received a non DT_response packet when waiting")
        elif not((self.lang_type > 0) and (self.lang_type < 4)):
            self.terminate("The language request is out of bounds")
        else:
            return 1
        return 0
        
        
        
    def print_representation(self, data,display_all = True):
        string = data[13:].decode('UTF-8')
        
        if display_all:
            headings = ['MagicNo: ', 'Packet Type: ', 'Language Code: ', 'Year: ', 'Month: ', 'Day: ', 'Hour: ', 'Minute: ', 'Length: ', 'Message: ']
            array = []
            array.append(hex(self.two_bytes_to_integer(data[0],data[1])))
            array.append(hex(self.two_bytes_to_integer(data[2],data[3])))
            array.append(hex(self.two_bytes_to_integer(data[4],data[5])))
            array.append(self.two_bytes_to_integer(data[6],data[7]))
            array.append(self.one_byte_to_integer(data[8]))
            array.append(self.one_byte_to_integer(data[9]))
            array.append(self.one_byte_to_integer(data[10]))
            array.append(self.one_byte_to_integer(data[11]))
            length  = (self.one_byte_to_integer(data[12]))
            array.append(length)
            array.append(string)
            
            
            for i in range (0,len(headings)-1):
                print('{} {} {}'.format( i,array[i],headings[i]))
        print(string)

        
        
        
       
        

    def make_packet(self, packet_type, request_type):
        req_type_num = 2
        if (request_type == 'date'):
            req_type_num = 1
            
        to_sixteen_bits = lambda x: format(x, '016b')   # it appears that splitting like this yields the same
        packet = bytearray()                            # result as using a = magic_num.to_bytes(2, 'big'); it is  still more or less big endian
        construct = (to_sixteen_bits(self.magic_num))     #Split binary, append as bytes for 0-7, 8-15
        packet.append(int(construct[0:8],2))
        packet.append(int(construct[8:16],2))
        
        construct = (to_sixteen_bits(packet_type))
        packet.append(int(construct[0:8],2))
        packet.append(int(construct[8:16],2))
        
        construct = (to_sixteen_bits(req_type_num))
        packet.append(int(construct[0:8],2))
        packet.append(int(construct[8:16],2))
        
       # print ('PORT#' ,self.port,' Packettype = ', packet_type, ' requesttype = ', req_type_num,packet)
        return packet
    
    
    def terminate(self,message = "default end"):
        print(message)
        sys.exit()

    
if __name__ == "__main__":
    a  = (sys.argv[1:])
    print (a)
    if (len(a) != 3):
        print("Bad arguements, using default (date,127.0.0.1,1024) \nbecause this was probably run from the IDE with no params\nIf you're seeing this, then I forgot to remove it")
        a = ['date','localhost',1028]
    if ((a[0].lower() == 'time') or (a[0].lower() == 'date')):
        try:
            IP =  (socket.gethostbyname_ex(a[1]))[2][0]
        except socket.gaierror:
            print("cannot resolve IP")
            sys.exit()

        
        
        
        port = int(a[2])
        
        
        
        if ((port > 64000) or (port< 1024)):
            print("port range error")
            sys.exit()
        else:
            client = client(a[0],a[1],port, IP)
    else:
        print("Please specify <date/time> IP Port_num; Invalid date/time")
        sys.exit()           
