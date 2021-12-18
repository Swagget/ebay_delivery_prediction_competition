import os
from datetime import timedelta, datetime

class postprocessing:
    @classmethod
    def generate_output_column(postprocessing, df, predicted_days_column, output_columns_name="predicted_delivery_date"):
        def calc_outputs(row):
            return (row["payment_datetime"] + timedelta(days=row[predicted_days_column])).date().strftime("%Y-%m-%d")
        df[output_columns_name] = df.apply(calc_outputs, axis=1)

    @classmethod
    def generate_submission_file(postprocessing, df, predicted_dates_column):
        if not os.path.isdir("results"):
            os.mkdir("results")
        df[["record_number", predicted_dates_column]].to_csv("./results/result_"+ datetime.now().strftime("%Y-%m-%d %H:%M:%S") +".tsv.gz",
                                                                   header = False, index = False, sep = "\t",
                                                                  compression="gzip")