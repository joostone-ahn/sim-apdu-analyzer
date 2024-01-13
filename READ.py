debug_mode = 0
import spec_ref

def process(ins, file_name, data, sum_read):

    file_name = file_name.replace('[', '').replace(']', '')
    sum_read.append([[data[1][2:-4]]])  # sum_read[n][0] = [file_data]

    if ins == 'B0':
        P2 = data[0][6:8].zfill(2)
        Le = data[0][8:10].zfill(2)
        sum_read[-1].append([P2,Le]) # sum_read[n][1] = [offset low, Number of bytes to be read]
        parsing = parser(file_name, data[1][2:-4], P2)
        if parsing: sum_read[-1][0].append(parsing) # sum_read[n][0] = [file_data, parsing]

    elif ins == 'B2':
        P1 = data[0][4:6].zfill(2)
        P2 = format(int(data[0][6:8], 16), 'b').zfill(8)  # ts102.221 table 11.11 Coding of P2
        if P2[-3:] == '100':
            sum_read[-1].append(P1) # sum_read[n][1] = record_num
        elif P2[-3:] == '010':
            sum_read[-1].append('Next')
        elif P2[-3:] == '011':
            sum_read[-1].append('Previous')
        Le = data[0][8:10].zfill(2)
        sum_read[-1].append(Le) # sum_read[n][2] = record length
        parsing = parser(file_name, data[1][2:-4], '00')
        if parsing: sum_read[-1][0].append(parsing) # sum_read[n][0] = [file_data, parsing]

    return sum_read

def parser(file_name, data, offset):
    parsing = ''

    if file_name == 'ICCID':
        for n in range(int(len(data)/2)):
            parsing += data[2*n+1]
            parsing += data[2*n]

    elif file_name == 'IMSI':
        data = data[2:2+int(data[:2],16)*2]
        for n in range(int(len(data)/2)):
            parsing += data[2*n+1]
            parsing += data[2*n]
        parsing = parsing[1:]

    elif file_name in ['IMPI', 'IMPU', 'P-CSCF']:
        if data[2:4] != 'FF': # IMPU [0x] not used
            byte_array = bytearray.fromhex(data[4:4+int(data[2:4],16)*2])
            parsing += byte_array.decode()

    elif file_name == 'ACC':
        parsing = '0x%s'%data[:2] + '%s '%data[2:]
        parsing += '(BIN ' + format(int(data[:2], 16), 'b').zfill(8)
        parsing += ' ' + format(int(data[2:], 16), 'b').zfill(8) +')'


    elif file_name in ['HPLMNwAcT','OPLMNwAcT','PLMNwAcT']:
        PLMNwAcT = []
        for n in range(int(len(data)/10)):
            if data[10*n:10*(n+1)] != 'FFFFFF0000':
                PLMNwAcT.append(data[10*n:10*(n+1)])
        if PLMNwAcT:
            cnt = 0
            for n in PLMNwAcT:
                cnt += 1
                if parsing != '': parsing += '\n'
                MCC = n[:-4][1] + n[:-4][0] + n[:-4][3]
                MNC = n[:-4][5] + n[:-4][4] + n[:-4][2]
                # if 'F' in MNC: MNC = MNC.replace('F',' ')
                if n[-4:] in AccessTech:
                    AcT = AccessTech[n[-4:]]
                else:
                    AcT = n[-4:]
                parsing += '[PLMN %3d]'%(cnt+int(int(offset, 16)/10*2))+' MCC %s'%MCC+' MNC %s'%MNC+' '
                parsing += '[AcT] %s'%AcT

    elif file_name == 'FPLMN':
        FPLMN = []
        for n in range(int(len(data)/6)):
            if data[6*n:6*(n+1)] != 'FFFFFF':
                FPLMN.append(data[6*n:6*(n+1)])
        if FPLMN:
            cnt = 0
            for n in FPLMN:
                cnt += 1
                if parsing != '': parsing += '\n'
                MCC = n[1] + n[0] + n[3]
                MNC = n[5] + n[4] + n[2]
                # if 'F' in MNC: MNC = MNC.replace('F',' ')
                parsing += '[FPLMN %2d]'%(cnt+int(int(offset, 16)/10*2)) + ' MCC %s' % MCC + ' MNC %s' % MNC

    elif file_name == 'MSISDN':
        byte_array = bytearray.fromhex(data[:32].split('FFFF')[0])
        data_len = int(data[32:34],16)
        Num = data[34:34+data_len*2][2:]
        parsing += byte_array.decode()+'/0x'+data[34:34+data_len*2][:2]+'/'
        for n in range(int(len(Num)/2)):
            parsing += Num[2*n+1]
            parsing += Num[2*n]
        # parsing += " (Alpha Id/TON and NPI/Dialling Num)"

    # EF_UST (31.102)
    elif file_name == 'UST':
        UST_binary = bin(int(data, 16))[2:]
        cnt = 0
        for i in range(0, len(UST_binary), 8):
            for bin_value in UST_binary[i:i + 8][::-1]:
                cnt += 1
                if cnt > len(spec_ref.UST_type):
                    break
                parsing += "[O]" if bin_value == '1' else "[X]"
                parsing += ' Service n%-3d' % cnt
                parsing += " %s" % spec_ref.UST_type[cnt] + '\n'

    # EF_IST (31.103)
    elif file_name == 'IST':
        IST_binary = bin(int(data, 16))[2:]
        if debug_mode: print(IST_binary)
        cnt = 0
        for i in range(0, len(IST_binary), 8):
            for bin_value in IST_binary[i:i + 8][::-1]:
                cnt += 1
                if cnt > len(spec_ref.IST_type):
                    break
                parsing += "[O]" if bin_value == '1' else "[X]"
                parsing += ' Service n%-3d' % cnt
                parsing += " %s" % spec_ref.IST_type[cnt] + '\n'

    elif file_name == 'EPSLOCI':
        parsing += "[Bytes  1-12] GUTI : "
        parsing += data[:24] + '\n'
        parsing += "[Bytes 13-17] Last visited registered TAI : "
        parsing += data[24:34] + '\n'
        parsing += "[Bytes    18] EPS update status : "
        parsing += data[34:36] + '\n'

    return parsing

AccessTech = dict()
AccessTech['4000'] = '4000 (LTE)'
AccessTech['4010'] = '4010 (LTE+CDMA)'
AccessTech['8000'] = '8000 (WCDMA)'
AccessTech['C000'] = 'C000 (LTE+WCDMA)'
AccessTech['00C0'] = '00C0 (GSM)'
AccessTech['40C0'] = '40C0 (LTE+GSM)'
AccessTech['80C0'] = '80C0 (WCDMA+GSM)'
AccessTech['C0C0'] = 'C0C0 (LTE+WCDMA+GSM)'