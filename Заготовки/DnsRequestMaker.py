import binascii


class DNSRequestMaker:
    def __init__(self, requested_name, package_id, rr_type):
        self.name = requested_name
        self.id = package_id
        self.type = rr_type

    def make_header(self):
        package_id = self.id
        request_params = '0100'
        qd_count = '0001'
        an_count = '0000'
        ns_ar_count = '00000000'
        return binascii.unhexlify(bytes(
            package_id + request_params + qd_count + an_count + ns_ar_count,
            'utf-8'))

    def make_question(self):
        name = b''
        sections = self.name.split('.')
        for section in sections:
            name += bytes(len(section))
            name += section.encode('utf-8')
        name += b'0'
        if self.type == 'A':
            name += b'0001'
        elif self.type == 'MX':
            name += b'0002'
        else: 
            raise Exception('Wrong RR type')
        name += b'0001'
        return binascii.unhexlify(name)

    def make_request(self):
        return self.make_header() + self.make_question()            




        