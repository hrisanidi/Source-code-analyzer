"""
Brno University of Technology
Project: IPP1
Author: Vladislav Khrisanov (xkhris00)
"""

import sys


# the storage for individual statistics requests
class StatsRequest:
    def __init__(self, filename):
        self.filename = filename
        self.params = []
        self.to_print = []
        self.to_print_index = 0


# the logic of STATP extension
class StatsCollector:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StatsCollector, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.__requests = []
        self.__to_compute = set()

        self.__loc_cnt = 0
        self.__comment_cnt = 0
        self.__unique_label_cnt = 0
        self.__directionless_jump_cnt = 0
        self.__bad_jump_cnt = 0
        self.__fw_jump_cnt = 0
        self.__back_jump_cnt = 0

        self.__label_name_pos = dict()
        self.__jump_pos_name = dict()

        self.__opcode_frequency = dict()
        self.__frequent_opcodes = []

    # parse script arguments
    def initialize(self):
        request_index = None

        for i in range(1, len(sys.argv)):
            # --stats
            if len(sys.argv[i].split('=', 1)) == 2 and sys.argv[i].split('=', 1)[0] == '--stats':
                filename = sys.argv[i].split('=', 1)[1]
                if filename == '':
                    sys.exit(12)
                else:
                    # filename overlap
                    for request in self.__requests:
                        if filename == request.filename:
                            sys.exit(12)

                    # add a valid request
                    self.__requests.append(StatsRequest(filename))

                    if request_index is None:
                        request_index = 0
                    else:
                        request_index += 1
            # --print
            elif len(sys.argv[i].split('=', 1)) == 2 and sys.argv[i].split('=', 1)[0] == '--print':
                self.__requests[request_index].params.append('--print')
                self.__requests[request_index].to_print.append(sys.argv[i].split('=', 1)[1])
            # other parameters
            else:
                match sys.argv[i]:
                    case '--loc' | '--comments' | '--labels' | '--jumps' | '--eol':
                        pass
                    case '--fwjumps' | '--backjumps' | '--badjumps':
                        self.__to_compute.update({'j'})
                    case '--frequent':
                        self.__to_compute.update({'f'})
                    case _:
                        sys.exit(10)
                self.__requests[request_index].params.append(sys.argv[i])

    # gather data for the individual instruction
    def process_instruction(self, opcode, label_name, position):
        match opcode:
            case 'LABEL':
                if label_name not in self.__label_name_pos:
                    self.__unique_label_cnt += 1
                    self.__label_name_pos.update({label_name: position})
            case 'RETURN':
                self.__directionless_jump_cnt += 1
            case 'CALL' | 'JUMP' | 'JUMPIFEQ' | 'JUMPIFNEQ':
                self.__directionless_jump_cnt += 1
                self.__jump_pos_name.update({position: label_name})

        if opcode in self.__opcode_frequency:
            self.__opcode_frequency[opcode] += 1
        else:
            self.__opcode_frequency.update({opcode: 1})

    # compute the jump values based on the gathered data
    def __compute_jumps(self):
        for jump_pos, name in self.__jump_pos_name.items():
            label_pos = self.__label_name_pos.get(name)
            if label_pos is None:
                self.__bad_jump_cnt += 1
            elif label_pos > jump_pos:
                self.__fw_jump_cnt += 1
            elif label_pos < jump_pos:
                self.__back_jump_cnt += 1

    # compute the frequency values based on the gathered data
    def __compute_frequency(self):
        if self.__opcode_frequency:
            max_cnt = max(self.__opcode_frequency.values())

            for key in self.__opcode_frequency:
                if self.__opcode_frequency[key] == max_cnt:
                    self.__frequent_opcodes.append(key)

            self.__frequent_opcodes.sort()

    def set_loc_comments(self, loc_cnt, comment_cnt):
        self.__loc_cnt = loc_cnt
        self.__comment_cnt = comment_cnt

    def write_results(self):
        # if computation required for the output
        for computation in self.__to_compute:
            if computation == 'j':
                self.__compute_jumps()
            elif computation == 'f':
                self.__compute_frequency()

        for request in self.__requests:
            try:
                file = open(request.filename, 'w')
            except OSError:
                sys.exit(12)

            for parameter in request.params:
                match parameter:
                    case '--print':
                        file.write(request.to_print[request.to_print_index] + '\n')
                        request.to_print_index += 1
                    case '--loc':
                        file.write(str(self.__loc_cnt) + '\n')
                    case '--comments':
                        file.write(str(self.__comment_cnt) + '\n')
                    case '--labels':
                        file.write(str(self.__unique_label_cnt) + '\n')
                    case '--jumps':
                        file.write(str(self.__directionless_jump_cnt) + '\n')
                    case '--fwjumps':
                        file.write(str(self.__fw_jump_cnt) + '\n')
                    case '--backjumps':
                        file.write(str(self.__back_jump_cnt) + '\n')
                    case '--badjumps':
                        file.write(str(self.__bad_jump_cnt) + '\n')
                    case '--frequent':
                        value = ''
                        opcode_cnt = len(self.__frequent_opcodes)
                        for i, opcode in enumerate(self.__frequent_opcodes):
                            value += opcode
                            if i + 1 != opcode_cnt:
                                value += ','
                        file.write(value + '\n')
                    case '--eol':
                        file.write('\n')
            file.close()
