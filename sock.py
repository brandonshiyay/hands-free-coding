import socket

interface = 'wlp2s0'
port = 8002
s=socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))
s.bind((interface, port))
s.listen(5)
print('starting listening')
while True:
	data = s.recvfrom(4096)
	print(data)