# COSC264



Couple of quick wee notes about this solution;

1. This is not the most efficient implementation; Python does not store the location of the end of one of their lists, so 
do note that when assembling a request packet.




Quick synopsis:

The client creates and sends a dt_request packet to a server/port specified by the command line. I have tested this locally and with my own wee server hole but further testing was unavailable, so locally its fine but externally there may be some ipv6 vs ipv4 issues. 

The server.py receives the dt_request, makes sure its all dandy (that is the header is tip top and valid) and returns a dt_response and terminates connection with the client. 


That's about it. 
