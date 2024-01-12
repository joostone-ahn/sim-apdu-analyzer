import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_colwidth', None)

def process(sum_rst, sum_read, sum_log_ch, sum_log_ch_id):

    df_sum_rst = pd.DataFrame(sum_rst)
    df_sum_read = pd.DataFrame(sum_read)
    df_sum_log_ch = pd.DataFrame(sum_log_ch)
    df_sum_log_ch_id = pd.DataFrame(sum_log_ch_id)
    df = pd.concat([df_sum_rst, df_sum_read, df_sum_log_ch, df_sum_log_ch_id], axis=1)
    print(df.head())
    df.columns = ['rst', 'read_1', 'read_2', 'read_3', 'DF', 'File_Id', 'log_ch_id']
    df = df[df['rst'].str.contains('READ')]

    df['contents'] = df['read_1'].apply(lambda x: x[0] if len(x) >= 1 else None)
    df['parsing'] = df['read_1'].apply(lambda x: x[1] if len(x) == 2 else None)
    del df['read_1']

    df_binary = df[df['rst'].str.contains('READ BINARY')]
    df_binary = df_binary.copy()
    df_binary[['offset', 'length']] = df_binary['read_2'].apply(pd.Series)
    df_binary.drop(['read_2', 'read_3'], axis=1, inplace=True)
    df_binary['type'] = 'TF'

    df_record = df[df['rst'].str.contains('READ RECORD')]
    df_record = df_record.copy()
    df_record['record_num'] = df_record['read_2']
    df_record['length'] = df_record['read_3']
    df_record.drop(['read_2', 'read_3'], axis=1, inplace=True)
    df_record['type'] = 'LF'

    df_combined = pd.concat([df_binary, df_record], ignore_index=True)

    new_order = ['rst', 'log_ch_id', 'DF','File_Id','type', 'offset', 'record_num', 'length', 'contents', 'parsing']
    df_combined = df_combined[new_order]
    print(df_combined)

    return