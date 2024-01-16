debug_mode = 0

def process(current_DF, current_EF, file_id):
    error = ''

    # current DF is NOT determined
    if current_DF == '':
        file_name = "DF NOT determined"
        error = '*N/A: current DF is NOT determined'

    # current DF is determined
    else:
        if current_DF[:14] in DF_name: current_DF = current_DF[:14]
        # DF_name['A0000000871002'] = 'ADF USIM' 14자리만 인식
        # DF_name['A0000000871004'] = 'ADF ISIM' 14자리만 인식

        # Unknown DF
        if current_DF not in DF_name:
            file_name = file_id
            error = f"*'{current_DF}': Unknown DF"

        # Known DF (if current_DF in DF_name:)
        else:
            # current EF is NOT determined, select current DF
            if current_EF == '':
                file_name = DF_name[current_DF]

            # current EF is determined
            else:
                if current_DF in EF_name:
                    if current_EF in EF_name[current_DF]:
                        file_name = EF_name[current_DF][current_EF]
                    # Unknown file id in current DF
                    else:
                        file_name = file_id
                        error = f"*'{file_id}': Unknown file id in current DF"
                # current DF parsing N/A
                else:
                    file_name = file_id
                    error = f"*'{file_id}': parsing not supported in current DF"

    if debug_mode: print(current_DF, current_EF, file_name, error)

    return file_name, error


DF_name = dict()

# GSMA SGP.02 v4.2
DF_name['A0000005591010FFFFFFFF8900000100'] = 'ISD-R'
DF_name['A0000005591010FFFFFFFF8900000D00'] = 'ISD-PExecutableLoadFile'
DF_name['A0000005591010FFFFFFFF8900000E00'] = 'ISD-PExecutableModule'
DF_name['A0000005591010FFFFFFFF8900000200'] = 'ECASDApplication'

# Android UICC Carrier Privilege
# https://source.android.com/devices/tech/config/uicc?hl=ko
# https://android.googlesource.com/platform/frameworks/opt/telephony/+/master/src/java/com/android/internal/telephony/uicc/UiccCarrierPrivilegeRules.java
# https://android.googlesource.com/platform/frameworks/opt/telephony/+/master/tests/telephonytests/src/com/android/internal/telephony/uicc/UiccCarrierPrivilegeRulesTest.java?autodive=0%2F%2F
DF_name['A000000063504B43532D3135'] = 'ARA-M'
DF_name['A00000015141434C00'] = 'ARA-M'
DF_name['A00000015144414300'] = 'ARA-D'
DF_name['A000000063504B43532D3135'] = 'PKCS15'

# 3GPP ts31.102 Release16
DF_name['3F00'] = 'MF'
DF_name['7F10'] = 'DF TELECOM'
DF_name['7F105F3A'] = 'DF PHONEBOOK'
DF_name['7F105F3B'] = 'DF MULTIMEDIA'
DF_name['7F105F3D'] = 'DF MCS'
DF_name['7F105F3E'] = 'DF V2X'
DF_name['A0000000871002'] = 'ADF USIM'
DF_name['7FFF5F3A'] = 'DF PHONEBOOK'
DF_name['7FFF5F3B'] = 'DF GSM-ACCESS'
DF_name['7FFF5F3C'] = 'DF MexE'
DF_name['7FFF5F70'] = 'DF SoLSA'
DF_name['7FFF5F40'] = 'DF WLAN'
DF_name['7FFF5F50'] = 'DF HNB'
DF_name['7FFF5F90'] = 'DF ProSe'
DF_name['7FFF5FA0'] = 'DF ACDC'
DF_name['7FFF5FB0'] = 'DF TV'
DF_name['7FFF5FC0'] = 'DF 5GS'

# 3GPP ts31.103 Release16
DF_name['A0000000871004'] = 'ADF ISIM'
# DF_name['A0000003431002FF82FFFF89010000FF'] = 'ADF CSIM' #L

