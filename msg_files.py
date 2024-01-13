import file_system
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_colwidth', None)

def process(sum_rst, sum_read, sum_log_ch):

    df_sum_rst = pd.DataFrame(sum_rst)
    df_sum_read = pd.DataFrame(sum_read)
    df_sum_log_ch = pd.DataFrame(sum_log_ch)
    df = pd.concat([df_sum_rst, df_sum_read, df_sum_log_ch], axis=1)
    if len(df.columns) < 6: df.insert(loc=3, column='read_3',value='')
    df.columns = ['rst', 'read_1', 'read_2', 'read_3', 'DF_Id', 'File_Id']

    df = df[df['rst'].str.contains('READ')]
    df['contents'] = df['read_1'].apply(lambda x: x[0] if len(x) >= 1 else None)
    df['parsing'] = df['read_1'].apply(lambda x: x[1] if len(x) == 2 else None)
    del df['read_1']

    df_binary = df[df['rst'].str.contains('READ BINARY')]
    df_binary = df_binary.copy()
    df_binary[['OFS', 'LEN']] = df_binary['read_2'].apply(pd.Series)
    df_binary.drop(['read_2', 'read_3'], axis=1, inplace=True)
    df_binary['Type'] = 'TF'

    df_record = df[df['rst'].str.contains('READ RECORD')]
    df_record = df_record.copy()
    df_record['REC#'] = df_record['read_2']
    df_record['LEN'] = df_record['read_3']
    df_record.drop(['read_2', 'read_3'], axis=1, inplace=True)
    df_record['Type'] = 'LF'

    df = pd.concat([df_binary, df_record])
    df['REC#'] = df['REC#'].fillna('-')
    df['OFS'] = df['OFS'].fillna('-')

    df_SFI = df[df['rst'].str.contains('SFI')]
    df_nonSFI = df[~df['rst'].str.contains('SFI')]

    df_SFI = df_SFI.copy()
    df_SFI['SFI'] = df_SFI['rst'].str.extract('SFI: 0x(\S{2})')

    df = pd.concat([df_SFI, df_nonSFI])
    df['SFI'] = df['SFI'].fillna('-')

    df = df.copy()
    df['ref'] = df['rst'].str.extract('(\[\d+\])')
    del df['rst']

    df['DF'] = df['DF_Id'].str[:14].map(file_system.DF_name)
    df['DF'] = df['DF'].fillna('-')
    def get_File_name(row):
        return file_system.EF_name.get(row['DF_Id'][:14], {}).get(row['File_Id'])
    df['File'] = df.apply(get_File_name, axis=1)
    df['File'] = df['File'].fillna('-')
    # df.dropna(subset='File', inplace=True)

    unique_contents = df.groupby(['DF','DF_Id','File','File_Id','REC#','OFS'])['contents'].nunique() > 1
    mapped_values = df.set_index(['DF','DF_Id','File','File_Id','REC#','OFS']).index.map(unique_contents)
    df['OTA_updated'] = mapped_values.fillna(0).astype(int)

    df.loc[df['DF'].str.contains('ADF USIM'), 'DF_Id'] = 'AID'
    df.loc[df['DF'].str.contains('ADF ISIM'), 'DF_Id'] = 'AID'

    all_columns = df.columns.tolist()
    columns_to_check = [col for col in all_columns if col != 'ref']
    df.drop_duplicates(subset=columns_to_check, inplace= True)

    df.sort_values(['DF','File_Id','REC#'], ascending=[True, True, True], inplace=True)
    df_MF = df[df['DF'].str.contains('MF')]
    df_nonMF = df[~df['DF'].str.contains('MF')]
    df = pd.concat([df_MF, df_nonMF], ignore_index=True)
    df_ISIM = df[df['DF'].str.contains('ISIM')]
    df_nonISIM = df[~df['DF'].str.contains('ISIM')]
    df = pd.concat([df_nonISIM, df_ISIM], ignore_index=True)

    new_order = ['DF', 'File', 'DF_Id', 'File_Id',  'Type', 'SFI', 'REC#', 'OFS', 'LEN',
                 'ref', 'OTA_updated', 'contents', 'parsing']
    df = df[new_order]

    # df.to_excel('output.xlsx', index=False)

    return df