import socket,select,sys,os,datetime

#
# This is a solution to the first assignment for cosc264. 
# I'd advise against copying it, this implementation uses formatting tools
# To construct packets, the reccommended way is to use a a.to_bytes implementation
# But... I found this a bit easier, itll stick out like a sore thumb if copied
#

class server():
    """Server opens three UDP sockets and waits for a connection then DT_request packet,
    It will then return a packet containing date time information depending on the request, the ports 
    a,b,c will dictate the language results    
    
    If a packet is received on:
    Port Lang
    1    - English
    2    - German
    3    - maori
    
    the ports are provided as integers from console; likewise specifying
    
    date/time as a field in the request packet dictates the template returned.
    
    """

    def __init__(self,a,b,c):
        self.pkt_type = 0
        self.req_type = 0
        self.magic_num = 0x497e
        self.lang_type = 0
        self.load_identities()
        self.IP = socket.gethostbyname(socket.gethostname())
        self.portarray = [a,b,c]
        print("Server launched with", self.IP, " on ", self.portarray)
        self.make_socket(a,b,c,self.IP)
        self.wait_on_request()
    
    
    def load_identities(self):
        """Reference values are kept"""
        self.deutsch_library = ['Januar', 'Februar', 'M ̈arz', 'April', 'Mai', 
                       'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
        self.deutsch_template = ['Heute ist der {} {} {}','Die Uhrzeit ist {}:{}']
        
        self.englisch_library = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                   'September', 'October', 'November', 'December']
        self.englisch_template = ['Today’s date is {} {} {}','The current time is {}:{}']
        
        self.maori_library = ['Kohita ̄tea','Hui-tanguru', 'Poutu ̄-te-rangi',
                 'Paenga-wh ̄awh ̄a', 'Haratua', 'Pipiri','Ho ̄ngongoi','Here-turi-k ̄oka ̄',
                 'Mahuru','Whiringa-a ̄-nuku','Whiringa-a ̄-rangi', 'Hakihea']
        self.maori_tempalte = ['Ko te ra o tenei ra ko {} {} {}','Ko te wa o tenei wa {}:{}']
        
    def make_16_bit_binary(self, number):
        """returns a value as it's 16-bit binary representation with leading 0s"""
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

    def make_socket(self,porta, portb, portc,server_place):
        """Checks range of port numbers is between 1024 and 64000 and that they are all unique,
        Then assigns these ports to individual sockets"""
        if ((porta < 1024) or (porta > 64000)):
            print("invalid port num")
            self.terminate();
        if ((portb < 1024) or (portb > 64000)):
            
            print("invalid port num")
            self.terminate();    
        if ((portc < 1024) or (portc > 64000)):
            print("invalid port num")
            self. terminate();    
        if (porta == portb == portc):
            print("duplicate port number")
            self. terminate();
        try:
            # Binds sockets and gives SO_REUSEADDR: which allows us to reopen
            self.sock1 = socket.socket() 
            self.sock2 = socket.socket() 
            self.sock3 = socket.socket() 
            self.sock1.bind((server_place,porta))
            self.sock2.bind((server_place,portb))
            self.sock3.bind((server_place,portc))
        except:
            self.terminate("unable to bind sockets");


    def terminate(self, errormessage = "no message set"):
        """standard terminator, calls system exit because branched process doesnt get on
        with systemexit"""
        print (errormessage)
        SystemExit()
        os._exit(0)

    def wait_on_request2(self):
        """Listens on the three sockets with backlog allowing to 5 queued connections"""
        
        self.sock1.listen(5)
        self.sock2.listen(5)
        self.sock3.listen(5) 
        self.sock1.setblocking(1)
        self.sock2.setblocking(1)
        self.sock3.setblocking(1)
        while True:
            inputs = [self.sock1,self.sock2,self.sock3]
            incoming, a, b = select.select(inputs, [], inputs)
            recev_ad  =  (incoming[0].getsockname());
            self.connection,address = incoming[0].accept()
            data_in = self.connection.recv(64); 
            if self.verify_dt_request(data_in) == True:
                self.lang_type = self.portarray.index(recev_ad[1])+1
                self.response()



    def wait_on_request(self):
        """Listens on the three sockets with backlog allowing to 5 queued connections
        when received a requestion as inputs from select() the method takes the received and verifies
        that it is in fact a dt_request"""
        
        self.sock1.listen(5)
        self.sock2.listen(5)
        self.sock3.listen(5)
        self.sock1.setblocking(1)
        self.sock2.setblocking(1)
        self.sock3.setblocking(1)
        inputs = [self.sock1,self.sock2,self.sock3]
        incoming, a, b = select.select(inputs, [], inputs)
        if incoming[0]:
            recev_ad  =  (incoming[0].getsockname());
            self.connection,address = incoming[0].accept()
            data_in = self.connection.recv(64); 
            if self.verify_dt_request(data_in) == True:
                self.lang_type = self.portarray.index(recev_ad[1])+1
                print('Received a request for #{} language and type {}'.format(self.lang_type,self.req_type))
                self.response()
        self.wait_on_request()
                
    def response(self):
        """attempts to send things the other way around"""
        to_send = self.build_response()
        self.connection.send(to_send)
        self.connection.close()
        
        
        
    def build_response(self):
        time = datetime.datetime.now()
        reply_str = (self.textual_repr(time))
        encoded = reply_str.encode('utf-8')
        packet = bytearray(13+(len(encoded)))
        
        insert = (self.make_16_bit_binary(self.magic_num))
        packet[0] = int(insert[0:8],2)
        packet[1] = int(insert[8:16],2)
        
        insert = (self.make_16_bit_binary(2))
        packet[2] = int(insert[0:8],2)
        packet[3] = int(insert[8:16],2)        
        
        
        insert = (self.make_16_bit_binary(self.lang_type))
        packet[4] = int(insert[0:8],2)
        packet[5] = int(insert[8:16],2)
        
        insert = (self.make_16_bit_binary(time.year))
        packet[6] = int(insert[0:8],2)
        packet[7] = int(insert[8:16],2)        
        
        packet[8] = int(self.make_8_bit_binary(time.month),2)
        packet[9] = (int(self.make_8_bit_binary(time.day),2))
        packet[10] = (int(self.make_8_bit_binary(time.hour),2))
        packet[11] = (int(self.make_8_bit_binary(time.minute),2))        
        packet[12] = (int(self.make_8_bit_binary(len(encoded)),2))  
        
        place = 0
        for a in (encoded):
            packet[13+place] = a
            place += 1
        return packet

    
    def textual_repr(self,time):
        """returns the text to send, note that if for some odd reason lang_type is not in (1,3) 
        we default to english instead of raising an error, its impossible, but this computer is magic"""
        
        if self.lang_type == 3:
            months_names = self.deutsch_library
            template = self.deutsch_template

        elif (self.lang_type == 2):
            months_names = self.maori_library
            template = self.maori_tempalte

        else:
            months_names = self.englisch_library     
            template = self.englisch_template
            
            
        if (self.pkt_type == 1):
            return (template[0].format(time.day, months_names[time.month-1],time.year))
        return (template[1].format(time.hour, time.minute))
        
       
   
    
    def verify_dt_request(self,data_in):
        """ Verifies that a dt_request contains valid data i.e. 0x497e identifier
        and that the req, pkt types are valid, calls terminate if they are not"""
        if (type(data_in) != bytes):
            return False
        
        if (data_in == b''):
            return False;

        received_num = self.two_bytes_to_integer(data_in[0],data_in[1])
        if ((received_num) != (self.magic_num)):
            self.terminate("INVALID IDENTIFIER FOR PACKET")
        else:
            try:
                self.pkt_type = self.two_bytes_to_integer(data_in[2],data_in[3])
                self.req_type = self.two_bytes_to_integer(data_in[4],data_in[5])
            except IndexError:
                self.terminate("Received too few bytes")
            except:
                self.terminate()
            if (self.pkt_type != 1):
                self.terminate("This is not a date time request packet")
            elif (not((self.req_type == 1) ^ (self.req_type == 2))):
                self.terminate("The request is neither 1 or 2")
            return True;
        return False;
        

        


if __name__ == "__main__": 
    a  = (sys.argv[1:])
    if (len(a) == 3):
        instance = server(int(a[0]), int(a[1]), int(a[2]))
    else:
        #using default state, if called by IDE this is useful
        instance = server(1024,1025,1026)
        
