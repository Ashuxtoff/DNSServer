import time


class DNSServerCache:
    def __init__(self, backup_file):
        self.backup_file = backup_file
        self.database = {}
        self.ttl_dict = {}
        self.last_viewed_time = time.time()
        with open(backup_file) as f:
            lines = f.readlines() # формат записи в файл: первая строка - время, в которое произошла запись в файл
            if len(lines) > 0:
                rewrite_time = float(lines[0][:-1])
                for line in lines[1:]: # далее - ключ: значение : ttl
                    splitted_line = line.split()
                    key = splitted_line[0]
                    splitted_line = splitted_line[1:]
                    if len(splitted_line) != 0:
                        self.database[key] = []
                        self.ttl_dict[key] = []
                        for i in range(len(splitted_line)):
                            if i % 2 == 0:
                                self.database[key].append(splitted_line[i])
                            else:
                                self.ttl_dict[key].append(float(splitted_line[i]) - (time.time() - rewrite_time))
                self.delete_old_data()
                

    def add(self, data_dict, domain_name, response_type):
        self.database[response_type + domain_name] = [data.data for data in data_dict['answer']]
        self.ttl_dict[response_type + domain_name] = [data.ttl for data in data_dict['answer']]
        if data_dict['authority'] is not None:
            names = [data.data for data in data_dict['authority']]
            ttls = [data.ttl for data in data_dict['authority']]
            ips = [data.data for data in data_dict['additional']]
            ns_list = []
            for i in range(len(names)):
                if i < len(ips):
                    self.database['A' + names[i]] = [ips[i]]
                    self.ttl_dict['A' + names[i]] = [ttls[i]]
                    ns_list.append(names[i])
                else:
                    ns_list.append(names[i])
            self.database['NS' + domain_name] = ns_list
            self.ttl_dict['NS' + domain_name] = ttls
        self.update_ttl(time.time())
        self.delete_old_data()
        self.write_backup()    

    def delete_old_data(self):
        removing_indexes = []
        removing_keys = []
        for key in self.ttl_dict:
            for i in range(len(self.ttl_dict[key])):
                if self.ttl_dict[key][i] < 0:
                    removing_indexes.append(i)
            for i in removing_indexes[::-1]:
                del self.ttl_dict[key][i]
                del self.database[key][i]        
            removing_indexes.clear()
            if self.ttl_dict[key] == []:
                removing_keys.append(key)
        for key in removing_keys:
            self.database.pop(key)
            self.ttl_dict.pop(key)    

    def update_ttl(self, t):
        for key in self.ttl_dict:
            for i in range(len(self.ttl_dict[key])):
                self.ttl_dict[key][i] -= time.time() - t

    def write_backup(self):
        with open(self.backup_file, 'w') as f:
            f.write(str(time.time()))
            for key in self.database:
                f.write('\n')
                f.write(key)
                for i in range(len(self.database[key])):
                    f.write('   ' + self.database[key][i] + '   ' + str(self.ttl_dict[key][i]))

    def get_data(self, query_type, domain_name):
        removed_keys = []
        now = time.time()
        time_difference = now - self.last_viewed_time
        for key in self.ttl_dict:
            for i in range(len(self.ttl_dict[key])):
                self.ttl_dict[key][i] -= time_difference
                if self.ttl_dict[key][i] <= 0:
                    removed_keys.append(self.database[key][i])            
        for key in removed_keys:
            for data in self.database:
                self.database[data].remove(key)
            self.ttl_dict[key] = [time for time in self.ttl_dict[key] if time > 0]        
        self.last_viewed_time = now
        if query_type + domain_name in self.database:
            return self.database[query_type + domain_name]

    def check_data(self, name, type_request):
        if type_request + name in self.database:
            return self.database[type_request + name]
