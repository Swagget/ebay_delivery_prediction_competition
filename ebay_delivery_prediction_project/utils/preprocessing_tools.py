import pandas as pd
import re
import os
from datetime import datetime

class preprocessing:
    @staticmethod
    def import_test():
        """Testing import. It should print\"Preprocessing successfully imported.\""""
        print("Preprocessing successfully imported.")

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
        if not pd.isna(df["delivery_date"][0]):
            df["delivery_date"] = df["delivery_date"].apply(preprocess_delivery_date)
        return df

    @classmethod
    def create_delivery_calendar_days(Preprocessing, df):
        # This definetely could be improved. Need to look into time zones, working days, weekends, etc.
        def create_target_col(row):
            return (row["delivery_date"].date() - row["payment_datetime"].date()).days
        df["delivery_calendar_days"] = df.apply(create_target_col, axis=1)
        return df

    @classmethod
    def one_hot_encode_columns(Preprocessing, df, columns):
        generated_columns = []
        for col in columns:
            for val in df[col].unique():
                generated_columns.append(col + "_" + str(val))
        to_return_1 =  pd.get_dummies(df, columns=columns, prefix=columns)
        return to_return_1, generated_columns

    @classmethod
    def basic_preprocessing(Preprocessing, df):
        df = preprocessing.parse_datetime_columns(df)
        df = preprocessing.create_delivery_calendar_days(df)
        return df

    @staticmethod
    def expand_datetime(df, date_column): # Perhaps add  functionality to add more flags and different variables that could be used.
        """Takes a df and a datetime column.
        Outputs the df with the datetime column expanded into year, month, week, day of the week, day of year."""
        df[date_column+"_year"] = df[date_column].apply(lambda x : x.isocalendar()[0])
        df[date_column+"_month"] = df[date_column].apply(lambda x : x.month)
        df[date_column+"_week"] = df[date_column].apply(lambda x : x.isocalendar()[1])
        df[date_column+"_weekday"] = df[date_column].apply(lambda x : x.isocalendar()[2])
        df[date_column+"_day_of_year"] = df[date_column].apply(lambda x : x.isocalendar()[2] + (7 * x.isocalendar()[1]))
        return df