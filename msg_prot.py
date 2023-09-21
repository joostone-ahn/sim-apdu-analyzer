debug_mode = 0
# debug_mode = 1,2

def debug_message(msg, prot_data, prot_start_item, prot_data_item, prot_type_item):
    if debug_mode == 2:
        print(msg)
        print("  sum_num: [%d]" % (len(prot_data) + 1))
        print("  start_line:", prot_start_item[0])
        for i in range(len(prot_data_item)):
            print("  [%d]" % i, "[%s]" % prot_type_item[i], prot_data_item[i])
        print("=" * 50)
        return

def process(input):
    exe_start, exe_end, exe_type, exe_data = input

    prot_start, prot_end, prot_type, prot_data = [],[],[],[]
    prot_start_item, prot_end_item, prot_type_item, prot_data_item = [],[],[],[]
    cmd_type = []

    cmd_cnt = 0
    # prev_exe_data = None

    for n in range(len(exe_start)):
        if debug_mode == 1:
            print("exe_type   :", [exe_type[n]])
            print("exe_data   :", [exe_data[n]])
            print("cmd_cnt    :", cmd_cnt)
            print("-" * 50)

        if cmd_cnt == 0:
            # RX without TX
            if exe_type[n] == 'RX':
                if debug_mode == 2:
                    print("RX wo/ TX")
                    print("  start_line:", exe_start[n])
                    print("  discard_data:", exe_data[n])
                    print("=" * 50)
                continue

            # 1st TX data length has to be 5 Bytes
            if exe_type[n] == 'TX':
                if len(exe_data[n]) != 10:
                    if debug_mode == 2:
                        print("1st Tx data length is not 5 Bytes")
                        print("  start_line:", exe_start[n])
                        print("  discard_data:", exe_data[n])
                        print("=" * 50)
                    continue

        cmd_cnt += 1
        prot_start_item.append(exe_start[n])
        prot_end_item.append(exe_end[n])
        prot_type_item.append(exe_type[n])
        prot_data_item.append(exe_data[n])

        # RESET, ATR 등
        if exe_type[n] != 'TX' and exe_type[n] != 'RX':
            cmd_type.append(exe_type[n])

        # TX, RX
        else:
            error_flag = 0
            # consecutive TX or RX
            if cmd_cnt >= 2:
                if prot_type_item[-2] == prot_type_item[-1]:
                    cmd_type.append("ERROR_1: consecutive TX or RX")
                    error_flag = 1
                    debug_message(cmd_type[-1], prot_data, prot_start_item, prot_data_item, prot_type_item)

            if exe_type[n] == 'TX':
                # TX data length error
                if cmd_cnt >= 3:
                    if len(prot_data_item[-2]) == 2: # Case 3 or 4
                        P3 = prot_data_item[-3][-2:]
                        Lc = int(P3, 16)*2
                        if len(prot_data_item[-1]) != Lc:
                            cmd_type.append('ERROR_2: TX data length error')
                            debug_message(cmd_type[-1], prot_data, prot_start_item, prot_data_item, prot_type_item)

            elif exe_type[n] == 'RX':
                # INS not included in RX data
                # OR MANGE CHANNEL(Close), ENABLE/DISABLE/VERIFY/CHANGE PIN
                if cmd_cnt == 2:
                    if prot_data_item[-2][2:4] != prot_data_item[-1][:2]:
                        cmd_type.append("INS not included in RX data")
                        error_flag = 1
                        debug_message(cmd_type[-1], prot_data, prot_start_item, prot_data_item, prot_type_item)

                # INS included in RX data
                if error_flag == 0:
                    if len(exe_data[n]) == 4:
                        if cmd_cnt == 2:
                            if exe_data[n][-4:-2] != '6C': # case2
                                cmd_type.append('Case1')
                        elif cmd_cnt > 2:
                            if exe_data[n][-4:-2] != '61':
                                cmd_type.append('Case3')
                    elif len(exe_data[n]) > 4:
                        if exe_data[n][:2] == 'C0' :
                            if exe_data[n][-4:-2] != '61':
                                cmd_type.append('Case4')
                        elif exe_data[n][:2] == '60': # need to check '60' tag. (guess: response delay)
                            if exe_data[n][-4:-2] != '61':
                                cmd_type.append('Case60')
                        else:
                            if exe_data[n][:2] == prot_data_item[-2][2:4]:
                                cmd_type.append('Case2')

                    # Status word error
                    elif len(exe_data[n]) < 4:
                        if cmd_cnt >= 4:
                            cmd_type.append('ERROR_3: Status word error')
                            debug_message(cmd_type[-1], prot_data, prot_start_item, prot_data_item, prot_type_item)

        # cmd_type determined
        if len(cmd_type) > len(prot_type):
            cmd_cnt = 0
            prot_start.append(prot_start_item)
            prot_end.append(prot_end_item)
            prot_type.append(prot_type_item)
            prot_data.append(prot_data_item)
            prot_start_item, prot_end_item, prot_type_item, prot_data_item = [], [], [], []

            # ERROR 예외 처리
            if "ERROR" in cmd_type[-1]:
                # ERROR data 제거
                del prot_start[-1][-1]
                del prot_end[-1][-1]
                del prot_type[-1][-1]
                del prot_data[-1][-1]

                if exe_type[n] == 'TX' and len(exe_data[n]) == 10:
                    cmd_cnt = 1
                    prot_start_item.append(exe_start[n])
                    prot_end_item.append(exe_end[n])
                    prot_type_item.append(exe_type[n])
                    prot_data_item.append(exe_data[n])

            if debug_mode == 1:
                print("sum_num    : [%d]"%(len(prot_type)))
                print("cmd_type   :", cmd_type[-1])
                print("prot_data  :", prot_data[-1])
                print("="*50)

    return prot_start, prot_end, prot_type, prot_data

def rst(input, item_num, load_type):
    msg_all, prot_start, prot_type, prot_data = input
    start = prot_start[item_num]
    type = prot_type[item_num]
    data = prot_data[item_num]

    prot_rst = []
    if data[0]:
        for n in range(len(data)):
            if n == 0:
               rst_ind = '[%s]' % str(item_num + 1)
            else:
                rst_ind = ' '*len(rst_ind)

            if load_type == 'File':
                rst_time = msg_all[start[n]].split('  ')[1].split('  [')[0]
            elif load_type == 'Paste':
                rst_time = msg_all[start[n]].split('                 ')[1].split(' ')[0]
            if 'RX' in type[n]: rst_type = '[RX]'
            elif 'TX' in type[n]: rst_type = '[TX]'

            rst_data = ''
            cnt = 0
            for m in range(len(list(data[n]))):
                if m%32 == 0 and m//32 > 0:
                    rst_data += '\n' + ' '*(len(rst_ind)+len(rst_time)+len(rst_type)+5)
                if m%2 ==0 :
                    rst_data += list(data[n])[m]
                    cnt +=1
                else:
                    rst_data += list(data[n])[m] + ' '
                    cnt +=2
            prot_rst.append(rst_ind + ' ' + rst_time + '  ' + rst_type + '  ' + rst_data)
            if n!= len(data)-1: prot_rst.append(' '*(len(rst_ind)+1) + '-' *(80-len(rst_ind)-1))
            if debug_mode == 1:
                print('rst_time :', rst_time)
                print('rst_type :', rst_type)
                print('rst_data :', rst_data)
                print()

    return prot_rst