import command
import SELECT
import READ
import spec_ref
import file_system
import short_file_id
import re

debug_mode = 0

def rst(input):
    msg_all, prot_start, prot_type, prot_data = input
    sum_rst, sum_log_ch, sum_log_ch_id, sum_cmd, sum_read, sum_error = [], [], [], [], [], []
    log_ch = [['','']] # log_ch[n] = [current DF, current EF]

    file_list = []

    last_file_id = ''
    for m in range(len(prot_start)):
        if debug_mode: print('sum_num        : [%d]'%(m+1))
        if debug_mode: print('start_line     : %d'% prot_start[m][0])
        if debug_mode: print('prot_data      :', prot_data[m])

        num_max = len(str(len(prot_start)))+1 # including '['
        num = ' '*(num_max-len(str(m+1))) + '[' + str(m+1) + ']'

        # Time
        match = re.search(r'\d{2}:\d{2}:\d{2}.\d{3}', msg_all[prot_start[m][0]])
        if match:
            time = match.group()
        else:
            time = 'TIME ERROR'
            time = '%-12s'%time

        type = prot_type[m][0]

        # RESET, ATR
        if type != 'TX' and type != 'RX':
            sum_rst.append(num + '  ' + time + '  ' +'%-37s'%type + ' |  ')
            sum_log_ch.append(['','']) # sum_log_ch[n] = [current DF, current EF]
            sum_log_ch_id.append('')
            sum_cmd.append('')
            sum_read.append(['','']) # sum_read[n] = [file_name, file_data]
            sum_error.append('')

        # 'TX' or 'RX'
        else:
            if prot_type[m][-1] == 'RX':
                if len(prot_data[m][-1]) >= 4:
                    sw = prot_data[m][-1][-4:]
                else:
                    sw = None # Incomplete APDU
            else:
                sw = None # Incomplete APDU
            if debug_mode: print('status word    :', sw)

            # sum_log_ch_id
            cla = prot_data[m][0][:2]
            cla_bin = format(int(cla,16),'b').zfill(8)
            if cla_bin[0:2] == '01' or cla_bin[0:2] == '11': # '0100' ETSI ts102.221 Table 10.4a extended logical channels
                log_ch_id = 4 + int(cla_bin[4:],2)  # logical channel number from 4 to 19
            else:
                log_ch_id = int(cla_bin[6:],2) # logical channel number from 0 to 3
            if log_ch_id > len(log_ch) - 1:
                for n in range(log_ch_id - len(log_ch) + 1):
                    log_ch.append(['',''])
            sum_log_ch_id.append(log_ch_id)
            if debug_mode: print('CLA byte       :', cla)
            if debug_mode: print('log_ch_id      :', sum_log_ch_id[-1])

            if sum_rst:
                if 'SELECT (X)' in sum_rst[-1]:
                    log_ch[log_ch_id][1] = ''

            # log_ch
            file_name, info, error = '', '', ''
            ins = prot_data[m][0][2:4]
            if debug_mode: print('INS byte       :', ins)

            # Unknown INS
            if ins not in command.cmd_name:
                cmd = "Unknown"
                info = f"*INS: 0x{ins}"

            # Known INS
            else:
                cmd = command.cmd_name[ins]
                if sw is None:
                    error = 'Incomplete APDU'
                    if ins == 'A4':
                        info = '*N/A'
                else:
                    # SELECT
                    if ins == 'A4':
                        if len(prot_data[m])>2:
                            log_ch, file_name, error = SELECT.process(prot_data[m], log_ch, log_ch_id)
                            last_file_id = prot_data[m][2]
                        else:
                            info = '*N/A'
                            error = 'Incomplete APDU'

                    # SFI (Short file id)
                    elif ins in short_file_id.cmd_SFI_list:
                        SFI_used, SFI = short_file_id.category(prot_data[m][0])
                        if SFI_used:
                            log_ch, file_name, error = short_file_id.process(log_ch, log_ch_id, SFI)
                            cmd += ' (SFI: 0x%s)' % SFI

                    # STATUS
                    elif ins == 'F2':
                        if 'A000000087100' in prot_data[m][1]: #USIM or ISIM
                            AID_len = int(prot_data[m][1][4:6],16)*2
                            AID = prot_data[m][1][6:6+AID_len]
                            log_ch[log_ch_id][0] = AID
                            if len(log_ch[log_ch_id]) < 3:
                                log_ch[log_ch_id].append(log_ch[log_ch_id][0])

                    # AUTHENTICATE
                    elif ins == '88' or ins == '89':
                        info = ''
                        if debug_mode: print('AUTH check     :',prot_data[m])
                        if debug_mode: print('log_ch DF name :',log_ch[log_ch_id][0])
                        file_name, error = file_system.process(log_ch[log_ch_id][0], '', last_file_id)
                        if 'ADF' in file_name: cmd += ' (%s)'%file_name.split(' ')[1].replace(']','')
                        file_name = ''
                        RAND_len = int(prot_data[m][2][:2],16)
                        RAND = prot_data[m][2][2:2+RAND_len*2]
                        AUTN_len = int(prot_data[m][2][2+RAND_len*2:4+RAND_len*2],16)
                        AUTN = prot_data[m][2][4+RAND_len*2:4+RAND_len*2+AUTN_len*2]
                        if len(prot_data[m]) > 4:
                            SIM_resp_type = prot_data[m][-1][2:4]
                            if SIM_resp_type == 'DB':
                                RES = prot_data[m][-1][6:22]
                                AUTS = ''
                            elif SIM_resp_type == 'DC':
                                RES = ''
                                AUTS = prot_data[m][-1][6:34]
                                info = '*Re-Sync'
                            else:
                                RES = ''
                                AUTS = ''
                        else:
                            RES = ''
                            AUTS = ''
                        if debug_mode:
                            print('%7s' % 'RAND :', RAND)
                            print('%7s' % 'AUTN :', AUTN)
                            print('%7s' % 'RES :', RES)
                            print('%7s' % 'AUTS :', AUTS)

                    # MANAGE CHANNEL
                    elif ins == '70':
                        info = ''
                        if prot_data[m][0][4:6] == '80':
                            cmd += ' (CLOSE)'
                            info = f'Logical channel number: {int(prot_data[m][0][6:8],16)}'
                        elif prot_data[m][0][4:6] == '00':
                            if len(prot_data[m][1]) == 8:
                                if prot_data[m][1][-4:] == '9000' or prot_data[m][1][-4:-2] == '91':
                                    if prot_data[m][0][6:8] == '00':
                                        cmd += ' (OPEN)'
                                        info = f'Logical channel number: {int(prot_data[m][1][2:4],16)}'
                                    else:
                                        cmd += ' (OPEN)'
                                        info = f'Logical channel number: {int(prot_data[m][0][6:8],16)}'

                    # FETCH
                    elif ins == '12':
                        info = ''
                        if debug_mode: print('FETCH check    :',prot_data[m])
                        if '810301' in prot_data[m][1]:
                            FETCH_data = prot_data[m][1].split('810301')[1][:4]
                            if FETCH_data[:2] in spec_ref.Proactive_type:
                                FETCH_type = spec_ref.Proactive_type[FETCH_data[:2]]
                                cmd += ' (%s)' % FETCH_type
                                if FETCH_type == 'REFRESH':
                                    if FETCH_data[2:] in spec_ref.REFRESH_type:
                                        info = spec_ref.REFRESH_type[FETCH_data[2:]]
                                elif FETCH_type == 'POLL INTERVAL':
                                    dec_value = int(prot_data[m][1][-6:-4],16)
                                    info = str(dec_value) + 'sec'
                                elif FETCH_type == 'SETUP EVENT LIST':
                                    if '818299' in prot_data[m][1]: # 81(UICC), 82(terminal), 99(event list tag)
                                        if prot_data[m][1].split('818299')[1][:2] != '00':
                                            event_len = int(prot_data[m][1].split('818299')[1][:2], 16) * 2 # Byte 개수라 2배
                                            event_list_byte = prot_data[m][1].split('818299')[1][2:2+event_len]
                                            event_list = [event_list_byte[i:i+2] for i in range(0, len(event_list_byte), 2)]
                                            for event in event_list:
                                                info += spec_ref.Event_list[event] + ', '
                                            info = info[:-2]

                    # TERMINAL RESPONSE
                    elif ins == '14':
                        info = ''
                        if debug_mode: print('T/R check      :', prot_data[m])
                        if '810301' in prot_data[m][2]:
                            TR_data = prot_data[m][2].split('810301')[1][:4]
                            if TR_data[:2] in spec_ref.Proactive_type:
                                TR_type = spec_ref.Proactive_type[TR_data[:2]]
                                cmd += ' (%s)'%TR_type
                                TR_rst = prot_data[m][2].split('8281')[1][4:6]
                                if TR_rst in spec_ref.TR_RST_list:
                                    info = f'*0x{TR_rst}'
                                    info += f'({spec_ref.TR_RST_list[TR_rst]})'

                    # ENVELOPE
                    elif ins == 'C2':
                        info = ''
                        if debug_mode: print('ENVELOPE check :', prot_data[m])
                        if prot_data[m][2][:2] in spec_ref.Envelope_type:
                            ENV_type = spec_ref.Envelope_type[prot_data[m][2][:2]]
                            cmd += ' (%s)' % ENV_type
                            if ENV_type == 'Event Download':
                                if prot_data[m][2][8:10] in spec_ref.Event_list:
                                    info = spec_ref.Event_list[prot_data[m][2][8:10]]

            if debug_mode: print('command name   :', cmd)
            if debug_mode: print('file name      :', file_name)
            if debug_mode: print('information    :', info)
            if debug_mode: print('log_ch         :', log_ch)

            # sum_log_ch
            sum_log_ch.append(log_ch[log_ch_id][0:2])
            if debug_mode: print('sum_log_ch     :', sum_log_ch[-1])

            # status word NOT included
            if sw is None:
                cmd += ' (X)'
                error = '*No status word'
            # status word included
            else:
                # Error status word
                if sw != '9000' and sw[:2] != '91' and ins[0] != '2':
                    cmd += ' (X)'
                # Normal status word
                else:
                    # Incomplete APDU
                    if prot_data[m][1][:2] != ins:
                        # except for STATUS, MANAGE CHANNEL, UNBLOCK/VERIFY PIN
                        if ins not in ['F2', '70', '2C', '20', 'F2']:
                            cmd += ' (X)'
                            sw = None
                            error = '*Incomplete APDU'

            # sum_rst
            sum_rst.append(num + '  ' + time + '  ' +'%-37s'%cmd + ' |  ')
            sum_cmd.append(cmd)
            if file_name: sum_rst[-1] += file_name
            if info: sum_rst[-1] += info
            if debug_mode: print('sum_rst        :', sum_rst[-1])

            # sum_read
            if sw is None:
                sum_read.append(['', ''])
            else:
                # READ BINARY or READ RECORD
                if ins == 'B0' or ins == 'B2':
                    if sw == '9000' or sw[:2] == '91':
                        if SFI_used == False : file_name, error = file_system.process(log_ch[log_ch_id][0], log_ch[log_ch_id][1], last_file_id)
                        sum_read = READ.process(ins, file_name, prot_data[m], sum_read)
                        # print(sum_read[-1])
                        # print(log_ch[log_ch_id])
                        # print(SFI_used)
                        # print("="*200)

                        # file_name, adf_id, file_id, SFI, type(LF or TF), Record_Num, Len, contents, parsing
                        file_item = []
                        file_item.append(file_name)
                        file_item.append(sum_log_ch[0])
                        file_item.append(sum_log_ch[1])
                        if SFI_used:
                            file_item.append(SFI)
                        else:
                            file_item.append('')
                        if ins == 'B0':
                            file_item.append('TF')
                        elif ins == 'B2':
                            file_item.append('LF')

                    else:
                        sum_read.append(['',''])

                # UPDATE BINARY
                # 23.09.19 READ BINARY와 동일 포맷 (EPSLOCI, EPSNSC 타겟)
                elif ins == 'D6':
                    if sw == '9000' or sw[:2] == '91':
                        update_data = []
                        update_data.append([prot_data[m][2]])
                        update_data.append([prot_data[m][0][-4:-2], prot_data[m][0][-2:]])
                        sum_read.append(update_data)
                        # print(sum_read[-1])
                        # print(log_ch[log_ch_id])
                        # print(SFI_used)
                    else:
                        sum_read.append(['',''])

                # AUTHENTICATE
                elif ins == '88' or ins == '89':
                    sum_read.append([list()])
                    sum_read[-1][0].append('%19s'%'RAND : '+ '%s' % RAND)
                    sum_read[-1][0].append('%19s'%'AUTN : '+ '%s' % AUTN)
                    if RES : sum_read[-1][0].append('%19s'%'RES : '+ '%s' % RES)
                    if AUTS : sum_read[-1][0].append('%19s'%'AUTS : '+ '%s' % AUTS)
                    # print(sum_read[-1])

                    if debug_mode:
                        if 'USIM' in sum_rst[-1]:
                            print('='*60)
                            print(sum_rst[-1])
                            print('='*60)
                            print('%10s' % 'RAND :', RAND)
                            print('%10s' % 'AUTN :', AUTN)
                            print('%10s' % 'RES :', RES)
                            print('%10s' % 'AUTS :', AUTS)
                            print('='*60)
                            print('')
                else:
                    sum_read.append(['',''])

            if debug_mode: print('sum_read       :', sum_read[-1])

            # sum_error (R-APDU TBD)
            if sw == '6A82': # ETSI ts102.221 Table 10.14
                if error: error = '*File not found (SW:6A82) ' + error
                else: error = '*File not found (SW:6A82)'
            elif sw == '6282': # ETSI ts102.221 Table 10.9
                if error: error = '*unsuccessful search (SW:6282)' + error
                else: error = '*unsuccessful search (SW:6282)'
            sum_error.append(error)
            if debug_mode: print('error          :', sum_error[-1])

            # if debug_mode == 2:
            #     for n in log_ch:
            #         print(n)

        if debug_mode: print("=" * 200)

    return sum_rst, sum_log_ch, sum_log_ch_id, sum_cmd, sum_read, sum_error