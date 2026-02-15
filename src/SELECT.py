import file_system
debug_mode = 0

def process(data, log_ch, log_ch_id):
    file_id = data[2]
    if file_id[0:2] == 'A0':
        log_ch[log_ch_id][0] = file_id
        log_ch[log_ch_id][1] = ''
        if len(log_ch[log_ch_id]) == 3:
            log_ch[log_ch_id][2] = log_ch[log_ch_id][0]
    else:
        if len(file_id) <= 4:
            if file_id in file_system.DF_name: # MF or DF(7F10)
                log_ch[log_ch_id][0] = file_id
                log_ch[log_ch_id][1] = ''
            elif file_id in file_system.EF_name['3F00']: # MF's child EF
                log_ch[log_ch_id][0] = '3F00'
                log_ch[log_ch_id][1] = file_id
            elif file_id == '7FFF':
                log_ch[log_ch_id][1] = ''
                if len(log_ch[log_ch_id]) == 3:
                    log_ch[log_ch_id][0] = log_ch[log_ch_id][2]
                else:
                    if data[-1][-4:] == '9000' or data[-1][-4:-2] == '91':
                        if 'A00000008710' in data[-1]:
                            log_ch[log_ch_id][0] = 'A00000008710' + data[-1].split('A00000008710')[1][:20]
                    else:
                        log_ch[log_ch_id][0] = '' # 'current DF is NOT determined'
            # LSI Chipset example: SELECT 5F40(DF_5GS) wo/7FFF
            elif file_id[:2] == '5F':
                file_id = '7FFF'+file_id
                log_ch[log_ch_id][0] = file_id
                log_ch[log_ch_id][1] = ''
            # LGU+ Custom File
            elif file_id == '2F30':
                log_ch[log_ch_id][0] = '3F00'
                log_ch[log_ch_id][1] = file_id
            else:
                log_ch[log_ch_id][1] = file_id
        else: # len(file_id) > 4
            if file_id[0:4] == '7F10':
                if file_id[4:6] == '5F':
                    log_ch[log_ch_id][0] = file_id[0:8]
                    if len(file_id) > 8:
                        log_ch[log_ch_id][1] = file_id[8:]
                    else:
                        log_ch[log_ch_id][1] = ''
                else:
                    log_ch[log_ch_id][0] = file_id[0:4]
                    log_ch[log_ch_id][1] = file_id[4:]
            elif file_id[0:4] == '7FFF':
                if file_id[4:6] == '5F':
                    log_ch[log_ch_id][0] = file_id[0:8]
                    if len(file_id) > 8:
                        log_ch[log_ch_id][1] = file_id[8:]
                    else:
                        log_ch[log_ch_id][1] = ''
                else: # current ADF
                    log_ch[log_ch_id][1] = file_id[4:8]
                    if len(log_ch[log_ch_id]) == 3:
                        log_ch[log_ch_id][0] = log_ch[log_ch_id][2]
                    else:
                        if log_ch[log_ch_id][0] == '3F00' or '7F10' in log_ch[log_ch_id][0] :
                            log_ch[log_ch_id][0] = 'A0000000871002'
                            # MF and DF TELECOM use same logical channel with USIM ADF
                        elif '7FFF5F' in log_ch[log_ch_id][0]:
                            log_ch[log_ch_id][0] = 'A0000000871002'
                            # child DF not defined in ISIM ADF, select USIM ADF by default
                        else:
                            if log_ch[log_ch_id][1] in file_system.USIM_EF_list:
                                if log_ch[log_ch_id][1] in file_system.ISIM_EF_list:
                                    log_ch[log_ch_id][0] = '' # current DF is NOT determined
                                else: # USIM ADF decided
                                    log_ch[log_ch_id][0] = 'A0000000871002'
                            else:
                                if log_ch[log_ch_id][1] in file_system.ISIM_EF_list: # ISIM ADF decided
                                    log_ch[log_ch_id][0] = 'A0000000871004'
                                else:
                                    log_ch[log_ch_id][0] = '' # current DF is NOT determined

    if log_ch[log_ch_id][0][0:2] == 'A0':
        if len(log_ch[log_ch_id]) < 3:
            log_ch[log_ch_id].append(log_ch[log_ch_id][0])

    file_name, error = file_system.process(log_ch[log_ch_id][0], log_ch[log_ch_id][1], file_id)

    if debug_mode == 1:
        print('-'*200)
        print('  prot_data    :', data[0][0:2], data[2])
        print('  log_ch       :', log_ch)
        print('  DF_file_id   :', log_ch[log_ch_id][0])
        print('  EF_file_id   :', log_ch[log_ch_id][1])
        print('  file_name    :', file_name)
        print('  error        :', error)
        print('-'*200)

    return log_ch, file_name, error
