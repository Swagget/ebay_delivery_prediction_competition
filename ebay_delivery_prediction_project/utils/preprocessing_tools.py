import pandas as pd
import re
import os
from datetime import datetime
import pgeocode
from sklearn.preprocessing import LabelEncoder
import numpy as np


class preprocessing:
    numerical_column = ['declared_handling_days', 'shipping_fee',
                        'carrier_min_estimate',
                        'carrier_max_estimate',
                        'item_price',
                        'quantity',
                        'weight',
                        'distance_between_pincodes']

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

    @staticmethod
    def zip_clean(zipp):
        try:
            return str(int(str(zipp)[:5])).zfill(5)
        except:
            return None

    @classmethod
    def clean_zip_codes(cls, df):
        df["cleaned_item_zip"] = df["item_zip"].apply(lambda zipp: cls.zip_clean(zipp))
        df["cleaned_buyer_zip"] = df["buyer_zip"].apply(lambda zipp: cls.zip_clean(zipp))
        return df

    @classmethod
    def pin_codes_dist(cls, pin_1, pin_2):
        return cls.dist.query_postal_code(pin_1, pin_2)

    @classmethod
    def add_distance_euclidean(cls, df):
        cls.dist = pgeocode.GeoDistance('us')
        # df["distance_between_pincodes"] = df.apply(lambda row: cls.pin_codes_dist(row["cleaned_buyer_zip"],
        #                                                                           row["cleaned_item_zip"]),
        #                                             axis=1)
        df["distance_between_pincodes"] = cls.dist.query_postal_code(
            df["cleaned_item_zip"].values, df["cleaned_buyer_zip"].values)
        return df

    @classmethod
    def removeMissingValues(cls, data, column, missing_val):
        row_names = data[data[column] == missing_val].index
        data.drop(row_names, inplace=True)
        print("Number of Rows dropped: ", len(row_names))
        return data

    @classmethod
    def other_preprocessing(cls, df): # TODO : @monisha could you redefine this and split it up if necessary. I pulled this from your EDA notebook
        df['declared_handling_days'].fillna(df['declared_handling_days'].mean(), inplace=True)
        df = cls.removeMissingValues(df, 'carrier_min_estimate', -1)
        df = cls.removeMissingValues(df, 'carrier_max_estimate', -1)
        columns_to_remove = ['record_number']
        df = df.drop(columns=list(columns_to_remove))
        unique = df.nunique()
        unique = unique[unique.values == 1]
        # print(list(unique.index))
        df = df.drop(columns=list(unique.index))
        categorical_values = ['b2c_c2c', 'package_size']
        le = LabelEncoder()
        df[categorical_values] = df[categorical_values].apply(lambda col: le.fit_transform(col))
        return df

    @classmethod
    def create_mapped_frequencies(cls, df, column_to_get_frequencies):
        seller_id_value_counts = df[column_to_get_frequencies].value_counts()
        mapping_data = {}
        for key in seller_id_value_counts.index:
            mapping_data[key] = seller_id_value_counts[key]
        df[column_to_get_frequencies + "_frequencies"] = df[column_to_get_frequencies].map(mapping_data)
        return df, column_to_get_frequencies + "_frequencies"

    @classmethod
    def basic_preprocessing(Preprocessing, df):
        df = preprocessing.parse_datetime_columns(df)
        print("Finished parse_datetime_columns")
        df = preprocessing.create_delivery_calendar_days(df)
        print("Finished create_delivery_calendar_days")
        df = preprocessing.clean_zip_codes(df)
        print("Finished clean_zip_codes")
        df = preprocessing.add_distance_euclidean(df)
        df = preprocessing.create_mapped_frequencies(df, column_to_get_frequencies = "seller_id")
        return df

    @staticmethod
    def expand_datetime(df, date_column): # Perhaps add  functionality to add more flags and different variables that could be used.
        """Takes a df and a datetime column.
        Outputs the df with the datetime column expanded into year, month, week, day of the week, day of year."""
        df[date_column+"_year"] = df[date_column].apply(lambda x : int(x.strftime('%Y')))
        df[date_column+"_month"] = df[date_column].apply(lambda x : x.month)
        df[date_column+"_week"] = df[date_column].apply(lambda x : x.isocalendar()[1])
        df[date_column+"_weekday"] = df[date_column].apply(lambda x : x.strftime('%A'))
        df[date_column+"_day_of_year"] = df[date_column].apply(lambda x : int(x.strftime('%j')))
        return df

    @classmethod
    def drop_bad_values(cls, df):
        df = preprocessing.replace_neg_with_nan(df)
        df = preprocessing.drop_nan(df)
        return df

    @classmethod
    def replace_neg_with_nan(cls, df):
        for col in cls.numerical_column:
            col_data = df[col]
            negative_mask = col_data < 0
            col_data[negative_mask] = np.nan
            df[col] = col_data
        return df

    @classmethod
    def drop_nan(cls, df):
        na_columns = []
        sum_na = df.isnull().sum()
        columns = df.columns
        for i in range(len(sum_na)):
            if sum_na[i] != 0:
                if int((sum_na[i] / len(df)) * 100) == 0:
                    na_columns.append(columns[i])
        df = df.dropna(subset = na_columns)
        return df

    @classmethod
    def squeeze_outlier_with_interquantile_range(cls, data):
        for col in cls.numerical_column:
            sorted(data[col])
            Q1, Q3 = data[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            lower_limit = Q1 - 1.5 * IQR
            upper_limit = Q3 + 1.5 * IQR
            print('lower_limit: ', lower_limit, 'upper_limit: ', upper_limit)
            upper_rows = data[data[col] > upper_limit]
            lower_rows = data[data[col] < lower_limit]
            outlier_rows = pd.concat([upper_rows, lower_rows])
            data[col] = np.where(data[col] >= upper_limit, upper_limit, data[col])
            data[col] = np.where(data[col] <= lower_limit, lower_limit, data[col])
        return data, outlier_rows