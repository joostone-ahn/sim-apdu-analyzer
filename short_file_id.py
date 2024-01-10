cmd_SFI_list = ['B0', 'D6', 'B2', 'DC', 'A2', '32', 'CB', 'DB']  # command using SFI
import file_system
debug_mode = 0

def category(prot_data):
    SFI_used = False
    SFI = ''
    ins = prot_data[2:4]

    # READ/UPDATE BINARY, INCREASE
    if ins == 'B0' or ins == 'D6' or ins == '32':
        P1 = format(int(prot_data[4:6], 16), 'b').zfill(8)
        if P1[0] == '0':
            SFI_used = False
        elif P1[0:3].zfill(3) == '100':
            SFI_used = True
            SFI = format(int(P1[3:], 2), '02X')

    # READ/UPDATE/SEARCH RECORD
    elif ins == 'B2' or ins == 'DC' or ins == 'A2':
        P2 = format(int(prot_data[6:8], 16), 'b').zfill(8)
        if P2[:5].zfill(5) == '00000':
            SFI_used = False
        else:
            SFI_used = True
            SFI = format(int(P2[:5], 2), '02X')

    # RETRIEVE/SET DATA
    elif ins == 'CB' or ins == 'DB':
        P2 = format(int(prot_data[6:8], 16), 'b').zfill(8)
        if P2[3:].zfill(5) == '00000':
            SFI_used = False
        else:
            SFI_used = True
            SFI = format(int(P2[3:], 2), '02X')

    if debug_mode == 1:
        if SFI_used:
            print('  prot_data    :', prot_data)
            print('  cmd_SFI      :', SFI)
            print('  SFI_used     :', SFI_used)
            print()

    return SFI_used, SFI


def process(log_ch, log_ch_id, SFI):
    error = ''
    current_DF = log_ch[log_ch_id][0]

    # current DF is NOT determined
    if current_DF == '':
        file_name = "*Unknown"
        file_id = "0x%s(SFI)" % SFI + ' *Unknown'
        error = '*current DF is NOT determined'
        # log_ch[log_ch_id][1] = file_id

    # current DF is determined
    else:
        if current_DF[:14] in SFI_file_id: current_DF = current_DF[:14]
        # DF_name['A0000000871002'] = 'ADF USIM' 14자리만 인식
        # DF_name['A0000000871004'] = 'ADF ISIM' 14자리만 인식

        if current_DF in SFI_file_id:
            if SFI in SFI_file_id[current_DF]:
                file_id = SFI_file_id[current_DF][SFI]
                file_name, error = file_system.process(log_ch[log_ch_id][0], file_id, file_id)
                log_ch[log_ch_id][1] = file_id

            # Unknown SFI in current DF
            else:
                file_name = "*Unknown"
                file_id = "0x%s(SFI)" % SFI + ' *Unknown'
                log_ch[log_ch_id][1] = file_id
                error = '*Unknown SFI in current DF'
        else:
            file_name = "*Unknown"
            file_id = "0x%s(SFI)" % SFI + ' *Unknown'
            log_ch[log_ch_id][1] = file_id
            error = '*Unknown SFI in current DF'

    if debug_mode == 2:
        print('current DF  :', current_DF)
        print('SFI         :', SFI)
        print('file_id     :', file_id)
        print('file_name   :', file_name)
        print('log_ch      :', log_ch[log_ch_id])
        print('error       :', error)
        print('')

    return log_ch, file_name, error

