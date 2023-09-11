debug_mode = 1
def process(input, index):
    msg_all, msg_start, msg_end, msg_SN, msg_type, msg_data = input
    exe_start, exe_end, exe_type, exe_data = [],[],[],[]

    SN_prev = None
    for n in index:
        exe_start.append(msg_start[n])
        exe_end.append(msg_end[n])
        exe_type.append(msg_type[n])
        exe_data.append(msg_data[n])

        # 230911 APDU 로그 빠짐 현상 대응 (SN 가 2이상 증가한 경우)
        if SN_prev != None:
            if msg_SN[n] >= SN_prev+2:
                if debug_mode:
                    print("log loss line (start, end, type):", msg_start[n], msg_end[n], msg_type[n])
                # 로그가 누락 후 단말 TX 없이 곧바로 SIM RX 로그 확인되면 parsing 불가하므로 제외
                if msg_type[n] == 'RX':
                    del exe_start[-1], exe_end[-1], exe_type[-1], exe_data[-1]
                    continue

        if SN_prev != msg_SN[n]:
            SN_prev = msg_SN[n]
        else:
            # if debug_mode:
            #     print("log duplicated line:", msg_start[n], msg_end[n])
            del exe_start[-1], exe_end[-1], exe_type[-1], exe_data[-1]
            if msg_all[exe_end[-1]-1] != '  ':
                exe_start[-1] = msg_start[n]
                exe_end[-1] = msg_end[n]
                exe_type[-1] = msg_type[n]
                exe_data[-1] = msg_data[n]
                # print(" post", exe_start)
                # print(" post", exe_data)
            else:
                continue
                # print("*prev", exe_start)
                # print("*prev", exe_data)

    return exe_start, exe_end, exe_type, exe_data