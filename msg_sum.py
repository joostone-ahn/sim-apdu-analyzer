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
        file_name, sw, info, error  = '', '', '', ''

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
                if 'SELECT (X)' in sum_rst[-1] or 'SELECT (*)' in sum_rst[-1]:
                    log_ch[log_ch_id][1] = ''

            # log_ch
            ins = prot_data[m][0][2:4]
            if debug_mode: print('INS byte       :', ins)

            # Unknown INS
            if ins not in command.cmd_name:
                cmd = f"INS: 0x{ins}"
                info = f"Unknown INS"

            # Known INS
            else:
                cmd = command.cmd_name[ins]

                # sw (Status Word)
                if prot_type[m][-1] == 'RX': # len(prot_data[m])>=2
                    if len(prot_data[m][-1]) >= 4:
                        sw = prot_data[m][-1][-4:]
                    else:
                        sw = None
                        cmd += ' (*)'
                        info = 'Status Words not received'
                else:
                    sw = None
                    cmd += ' (*)'
                    info = 'RX data not received'
                if debug_mode: print('status word    :', sw)

                # status word included
                if sw is not None:
                    # File not found, Record not found, unsuccessful search, security status not satisfied
                    if sw in spec_ref.RAPDU_list:
                        cmd += ' (X)'
                        error += f"*SW'{sw}': {spec_ref.RAPDU_list[sw]}"
                    # Error status word
                    elif sw != '9000' and sw[:2] != '91':
                        # except for GET IDENTITY, GET DATA, STATUS, MANAGE CHANNEL, UNBLOCK/VERIFY PIN, TERMINCAL CAPABILITY
                        if ins not in ['78', 'CA', 'F2', '70', '2C', '20', 'AA'] and cmd != 'Unknown':
                            info = f"ERROR (SW'{sw}')"
                            if sw in spec_ref.Error_RAPDU_list:
                                error += f"*SW'{sw}': {spec_ref.Error_RAPDU_list[sw]}"
                            else:
                                error += f"*SW'{sw}': please check ETSI ts102.221 10.2.Response APDU"
                        # else:
                        #     info = f"SW'{sw}'" # in order to check status words of above INS sets

                    # SELECT
                    if ins == 'A4':
                        SELECT_rst = SELECT.process(prot_data[m], log_ch, log_ch_id)
                        log_ch = SELECT_rst[0]
                        file_name = SELECT_rst[1]
                        if error and SELECT_rst[2]:
                            error += '\n' + ' '*len(f"[{m+1}] ")
                        error += SELECT_rst[2]
                        last_file_id = prot_data[m][2]

                    # SFI (Short file id)
                    elif ins in short_file_id.cmd_SFI_list:
                        SFI_used, SFI = short_file_id.category(prot_data[m][0])
                        if SFI_used:
                            short_file_id_rst = short_file_id.process(log_ch, log_ch_id, SFI)
                            log_ch = short_file_id_rst[0]
                            file_name = short_file_id_rst[1]
                            if error and short_file_id_rst[2]:
                                error += '\n' + ' '*len(f"[{m+1}] ")
                            error += short_file_id_rst[2]
                            if '(X)' not in cmd: cmd += f' (SFI: 0x{SFI})'
                            else: cmd = cmd.replace(' (X)','') + f' (SFI: 0x{SFI}) (X)'

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
                        if debug_mode: print('AUTH check     :',prot_data[m])
                        if debug_mode: print('log_ch DF name :',log_ch[log_ch_id][0])
                        file_name = file_system.process(log_ch[log_ch_id][0], '', last_file_id)[0]
                        if 'ADF' in file_name:
                            info = file_name.replace(']','').replace('[','')
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
                                info = 'Re-Sync'
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
                        if debug_mode: print('T/R check      :', prot_data[m])
                        if '810301' in prot_data[m][2]:
                            TR_data = prot_data[m][2].split('810301')[1][:4]
                            if TR_data[:2] in spec_ref.Proactive_type:
                                TR_type = spec_ref.Proactive_type[TR_data[:2]]
                                cmd += ' (%s)'%TR_type
                                TR_rst = prot_data[m][2].split('8281')[1][4:6]
                                if TR_rst in spec_ref.TR_RST_list:
                                    info = f"ERROR (result'0x{TR_rst}')"
                                    error = f"*result'0x{TR_rst}': {spec_ref.TR_RST_list[TR_rst]}"

                    # ENVELOPE
                    elif ins == 'C2':
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

            # sum_rst
            sum_rst.append(num + '  ' + time + '  ' +'%-37s'%cmd + ' |  ')
            sum_cmd.append(cmd)
            if file_name:
                if 'ERROR' not in info: sum_rst[-1] += file_name
            if info: sum_rst[-1] += info
            if debug_mode: print('sum_rst        :', sum_rst[-1])

            # sum_error
            sum_error.append(error)
            if debug_mode: print('error          :', sum_error[-1])

            # sum_read
            if sw is None:
                sum_read.append(['', ''])
            else:
                # READ BINARY or READ RECORD
                if ins == 'B0' or ins == 'B2':
                    if sw == '9000' or sw[:2] == '91':
                        if SFI_used == False:
                            file_name = file_system.process(log_ch[log_ch_id][0], log_ch[log_ch_id][1], last_file_id)[0]
                        sum_read = READ.process(ins, file_name, prot_data[m], sum_read)
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
                elif ins == 'D6' and len(prot_data[m]) ==4:
                    if sw == '9000' or sw[:2] == '91':
                        update_data = []
                        update_data.append([prot_data[m][2]])
                        update_data.append([prot_data[m][0][-4:-2], prot_data[m][0][-2:]])
                        sum_read.append(update_data)
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

        if debug_mode: print("=" * 200)

    return sum_rst, sum_log_ch, sum_log_ch_id, sum_cmd, sum_read, sum_error