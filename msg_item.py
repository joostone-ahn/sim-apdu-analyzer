debug_mode = 0
import re

# Open file
def QCAT(msg):
    msg_start, msg_end, msg_SN, msg_port, msg_type = [],[],[],[],[]
    for n in range(len(msg)):
        if '0x19B7' in msg[n]:
            msg_start.append(n)
            msg_end.append(n-1)
        if 'Sequence Number' in msg[n]:
            msg_SN.append(int(msg[n].split('= ')[1]))
        if 'Slot Id' in msg[n]:
            msg_port.append(int(msg[n].split('= SLOT_')[1]))
        if 'Message Type' in msg[n]:
            msg_type.append(msg[n].split('= ')[1])
    if msg_end:
        msg_end.remove(msg_start[0]-1)
        msg_end.append(len(msg)-1)

    msg_data = []
    for m in range(len(msg_start)):
        msg_data.append('')
        for n in range(msg_start[m], msg_end[m]+1):
            if 'Data' in msg[n] or 'DATA' in msg[n]:
                if '{' in msg[n]:

                    # single line
                    if '}' in msg[n]:
                        msg_data[-1] = msg[n].split('{')[1].split('}')[0].replace(' ','')

                    # multiple lines
                    else:
                        msg_data_item = ''
                        for a in range(n+1, msg_end[m]+1):
                            msg_data_item += msg[a].replace(' ', '')
                            if '}' in msg[a]:
                                msg_data[-1] = msg_data_item.replace('}','').replace(' ','')
                                break
                else:
                    msg_data[-1] = msg[n].split('= ')[1].replace('\x00','').replace(' ', '')
                break
    return msg_start, msg_end, msg_SN, msg_port, msg_type, msg_data

# Load clipboard
def QXDM(msg_all):
    msg_start, msg_end, msg_SN, msg_port, msg_type, msg_data = [], [], [], [], [], []

    if '19B7' not in msg_all[0]:
        return [], [], [], [], [], []

    cnt = 0
    CONTINUED = 0
    for n in range(len(msg_all)):
        if msg_all[n] == '': break
        cnt += 1
        if CONTINUED == 0:
            msg_start.append(n)
            msg_end.append(n)
            msg_SN.append(cnt)
            msg_port.append(int(msg_all[n].split("SLOT_")[1][0]))

            type_str = msg_all[n].split("Type =")[1]

            # ATR, PPS
            if "DATA" in type_str:
                msg_type.append(type_str.split(" DATA")[0][1:].replace(' ', '_')) # ATR_RX / ATR_TX / PPS_RX / PPS_TX
                msg_data.append(type_str.split("=")[1])
                if '{' in msg_data[-1]:
                    msg_data[-1] = msg_data[-1].split('}')[0].replace('{', '').replace(' ', '')

            # RX, TX
            elif "Data" in type_str:
                msg_type.append(type_str.split(" Data")[0][1:])
                msg_data.append(type_str.split("=")[1])

                if '{' in msg_data[-1]:
                    # single line
                    if '}' in msg_data[-1]:
                        msg_data[-1] = msg_data[-1].split('{')[1].split('}')[0].replace(' ', '')
                    # multiple lines
                    else:
                        msg_data[-1] = ''
                        cnt_prev = cnt
                        CONTINUED = 1
                # single byte
                else:
                    msg_data[-1] = msg_data[-1].split()[0]
            else:
                msg_type.append("RESET")
                msg_data.append('')

        else:
            if '}' not in msg_all[n]:
                msg_data[-1] += msg_all[n].replace(' ','')
            else:
                msg_end[-1] = n
                cnt = cnt_prev
                CONTINUED = 0

        if n>0:
            if msg_data[-1] == msg_data[-2] and msg_port[-1] == msg_port[-2]:
                cnt = msg_SN[-1]-1
                del msg_start[-1], msg_end[-1], msg_SN[-1], msg_port[-1], msg_type[-1], msg_data[-1]

    if debug_mode:
        for n in range(len(msg_data)):
            print('%4s'%msg_SN[n], msg_port[n], msg_type[n], msg_data[n])

    return msg_start, msg_end, msg_SN, msg_port, msg_type, msg_data

def ShannonDM(msg_all):
    new_msg_all = []
    concat_len = 0
    for n in range(len(msg_all)):
        msg_items = msg_all[n].split('\t')
        if 'Hex Dump -> :' in msg_items[5]:
            hex_values = msg_items[5].split(':')[1].replace(' ', '')
            if concat_len == 0:
                new_msg_all.append(basic_format(msg_items, 'TX') + format('{ %s }')%split_hex(hex_values[:10]))

                if len(hex_values) > 10:
                    new_msg_all.append(basic_format(msg_items, 'RX') + hex_values[2:4])
                    Length = int(hex_values[8:10], 16) * 2
                    if len(hex_values[10:]) == Length:
                        new_msg_all.append(basic_format(msg_items, 'TX') + format('{ %s }')%split_hex(hex_values[10:]))
                    elif len(hex_values[10:]) < Length:
                        msg_concat = basic_format(msg_items, 'TX') + format('{ %s ')%split_hex(hex_values[10:])
                        concat_len = Length - len(hex_values[10:])
            elif concat_len > 0:
                msg_concat += format('%s ')%split_hex(hex_values)
                concat_len -= len(hex_values)
                if concat_len == 0:
                    new_msg_all.append(msg_concat + '}')
        elif 'SW1' in msg_items[5]:
            match = re.search(r'SW1: (0x[0-9A-Fa-f]{2}) SW2: (0x[0-9A-Fa-f]{2})$', msg_items[5])
            if match:
                sw1, sw2 = match.groups()
                new_msg_all.append(basic_format(msg_items, 'RX') + "{{ {} {} }}".format(sw1[2:].upper(), sw2[2:].upper()))

            # For testing
            # [USIM_0] Send TR status SW1:0x90, SW2:0x0
            # [USIM_0] SW1: 0x90, SW2: 0x0, INS: 0x70, P3: 0x0, Le: 0x2
            # [USIM_0] RetVal after Status: 1 RspApdu. SW1: 0x90
            # if ',' not in msg_items[5]:
            #     if 'RetVal' not in msg_items[5]:
            #         print(msg_items[5])

    for msg in new_msg_all:
        print(msg)

    return new_msg_all

def basic_format(msg_items, Type):
    msg_converted = '[0x19B7] ' # QCAT Tag
    msg_converted += msg_items[1] # CP_TIME
    msg_converted += ' SLOT_' + str(int(msg_items[5].split('USIM_')[1][0])+1) # SLOT_1 or SLOT_2
    msg_converted += f' Type = {Type} Data = ' # TX or RX
    return msg_converted

def split_hex(hex_values):
    return ' '.join([hex_values[i:i+2] for i in range(0, len(hex_values), 2)])




