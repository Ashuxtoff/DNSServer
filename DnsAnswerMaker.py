from DnsServerCache import DNSServerCache


class DNSAnswerMaker:
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

    def __init__(self, request, cache: DNSServerCache):
        self.request = request
        self.cache = cache
        self.name, self.request_type = self.extract_request_data(self.request)
        self.names_dict = {}

    def make_header(self):
        request_id = self.request[:2]
        msg_type = b'\x81\x00'
        questions = self.request[4:6]
        answers = len(self.cache.database[self.request_type + self.name]).to_bytes(2, 'big')
        auth_add = b'\x00' * 4
        return request_id + msg_type + questions + answers + auth_add

    def make_query(self):
        last = 12
        self.names_dict[self.name] = last
        splitted = self.name.split('.')
        for i in range(list(self.name).count('.')):
            last += 1 + len(splitted[i])
            self.names_dict['.'.join(splitted[i + 1:])] = last
        data = b''    
        for label in splitted:
            data += len(label).to_bytes(1, 'big') + label.encode('utf-8')
        data += b'\x00'
        data += b'\x00\x01' if self.request_type == 'A' else b'\x00\x02'
        data += b'\x00\x01'
        return data            

    def make_answers(self, len_header, len_query):
        answers = []
        requested_data = self.cache.get_data(self.request_type, self.name)
        for i in range(len(requested_data)):
            name_ref = b'\xc0\x0c'
            type_code = b'\x00\x01' if self.request_type == 'A' else b'\x00\x02'
            class_in = b'\x00\x01'
            ttl = int(round(self.cache.ttl_dict[self.request_type + self.name][i])).to_bytes(4, 'big')
            first_part = name_ref + type_code + class_in + ttl
            if self.request_type == 'A':
                data_length = b'\x00\x04'
                data_list = [int(octet).to_bytes(1, 'big') for octet in self.cache.database['A' + self.name][i].split('.')]    
                data = b''.join(data_list)
                answers.append(first_part + data_length + data)
            else:
                second_part = b''
                splitted = self.cache.database[self.request_type + self.name][i].split('.')
                finished = False
                while not finished and len(splitted) > 0:
                    first_label = splitted[0] 
                    second_part += len(first_label).to_bytes(1, 'big') + first_label.encode()
                    remaining = '.'.join(splitted[1:])
                    if remaining in self.names_dict:
                        finished = True
                        second_part += b'\xc0' + self.names_dict[remaining].to_bytes(1, 'big')
                    else:
                        self.names_dict[remaining] = len_header + len_query + 2 + len(first_part) + len(second_part)
                        print(self.names_dict[remaining])
                    splitted = splitted[1:]
                answers.append(first_part + len(second_part).to_bytes(2, 'big') + second_part)
        return answers

    def make_package(self):
        header = self.make_header()
        print(len(header))
        print(header)
        query = self.make_query()
        print(len(query))
        print(query)
        answers = b''.join(self.make_answers(len(header), len(query)))
        print(len(answers))
        print(answers)
        return header + query + answers                          




            


        