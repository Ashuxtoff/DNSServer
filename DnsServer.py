import socket
import select
import binascii
from DnsAnswerParser import DNSArswerParser
from DnsServerCache import DNSServerCache
from DnsAnswerMaker import DNSAnswerMaker


PORT = 53
IP = "127.0.0.1"


class DNSServer:
    def __init__(self):
        with open('config.txt') as f:
            line = f.readline()
            self.forwarder = line.split(' ')[1]
        self.cache = DNSServerCache("backup.txt")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((IP, PORT))
        self.forwarder_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.forwarder_sock.connect((self.forwarder, PORT))

    def extract_request_data(self, ns_request):
        labels = []
        query = ns_request[12:]
        cursor = 0
        label_length = query[cursor]
        while label_length != 0:
            cursor += 1
            labels.append(query[cursor : cursor + label_length])
            cursor += label_length
            label_length = query[cursor]
        name = '.'.join([label.decode() for label in labels])
        cursor += 2
        query_type = 'A' if query[cursor] == 1 else 'NS'
        return (name, query_type)    

    def run(self):
        while True:
            query, addr = self.sock.recvfrom(1024) 
            parser = DNSArswerParser(query) 
            n, t = self.extract_request_data(query) #
            # parsed_query = parser.extract_answer_data() 
            if self.cache.get_data(t, n): #
                answer_maker = DNSAnswerMaker(query, self.cache) 
                response = answer_maker.make_package() 
                self.sock.sendto(response, addr)  
            else: 
                self.forwarder_sock.sendto(query, (self.forwarder, PORT)) 
                response, _ = self.forwarder_sock.recvfrom(4096) 
                response = response[:2] + b'\x81' + response[3:]
                self.sock.sendto(response, addr) 
                parser = DNSArswerParser(response) 
                data, response_type, response_name = parser.extract_answer_data() 
                self.cache.add(data, response_name, response_type)

server = DNSServer()
server.run()                







    
        
















# while True:
#             request = self.sock.recvfrom(1024)[0]
#             request_name, request_type = self.extract_request_data(request)
#             if self.cache.get_data(request_type, request_name):
#                 answer_maker = DNSAnswerMaker(request, self.cache)
#                 response = answer_maker.make_package()
#                 self.sock.sendto(response, (IP, PORT))
#             else:
#                 self.forwarder_sock.sendto(request, (self.forwarder, PORT))
#                 response = self.forwarder_sock.recvfrom(1024)[0]
#                 self.sock.sendto(response, (IP, PORT))
#                 parser = DNSArswerParser(response)
#                 data, response_type, response_name = parser.extract_answer_data()
#                 self.cache.add(data, response_name)












    # rlist, _, _ = select.select([sock], [], [])
    # #  rlist != []:
    # request = sock.recv(512)
    # new_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # new_sock.connect((forwarder, PORT))
    # new_sock.send(request)
    # forwarder_responce = new_sock.recv(512)
    # print(len(forwarder_responce))
    # parser = DNSArswerParser(forwarder_responce)
    # data, query_type, domain_name = parser.extract_answer_data()
    # cache.add(data, domain_name)
    # result = cache.get_data(query_type, domain_name)
    # answer = 'Не заслуживающий доверия ответ:\n'
    # for data_item in result:
    #     answer += data_item + '\n'
    # print(answer)
    # sock.sendto(answer.encode('utf-8'), (IP, PORT))
    # sock.shutdown(socket.SHUT_RDWR)
    # sock.close()
