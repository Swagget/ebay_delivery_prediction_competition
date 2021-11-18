import seaborn as sns
import matplotlib.pyplot as plt

class Visualisation:
    @staticmethod
    def plot_line_graph(df, columns_to_display = [], index_column = None, agerage_group_together = 1, show_nulls = False):
        f, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 4))
        try:
            ax.set_title(df.name,fontsize=16)
        except:
            ax.set_title("DF not named", fontsize=16)


        if index_column is None:
            x_input = df.index.values
            x_axis_name = "Index"
        else:
            x_input = df[index_column].values
            x_axis_name = index_column

        for display_col in columns_to_display:
            sns.lineplot(x=x_input, y=df[display_col].rolling(agerage_group_together).mean(), label=display_col)
            if show_nulls:
                sns.lineplot(x=x_input, y=df[display_col].isna(), label=display_col + " Null Values")
        ax.set_xlabel(x_axis_name, fontsize=14)
        plt.show()