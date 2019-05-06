from bitstring import BitArray
from collections import namedtuple
from PackageData import PackageData


class DNSPackageParser:
    def __init__(self):
        # self.header_info = namedtuple('header_info', 'id, is_query is_recursion is_ra qdcount ancount')

    def extract_data(self, package):
        package_data = PackageData()
        bits_package = BitArray(hex=package).bin[2:]
        header = package[:12]
        answer = header[header.index(b'\x00') + 2:]


        def extract_header(self):
            package_data.id = header[:2].decode('utf-8')
            package_data.is_query = int(bits_package[16] == '0')
            package_data.is_authority = int(bits_package[21] == '1')
            package_data.is_recursion = int(bits_package[23] == '1')
            package_data.is_ra = int(bits_package[24] == '1')
            package_data.qdcount = int(bits_package[32:47], 2)
            package_data.ancount = int(bits_package[48:63], 2)

        def extract_answer(self):
            offset = int(answer[:2]) - 3 * (2 ** 14)
            package_data.name = 
            
            
            

           


            




