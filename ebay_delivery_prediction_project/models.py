from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
import numpy as np
import lightgbm as lgb
import pandas as pd
from datetime import datetime, date
import seaborn as sns
import matplotlib.pyplot as plt

class preprocessing_models:
    @staticmethod
    def impute_temperature_lgb(df, target_temperature_columns, input_columns, datetime_column = "Date"):
        """Takes the dataframe, target_temperature_columns and input columns. Returns (list_of_trained_models, imputed_dataframe)
        input_columns can contain the terget columns, they will automatically not be used for training, wherever not logical."""

        params = {'num_leaves': 24,
                  'objective': 'regression_l1',
                  'max_depth': 8,
                  'learning_rate': 0.01,
                  "metric": 'mae',
                  "verbosity": -1,
                  'verbose': -1,
                  'seed': 42
                  }

        output_df = df.copy()
        list_of_trained_models = []
        for target in target_temperature_columns:
            test_df = df.copy()
            train_df = df[df[target].notna()]

            features = [c for c in input_columns if c != target]

            X = train_df[features]
            y = train_df[[target]]
            X_test = test_df[features]

            # y_preds = np.zeros(X_test.shape[0])

            X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42)

            dtrain = lgb.Dataset(X_train, y_train, params={'verbose': -1})
            dvalid = lgb.Dataset(X_valid, y_valid, params={'verbose': -1})

            # For analysis set 'verbose_eval' to 200, false
            clf = lgb.train(params, dtrain, 10000, valid_sets=[dtrain, dvalid], verbose_eval=False,
                            early_stopping_rounds=100)

            y_pred_valid = clf.predict(X_valid)
            y_preds = clf.predict(X_test)

            f, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 4))
            ax.set_title(
                f'Rolling Mean Temperatures for {target} \n(Rolling Window: 1 Day, MAE: {mean_absolute_error(y_valid.rolling(1).mean()[1:], pd.Series(y_pred_valid).rolling(1).mean()[1:])})',
                fontsize=16)
            old = df[target].copy().replace({np.nan: np.inf})
            output_df[target] = np.where(output_df[target].isna(), pd.Series(y_preds), df[target])


            sns.lineplot(x=df[datetime_column], y=output_df[target].rolling(1).mean(), label='Imputed',
                         color='darkorange')
            sns.lineplot(x=df[datetime_column], y=old.rolling(1).mean(), label='Original', color='dodgerblue')
            ax.set_xlabel(datetime_column, fontsize=14)
            # ax.set_xlim([date(2000, 1, 1), date(2020, 6, 30)])
            plt.show()
            list_of_trained_models.append(clf)
        return list_of_trained_models, output_df