SFI_file_id = {
    # ETSI ts102.221 v16.00.00 Annex.H
    '3F00': {
        '02': '2FE2',
        '05': '2F05',
        '06': '2F06',
        '07': '2F07',
        '08': '2F08',
        '1E': '2F00'
    },
    # 3GPP ts31.102 v17(ha0) Annex.H
    'A0000000871002': {
        '01': '6FB7',
        '02': '6F05',
        '03': '6FAD',
        '04': '6F38',
        '05': '6F56',
        '06': '6F78',
        '07': '6F07',
        '08': '6F08',
        '09': '6F09',
        '0A': '6F60',
        '0B': '6F7E',
        '0C': '6F73',
        '0D': '6F7B',
        '0E': '6F48',
        '0F': '6F5B',
        '10': '6F5C',
        '11': '6F61',
        '12': '6F31',
        '13': '6F62',
        '14': '6F80',
        '15': '6F81',
        '16': '6F4F',
        '17': '6F06',
        '19': '6FC5',
        '1A': '6FC6',
        '1B': '6FCD',
        '1C': '6F39',
        '1D': '6FD9',
        '1E': '6FE3',
        '18': '6FE4'
    },
    '7FFF5F3B': {
        '01': '4F20',
        '02': '4F52'
    },
    '7FFF5F40': {
        '01': '4F41',
        '02': '4F42',
        '03': '4F43',
        '04': '4F44',
        '05': '4F45',
        '06': '4F46',
        '07': '4F47',
        '08': '4F48',
        '09': '4F49',
        '0A': '4F4A',
        '0B': '4F4B'
    },
    '7FFF5F50': {
        '01': '4F81',
        '02': '4F82',
        '03': '4F83',
        '04': '4F84',
        '05': '4F85',
        '06': '4F86'
    },
    '7FFF5F90': {
        '01': '4F01',
        '02': '4F02',
        '03': '4F03',
        '04': '4F04',
        '05': '4F05',
        '06': '4F06',
        '07': '4F07',
        '08': '4F08',
        '09': '4F09',
        '10': '4F10',
        '11': '4F11',
        '12': '4F12',
        '13': '4F13',
        '14': '4F14'
    },
    '7FFF5FA0': {
        '01': '4F01'
    },
    '7F105F3D': {
        '01': '4F01',
        '02': '4F02'
    },
    '7F105F3E': {
        '01': '4F01',
        '02': '4F02',
        '06': '4F03',
        '07': '4F04'
    },
    '7FFF5FC0': {
        '01': '4F01',
        '02': '4F02',
        '03': '4F03',
        '04': '4F04',
        '05': '4F05',
        '06': '4F06',
        '07': '4F07',
        '08': '4F08',
        '09': '4F09',
        '0A': '4F0A',
        '0B': '4F0B',
        '0C': '4F0C',
        '0D': '4F0D',
        '0E': '4F0E',
        '0F': '4F0F',
        '10': '4F10',
        '11': '4F11',
        '15': '4F15',
        '16': '4F16'
    },
    # 3GPP ts31.103 v17(h00) Annex.D
    'A0000000871004': {
        '02': '6F02',
        '05': '6F03',
        '04': '6F04',
        '03': '6FAD',
        '06': '6F06',
        '07': '6F07'
    },
    '7F105F3A': {
        '01': '4F3A', # ADN
        '02': '4F09', # PBC
        '03': '4F26', # GRP
        '04': '4F11', # ANRA
        '05': '4F13', # ANRB
        '06': '4F15', # ANRC
        '07': '4F19', # SNE
        '12': '4F21', # UID
        '08': '4F4A', # EXT1
        '14': '4F4B', # AAS
        '15': '4F4C', # GAS
        '09': '4F50', # EMAIL
        '16': '4F54',  # PURI
        '0A': '4F3B',  # ADN1
        '0B': '4F0A',  # PBC1
        '0C': '4F25',  # GRP1
        '0D': '4F12',  # ANRA1
        '0E': '4F14',  # ANRB1
        '0F': '4F16',  # ANRC1
        '10': '4F1A',  # SNE1
        '13': '4F20',  # UID1
        '11': '4F51',  # EMAIL1
        '17': '4F55'  # PURI1
    },
    '7FFF5F3A': {
        '01': '4F3A',  # ADN
        '02': '4F09',  # PBC
        '03': '4F26',  # GRP
        '04': '4F11',  # ANRA
        '05': '4F13',  # ANRB
        '06': '4F15',  # ANRC
        '07': '4F19',  # SNE
        '12': '4F21',  # UID
        '08': '4F4A',  # EXT1
        '14': '4F4B',  # AAS
        '15': '4F4C',  # GAS
        '09': '4F50',  # EMAIL
        '16': '4F54',  # PURI
        '0A': '4F3B',  # ADN1
        '0B': '4F0A',  # PBC1
        '0C': '4F25',  # GRP1
        '0D': '4F12',  # ANRA1
        '0E': '4F14',  # ANRB1
        '0F': '4F16',  # ANRC1
        '10': '4F1A',  # SNE1
        '13': '4F20',  # UID1
        '11': '4F51',  # EMAIL1
        '17': '4F55'  # PURI1
    }
}
