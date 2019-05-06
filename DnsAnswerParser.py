import binascii
import re
from AnswerItem import AnswerItem
from IPy import IP


class DNSArswerParser:
    def __init__(self, package):
        self.package = package
        self.answer = []
        self.authority = []
        self.additional = []      

    def detect_type(self):
        query = self.package[12:]
        prev = query.index(b'\00')
        type_code = int.from_bytes(query[prev + 1 : prev + 3], 'big')
        if type_code == 1:
            return 'A'
        if type_code == 2:
            return 'NS'    

    def detect_name(self):
        labels = []
        query = self.package[12:]
        cursor = 0
        label_length = query[cursor]
        while label_length != 0:
            cursor += 1
            labels.append(query[cursor : cursor + label_length])
            cursor += label_length
            label_length = query[cursor]
        return '.'.join([label.decode() for label in labels])

    def read_recursive_labels(self, bytes_sequence, cursor, result):
        # print(bytes_sequence[cursor - 1 : cursor + 2])
        if bytes_sequence[cursor] >= 192:
            # print(bytes_sequence[cursor])
            cursor = int.from_bytes(bytes_sequence[cursor : cursor + 2], 'big') - 3 * 2 ** 14
            label_length = self.package[cursor]
            while label_length != 0 and label_length < 63:
                # print(self.package[cursor])
                cursor += 1
                label = self.package[cursor : cursor + label_length]
                result.append(label)
                cursor += label_length
                label_length = self.package[cursor]
            # cursor += 1    #тут говно
            self.read_recursive_labels(self.package, cursor, result)
        return result                

    def extract_answer_data(self):
        answer_number = int.from_bytes(self.package[6:8], 'big')
        authority_number = int.from_bytes(self.package[8:10], 'big')
        additional_number = int.from_bytes(self.package[10:12], 'big')
        read_tokens_count = 0
        question = self.package[12:]
        answer = question[question.index(b'\00') + 5:]
        # print(answer)
        cursor = 0
        while read_tokens_count < answer_number + authority_number + additional_number:
            cursor += 6
            # print(answer[cursor - 1 : cursor + 2])
            ttl = int.from_bytes(answer[cursor : cursor + 4], 'big')
            cursor += 4
            data_length = int.from_bytes(answer[cursor : cursor + 2], 'big')
            cursor += 2
            if data_length == 4:
                data = '.'.join([str(octet) for octet in answer[cursor : cursor + data_length]])
                cursor += data_length
            else:
                data = ''
                next_length = answer[cursor]
                # print(answer)
                while next_length < 63:
                    cursor += 1
                    data += answer[cursor : cursor + next_length].decode('utf-8') + '.'
                    cursor += next_length
                    next_length = answer[cursor]
                # if data == 'ns2':
                #     a = 1
                labels = self.read_recursive_labels(answer, cursor, [])
                cursor += 2
                data += '.'.join(label.decode() for label in labels)
            if read_tokens_count >= answer_number + authority_number:
                self.additional.append(AnswerItem(data, ttl))
            elif read_tokens_count >= answer_number:
                self.authority.append(AnswerItem(data, ttl))
            else:
                self.answer.append(AnswerItem(data, ttl))
            read_tokens_count += 1    
        return ({'answer' : self.answer,
                'authority' : self.authority if len(self.authority) != 0 else None,
                'additional' : self.additional if len(self.additional) != 0 else None
                }, self.detect_type(), self.detect_name())
            


        