debug_mode = 0

def process(input):
    exe_start, exe_end, exe_type, exe_data = input

    prot_start, prot_end, prot_type, prot_data = [],[],[],[]
    prot_start_item, prot_end_item, prot_type_item, prot_data_item = [],[],[],[]
    cmd_type = []

    cmd_cnt = 0
    prev_exe_data = None

    for n in range(len(exe_start)):
        if debug_mode:
            print("exe_type   :", [exe_type[n]])
            print("cmd_cnt    :", cmd_cnt)
            print("exe_data   :", [exe_data[n]])
            print("")

        # 230910 SIM 에서 APDU 응답이 두 번 올라오는 케이스가 있음
        if exe_data[n] == prev_exe_data:
            continue
        prev_exe_data = exe_data[n]

        if exe_type[n] != 'TX' and exe_type[n] != 'RX':
            prot_start.append([exe_start[n]])
            prot_end.append([exe_end[n]])
            prot_type.append([exe_type[n]])
            prot_data.append([exe_data[n]])
            cmd_type.append([exe_type[n]])
        else:
            prot_start_item.append(exe_start[n])
            prot_end_item.append(exe_end[n])
            prot_type_item.append(exe_type[n])
            prot_data_item.append(exe_data[n])
            if exe_type[n] == 'TX' :
                cmd_cnt += 1
                if cmd_cnt > 1:
                    if len(prot_data_item[-2]) == 2: # [INS] Case3 or Case4
                        P3 = prot_data_item[-3][-2:]
                        Lc = int(P3, 16)*2
                        if len(prot_data_item[-1]) != Lc :
                            cmd_type.append('ERROR')
            elif exe_type[n] == 'RX':
                if len(exe_data[n]) == 4:
                    if cmd_cnt == 1:
                        if exe_data[n][-4:-2] != '6C': # case2
                            cmd_type.append('Case1')
                    elif cmd_cnt > 1:
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
                        if exe_data[n][:2] == prot_data_item[-2][2:4]:  # [INS]
                            cmd_type.append('Case2')

        if len(cmd_type) > len(prot_type) : # cmd_type_appended
            if cmd_type[-1] == 'ERROR' :
                cmd_cnt -= 1
                del prot_start_item[-1], prot_end_item[-1]
                del prot_type_item[-1], prot_data_item[-1]

            prot_start.append(prot_start_item)
            prot_end.append(prot_end_item)
            prot_type.append(prot_type_item)
            prot_data.append(prot_data_item)

            if debug_mode:
                print("cmd_type   :", cmd_type[-1])
                print("cmd_cnt    :", cmd_cnt)
                print("prot_data  :", prot_data[-1])
                print()

            if cmd_type[-1] == 'ERROR':
                cmd_cnt = 1
                prot_start_item, prot_end_item, prot_type_item, prot_data_item = [],[],[],[]
                prot_start_item.append(exe_start[n])
                prot_end_item.append(exe_end[n])
                prot_type_item.append(exe_type[n])
                prot_data_item.append(exe_data[n])
            else:
                cmd_cnt = 0
                prot_start_item, prot_end_item, prot_type_item, prot_data_item = [],[],[],[]

    return prot_start, prot_end, prot_type, prot_data


def rst(input, item_num, load_type):
    msg_all, prot_start, prot_type, prot_data = input
    start = prot_start[item_num]
    type = prot_type[item_num]
    data = prot_data[item_num]

    prot_rst = []
    if data[0]:
        for n in range(len(data)):
            if n ==0:
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
            if debug_mode:
                print('rst_time :', rst_time)
                print('rst_type :', rst_type)
                print('rst_data :', rst_data)
                print()

    return prot_rst