# 3GPP ts31.102 Release16
EF_name ={
    '3F00': {
        '2F00': 'DIR',
        '2F05': 'PL',
        '2F06': 'ARR',
        '2FE2': 'ICCID',
        '2F08': 'UMPC',
        '2F30': 'VER',
    },
    '7F10': {
        '6F06': 'ARR',
        '6F3A': 'ADN',
        '6F3B': 'FDN',
        '6F3C': 'SMS',
        '6F40': 'MSISDN',
        '6F42': 'SMSP',
        '6F43': 'SMSS',
        '6F44': 'LND',
        '6F47': 'SMSR',
        '6F49': 'SDN',
        '6F4A': 'EXT1',
        '6F4B': 'EXT2',
        '6F4C': 'EXT3',
        '6F4D': 'BDN',
        '6F4E': 'EXT4',
        '6F4F': 'ECCP',
        '6F53': 'RMA',
        '6F54': 'SUME',
        '6FE0': 'ICE_DN',
        '6FE1': 'ICE_FF',
        '6FE5': 'PSISMSC'
    },
    '7F105F3A': {
        '4F09': 'PBC',
        '4F11': 'ANRA',
        '4F13': 'ANRB',
        '4F15': 'ANRC',
        '4F19': 'SNE',
        '4F21': 'UID',
        '4F22': 'PSC',
        '4F23': 'CC',
        '4F24': 'PUID',
        # '4F25': 'IAP',
        '4F26': 'GRP',
        '4F30': 'PBR',
        '4F3A': 'ADN',
        '4F3D': 'CCP1',
        '4F4A': 'EXT1',
        '4F4B': 'AAS',
        '4F4C': 'GAS',
        '4F50': 'EMAIL',
        '4F54': 'PURI',
        '4F3B': 'ADN1',
        '4F0A': 'PBC1',
        '4F25': 'GRP1',
        '4F12': 'ANRA1',
        '4F14': 'ANRB1',
        '4F16': 'ANRC1',
        '4F1A': 'SNE1',
        '4F20': 'UID1',
        '4F51': 'EMAIL1',
        '4F55': 'PURI1'
},
    '7F105F3B': {
        '4F47': 'MML',
        '4F48': 'MMDF'
    },
    '7F105F3D': {
        '4F01': 'MST',
        '4F02': 'MCS_CONFIG'
    },
    '7F105F3E': {
        '4F01': 'VST',
        '4F02': 'V2X_CONFIG'
    },
    'A0000000871002': {
        '6F05': 'LI',
        '6F06': 'ARR',
        '6F07': 'IMSI',
        '6F08': 'Keys',
        '6F09': 'KeysPS',
        '6F2C': 'DCK',
        '6F31': 'HPPLMN',
        '6F32': 'CNL',
        '6F37': 'ACMmax',
        '6F38': 'UST',
        '6F39': 'ACM',
        '6F3B': 'FDN',
        '6F3C': 'SMS',
        '6F3E': 'GID1',
        '6F3F': 'GID2',
        '6F40': 'MSISDN',
        '6F41': 'PUCT',
        '6F42': 'SMSP',
        '6F43': 'SMSS',
        '6F45': 'CBMI',
        '6F46': 'SPN',
        '6F47': 'SMSR',
        '6F48': 'CBMID',
        '6F49': 'SDN',
        '6F4B': 'EXT2',
        '6F4C': 'EXT3',
        '6F4D': 'BDN',
        '6F4E': 'EXT5',
        '6F4F': 'CCP2',
        '6F50': 'CBMIR',
        '6F55': 'EXT4',
        '6F56': 'EST',
        '6F57': 'ACL',
        '6F58': 'CMI',
        '6F5B': 'START-HFN',
        '6F5C': 'THRESHOLD',
        '6F60': 'PLMNwAcT',
        '6F61': 'OPLMNwAcT',
        '6F62': 'HPLMNwAcT',
        '6F73': 'PSLOCI',
        '6F78': 'ACC',
        '6F7B': 'FPLMN',
        '6F7E': 'LOCI',
        '6F80': 'ICI',
        '6F81': 'OCI',
        '6F82': 'ICT',
        '6F83': 'OCT',
        '6FAD': 'AD',
        '6FB1': 'VGCS',
        '6FB2': 'VGCSS',
        '6FB3': 'VBS',
        '6FB4': 'VBSS',
        '6FB5': 'eMLPP',
        '6FB6': 'AaeM',
        '6FB7': 'ECC',
        '6FC3': 'Hiddenkey',
        '6FC4': 'NETPAR',
        '6FC5': 'PNN',
        '6FC6': 'OPL',
        '6FC7': 'MBDN',
        '6FC8': 'EXT6',
        '6FC9': 'MBI',
        '6FCA': 'MWIS',
        '6FCB': 'CFIS',
        '6FCC': 'EXT7',
        '6FCD': 'SPDI',
        '6FCE': 'MMSN',
        '6FCF': 'EXT8',
        '6FD0': 'MMSICP',
        '6FD1': 'MMSUP',
        '6FD2': 'MMSUCP',
        '6FD3': 'NIA',
        '6FD4': 'VGCSCA',
        '6FD5': 'VBSCA',
        '6FD6': 'GBAP',
        '6FD7': 'MSK',
        '6FD8': 'MUK',
        '6FD9': 'EHPLMN',
        '6FDA': 'GBANL',
        '6FDB': 'EHPLMNPI',
        '6FDC': 'LRPLMNSI',
        '6FDD': 'NAFKCA',
        '6FDE': 'SPNI',
        '6FDF': 'PNNI',
        '6FE2': 'NCP-IP',
        '6FE3': 'EPSLOCI',
        '6FE4': 'EPSNSC',
        '6FE6': 'UFC',
        '6FE7': 'UICCIARI',
        '6FE8': 'NASCONFIG',
        '6FEC': 'PWS',
        '6FED': 'FDNURI',
        '6FEE': 'BDNURI',
        '6FEF': 'SDNURI',
        '6FF0': 'IWL',
        '6FF1': 'IPS',
        '6FF2': 'IPD',
        '6FF3': 'ePDGId',
        '6FF4': 'ePDGSelection',
        '6FF5': 'ePDGIdEm',
        '6FF6': 'ePDGSelectionEm',
        '6FF7': 'FromPreferred',
        '6FF8': 'IMSConfigData',
        '6FF9': '3GPPPSDATAOFF',
        '6FFA': '3GPPPSDATAOFFservicelist',
        '6FFB': 'TVCONFIG',
        '6FFC': 'XCAPConfigData',
        '6FFD': 'EARFCNList',
        '6FFE': 'MuDMiDConfigData'
    },
    '7FFF5F3A': {
        '4F09': 'PBC',
        '4F11': 'ANRA',
        '4F13': 'ANRB',
        '4F15': 'ANRC',
        '4F19': 'SNE',
        '4F21': 'UID',
        '4F22': 'PSC',
        '4F23': 'CC',
        '4F24': 'PUID',
        # '4F25': 'IAP',
        '4F26': 'GRP',
        '4F30': 'PBR',
        '4F3A': 'ADN',
        '4F3D': 'CCP1',
        '4F4A': 'EXT1',
        '4F4B': 'AAS',
        '4F4C': 'GAS',
        '4F50': 'EMAIL',
        '4F54': 'PURI',
        '4F3B': 'ADN1',
        '4F0A': 'PBC1',
        '4F25': 'GRP1',
        '4F12': 'ANRA1',
        '4F14': 'ANRB1',
        '4F16': 'ANRC1',
        '4F1A': 'SNE1',
        '4F20': 'UID1',
        '4F51': 'EMAIL1',
        '4F55': 'PURI1'
    },
    '7FFF5F3B': {
        '4F20': 'Kc',
        '4F52': 'KcGPRS',
        '4F63': 'CPBCH',
        '4F64': 'InvSCAN'
    },
    '7FFF5F3C': {
        '4F40': 'EMxE-ST',
        '4F41': 'ORPK',
        '4F42': 'ARPK',
        '4F43': 'TPRPK',
        '4F44': 'TKCDF'
    },
    '7FFF5F70': {
        '4F30': 'SAI',
        '4F31': 'SLL'
    },
    '7FFF5F40': {
        '4F41': 'Pseudo',
        '4F42': 'UPLMNWLAN',
        '4F43': 'OPLMNWLAN',
        '4F44': 'UWSIDL',
        '4F45': 'OWSIDL',
        '4F46': 'WRI',
        '4F47': 'HWSIDL',
        '4F48': 'WEHPLMNPI',
        '4F49': 'WHPI',
        '4F4A': 'WLRPLMN',
        '4F4B': 'HPLMNDAI'
    },
    '7FFF5F50': {
        '4F81': 'ACSGL',
        '4F82': 'CSGT',
        '4F83': 'HNBN',
        '4F84': 'OCSGL',
        '4F85': 'OCSGT',
        '4F86': 'OHNBN'
    },
    '7FFF5F90': {
        '4F01': 'PROSE_MON',
        '4F02': 'PROSE_ANN',
        '4F03': 'PROSEFUNC',
        '4F04': 'PROSE_RADIO_COM',
        '4F05': 'PROSE_RADIO_MON',
        '4F06': 'PROSE_RADIO_ANN',
        '4F07': 'PROSE_POLICY',
        '4F08': 'PROSE_PLMN',
        '4F09': 'PROSE_GC',
        '4F10': 'PST',
        '4F11': 'PROSE_UIRC',
        '4F12': 'PROSE_GM_DISCOVER',
        '4F13': 'PROSE_RELAY',
        '4F14': 'PROSE_RELAY_DISCOVERY'
    },
    '7FFF5FA0': {
        '4F01': 'ACDC_LIST',
        '4F0A': 'ACDC_OS_CONFIG'
    },
    '7FFF5FB0': {
        '4F01': 'TVUSD'
    },
    '7FFF5FC0': {
        '4F01': '5GS3GPPLOCI',
        '4F02': '5GSN3GPPLOCI',
        '4F03': '5GS3GPPNSC',
        '4F04': '5GSN3GPPNSC',
        '4F05': '5GAUTHKEYS',
        '4F06': 'UAC_AIC',
        '4F07': 'SUCI_Calc_Info',
        '4F08': 'OPL5G',
        '4F09': 'NSI',
        '4F0A': 'Routing_Ind',
        '4F0B': 'URSP',
        '4F0C': 'TN3GPPSNN'
    },
    'A0000000871004': {
        '6F07': 'IST',
        '6F02': 'IMPI',
        '6F03': 'DOMAIN',
        '6F04': 'IMPU',
        '6FAD': 'AD',
        '6F06': 'ARR',
        '6F09': 'P-CSCF',
        '6FD5': 'GBABP',
        '6FD7': 'GBANL',
        '6FDD': 'NAFKCA',
        '6FE7': 'UICCIARI',
        '6F3C': 'SMS',
        '6F43': 'SMSS',
        '6F47': 'SMSR',
        '6F42': 'SMSP',
        '6FF7': 'FromPreferred',
        '6FF8': 'IMSConfigData',
        '6FFC': 'XCAPConfigData',
        '6FFA': 'WebRTCURI'
    }
}

USIM_EF_list = []
for n in EF_name['A0000000871002'].keys():
    USIM_EF_list.append(n)

ISIM_EF_list = []
for n in EF_name['A0000000871004'].keys():
    ISIM_EF_list.append(n)

# print(DF_name)
# print(type(DF_list))
# print(DF_list)

# print(EF_name)
# print(type(MF_EF_list))
# print(MF_EF_list)
# print(type(USIM_EF_list))
# print(USIM_EF_list)
# print(type(ISIM_EF_list))
# print(ISIM_EF_list)