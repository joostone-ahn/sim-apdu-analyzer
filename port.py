debug_mode = 0
def process(input, index):
    msg_all, msg_start, msg_end, msg_SN, msg_type, msg_data = input
    exe_start, exe_end, exe_type, exe_data = [],[],[],[]

    SN_prev = None
    for n in index:
        exe_start.append(msg_start[n])
        exe_end.append(msg_end[n])
        exe_type.append(msg_type[n])
        exe_data.append(msg_data[n])
        if SN_prev != msg_SN[n]:
            SN_prev = msg_SN[n]
        else:
            del exe_start[-1], exe_end[-1], exe_type[-1], exe_data[-1]
            if msg_all[exe_end[-1]-1] != '  ':
                exe_start[-1] = msg_start[n]
                exe_end[-1] = msg_end[n]
                exe_type[-1] = msg_type[n]
                exe_data[-1] = msg_data[n]
            else:
                continue

    return exe_start, exe_end, exe_type, exe_data