import pandas as pd
import re
import os
from collections import defaultdict
import numpy as np
from datetime import datetime

class Preprocessing:
    @staticmethod
    def import_test():
        """Testing import. It should print\"Preprocessing successfully imported.\""""
        print("Preprocessing successfully imported.")

    # @staticmethod
    # def get_filtered_columns(dfs, temperature = False, rainfall = False, date = False, include_datetime = False):
    #     """Takes dataframe or list of dataframes and parameters for which columns you want, returns dict with lists of column names.
    #     It doesn't give columns with \"datetime64[ns]\" format, because that isn't trainable or """
    #     all_columns_prefix_strings = []
    #     if temperature:
    #         all_columns_prefix_strings.append("Temperature")
    #     if rainfall:
    #         all_columns_prefix_strings.append("Rainfall")
    #     if date:
    #         all_columns_prefix_strings.append("Date")
    #     cols_to_return = defaultdict(lambda : [])
    #     if type(dfs) is list:
    #         for df in dfs:
    #             cols_to_return[df.name] = []
    #     else:
    #         cols_to_return[dfs.name] = []
    #     for col_prefix in all_columns_prefix_strings:
    #         if type(dfs) is list:
    #             for df in dfs:
    #                 # cols_to_return[df.name] = cols_to_return[df.name] + list(df.columns[df.columns.str.startswith(col_prefix)].values)
    #                 for col_to_append in list(df.columns[df.columns.str.startswith(col_prefix)].values):
    #                     if include_datetime == False:
    #                         if df[col_to_append].dtype == np.dtype('datetime64[ns]'):
    #                             continue
    #                     cols_to_return[df.name].append(col_to_append)
    #         else:
    #             # cols_to_return[dfs.name] = cols_to_return[dfs.name] + list(dfs.columns[dfs.columns.str.startswith(col_prefix)].values)
    #             for col_to_append in list(dfs.columns[dfs.columns.str.startswith(col_prefix)].values):
    #                 if include_datetime == False:
    #                     if dfs[col_to_append].dtype == np.dtype('datetime64[ns]'):
    #                         continue
    #                 cols_to_return[dfs.name].append(col_to_append)
    #     return dict(cols_to_return)

    @classmethod
    def read_data(Preprocessing, path="../data/supplied_data/", rows_to_read=100, columns = []): # This could use a random parameter that shuffles which rows are picked.
        """Reads all csvs from path, names them, and returns a dict with all dataframe objects.
        If rows_to_read is set to None then it will attempt to read all the rows.
        """
        if rows_to_read is None:
            print("Reading full data.")
        else:
            print(f"Reading {rows_to_read} rows.")
        if columns == []:
            print("Reading all columns.")
        else:
            print(f"Reading {columns} columns.")
        csv_re = re.compile(".tsv$")
        dataset_object = {}
        for file in os.listdir(path):
            if csv_re.search(file) is not None:
                file_path = os.path.join(path, file)
                file_name = file[:csv_re.search(file).start()]
                if rows_to_read != None:
                    if columns == []:
                        dataset_object[file_name] = pd.read_csv(file_path, sep='\t', nrows=rows_to_read)
                    else:
                        dataset_object[file_name] = pd.read_csv(file_path, sep='\t', nrows=rows_to_read, usecols=columns)
                else:
                    if columns == []:
                        dataset_object[file_name] = pd.read_csv(file_path, sep='\t')
                    else:
                        dataset_object[file_name] = pd.read_csv(file_path, sep='\t', usecols=columns)

                dataset_object[file_name].name = file_name
        return dataset_object

    @classmethod
    def parse_datetime_columns(Preprocessing, df):
        def preprocess_payment_datetime(string):
            return datetime.strptime(string[:-3] + string[-2:], '%Y-%m-%d %H:%M:%S.000%z')
        def preprocess_delivery_date(string):
            return datetime.strptime(string, '%Y-%m-%d')
        df["acceptance_scan_timestamp"] = df["acceptance_scan_timestamp"].apply(preprocess_payment_datetime)
        df["payment_datetime"] = df["payment_datetime"].apply(preprocess_payment_datetime)
        df["delivery_date"] = df["delivery_date"].apply(preprocess_delivery_date)
        return df

    @classmethod
    def create_delivery_calendar_days(Preprocessing, df):
        # This definetely could be improved. Need to look into time zones, working days, weekends, etc.
        def create_target_col(row):
            return (row["delivery_date"].date() - row["payment_datetime"].date()).days
        df["delivery_calendar_days"] = df.apply(create_target_col, axis=1)
        return df

    # @staticmethod
    # def expand_datetime(df, date_column):
    #     """Takes a df and a datetime column. Outputs the df with the datetime column expanded into year, month, week, day of year."""
    #     df[date_column+"_year"] = df[date_column].apply(lambda x : x.year)
    #     df[date_column+"_month"] = df[date_column].apply(lambda x : x.month)
    #     df[date_column+"_week"] = df[date_column].apply(lambda x : x.week)
    #     df[date_column+"_day_of_year"] = df[date_column].apply(lambda x : (x - datetime.datetime(x.year, 1, 1)).days + 1)
    #     return df
    #
    # @staticmethod
    # def replace_implausible_zeros(df, col_name):
    #     """Takes df and a column name. Returns a series where all consecutive zeros are replaced by np.nan, because that's missing data."""
    #     temp_col = df[[col_name]].copy()
    #     temp_col['key'] = (temp_col[col_name] != temp_col[col_name].shift(1)).astype(int).cumsum() # Cumilative sum, this groups together because adjascent values will be euqal and no non adjascent will have the same value.
    #     key_dict = temp_col.groupby(['key']).agg({col_name : 'mean', 'key':'count'}) # Cumalitive values are grouped together. with their count and values.
    #     key_dict = key_dict[(key_dict[col_name]==0) & (key_dict.key >2)] # This is where the consective values are filtered to zeros, and only where there are more than 2 consecutive are selected.
    #     for key in key_dict.index:
    #         temp_col[col_name] = np.where(temp_col['key'] == key, np.nan, temp_col[col_name]) # The key values are replaced with 0s. need to see what np.where does exactly
    #     return temp_col[col_name]
