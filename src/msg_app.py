import file_system
import spec_ref
debug_mode = 0

def rst(input, read, error, item_num):
    prot_type, sum_cmd, sum_log_ch, sum_log_ch_id = input

    log_ch = sum_log_ch[item_num]
    log_ch_id = sum_log_ch_id[item_num]
    cmd = sum_cmd[item_num]

    current_DF = log_ch[0]
    current_EF = log_ch[1]
    if current_DF[:14] in file_system.DF_name: current_DF = current_DF[:14]
    # DF_name['A0000000871002'] = 'ADF USIM' 14자리만 인식
    # DF_name['A0000000871004'] = 'ADF ISIM' 14자리만 인식

    if debug_mode:
        print("%10s"%"prot_type:", prot_type[item_num])
        print("%10s"%"cmd:",cmd)
        if log_ch: print("%10s"%"log_ch:",log_ch)
        if log_ch_id: print("%10s"%"log_ch_id:",log_ch_id)
        print("%10s"%"read:",read[item_num])

    app_rst = []
    if prot_type[item_num][0] == 'TX':
        rst_ind = '[%s]'%str(item_num+1)
        void = ' '*len(rst_ind)
        app_rst.append(rst_ind + ' Logical Channel : %s' % str(log_ch_id))
        if log_ch_id >= 4: app_rst[-1] += ' [Extended]'

        app_rst.append(void+' Current DF File : %s'%log_ch[0])
        if current_DF:
            if current_DF in file_system.DF_name:
                app_rst[-1] += ' [%s]'%file_system.DF_name[current_DF]

        app_rst.append(void+' Current EF File : %s'%log_ch[1])
        if current_DF and current_EF:
            if current_DF in file_system.DF_name:
                if current_DF in file_system.EF_name:
                    if current_EF in file_system.EF_name[current_DF]:
                        app_rst[-1] += ' [%s]'%file_system.EF_name[current_DF][current_EF]

        app_rst.append(void+' Current Command : %s' % cmd.replace('(X)',''))

        if 'AUTHENTICATE' in cmd:
            app_rst.append(void + ' ' + '-' *(80-len(void)-1))
            for n in read[item_num][0]:
                app_rst.append(void + n)

        if 'READ' in cmd and read[item_num][0] != '':
            app_rst.append(void + ' ' + '-' *(80-len(void)-1))
            # READ RECORD
            if 'RECORD' in cmd and len(read[item_num]) == 3:
                app_rst.append(void+'%-17s'%' Record Number'+': 0x%s'%read[item_num][1])
                app_rst.append(void+'%-17s'%' Record Length'+': 0x%s'%read[item_num][2])
                app_rst[-1] +=' (%d Bytes)'%int(read[item_num][2],16)
                app_rst.append(void+'%-17s'%' Record Contents'+': ')
                app_rst = split_contents(read[item_num][0][0], app_rst)
                # Parsing data included
                if len(read[item_num][0])>1:
                    app_rst.append(void + ' ' + '-' * (80 - len(void) - 1))
                    app_rst.append(void + ' ')
                    app_rst = split_parsing(read[item_num][0][1], app_rst)

            # READ BINARY
            elif 'BINARY' in cmd and len(read[item_num]) == 2:
                app_rst.append(void+'%-17s'%' Read Offset'+': 0x%s'%read[item_num][1][0])
                app_rst.append(void+'%-17s'%' Read Length'+': 0x%s'%read[item_num][1][1])
                app_rst[-1] += ' (%d Bytes)'%int(read[item_num][1][1],16)
                app_rst.append(void+'%-17s'%' Read Contents'+': ')
                app_rst = split_contents(read[item_num][0][0], app_rst)
                # Parsing data included
                if len(read[item_num][0])>1:
                    app_rst.append(void + ' ' + '-' * (80 - len(void) - 1))
                    app_rst.append(void + ' ')
                    app_rst = split_parsing(read[item_num][0][1], app_rst)

        if 'UPDATE' in cmd and read[item_num][0] != '':
            app_rst.append(void + ' ' + '-' *(80-len(void)-1))

            # UPDATE BINARY
            if 'BINARY' in cmd and len(read[item_num]) == 2:
                app_rst.append(void+'%-17s'%' Update Offset'+': 0x%s'%read[item_num][1][0])
                app_rst.append(void+'%-17s'%' Update Length'+': 0x%s'%read[item_num][1][1])
                app_rst[-1] += ' (%d Bytes)'%int(read[item_num][1][1],16)
                app_rst.append(void+'%-17s'%' Update Contents'+': ')
                app_rst = split_contents(read[item_num][0][0], app_rst)

        if read[item_num][0] != '':
            if 'UPDATE' in cmd or 'READ' in cmd:
                # EF_EPSLOCI
                if current_EF == '6FE3':
                    app_rst.append(void + ' ' + '-' * (80 - len(void) - 1))
                    app_rst.append(void + " [Bytes  1-12] GUTI : ")
                    app_rst[-1] += read[item_num][0][0][:24]
                    app_rst.append(void + " [Bytes 13-17] Last visited registered TAI : ")
                    app_rst[-1] += read[item_num][0][0][24:34]
                    app_rst.append(void + " [Bytes    18] EPS update status : ")
                    app_rst[-1] += read[item_num][0][0][34:36]

        if error[item_num]:
            app_rst.append(void + ' ' + '-' *(80-len(void)-1))
            app_rst.append(void + ' ' + error[item_num])

    if debug_mode:
        print("="*50)
        for n in app_rst:
            print(n)
        print()

    return app_rst

def split_contents(input, app_rst):
    void = ' '*len(app_rst[-1])
    cnt = 0
    for m in range(len(list(input))):
        if m//32 > 0 and m % 32 == 0:
            app_rst.append(void)
        if m % 2 == 0:
            app_rst[-1] += list(input)[m]
            cnt += 1
        else:
            app_rst[-1] += list(input)[m] + ' '
            cnt += 2
    return app_rst

def split_parsing(input, app_rst):
    void = ' '*len(app_rst[-1])
    if '\n' in input:
        input_list = input.split('\n')
        for n in range(len(input_list)):
            if n>0: app_rst.append(void)
            app_rst[-1] += input_list[n]
    else:
        app_rst[-1] += input
    return app_rst
