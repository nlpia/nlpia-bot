""" juan_bots describes the data behind a pandas df.plot command with a new df.plot_describe() method """
import regex

import seaborn as sns  # noqa
import matplotlib.pyplot as plt
import pandas as pd

import logging
log = logging.getLogger(__name__)

df = pd.read_csv('http://totalgood.org/midata/teaching/rikeem-u/heights_weights_genders.csv')
df.describe()
# Add Color column with red for Female and blue for Male
df['Color'] = (df['Gender'] == 'Male').apply(lambda x: 'blue' if x else 'red')
# c is color, alpha is opacity (1 - transparency)
fig = df.plot(kind='scatter', x='Height', y='Weight', c='Color', alpha=.3)

# this is how you can display your plot if you want to show someone
plt.show()

# I looked around for the DataFrame in the Figure object but couldn't find it, only the bounding box (min and max values)
print(fig.dataLim)


# Your assignment is to reload the dataframe usind pd.read_html() instead of pd.read_csv()
# The url is 'https://totalgood.org/midata/teaching/rikeem-u/heights_weights_genders.html'
# This is the same as before but with the ".html" file extension.
# and read_html() should return a list of dataframes rather than a single dataframe,
# but this url only has one table, so the list should contain only one dataframe
# Once you download the DataFrame rather than plotting it I'd like you to try to describe using statistics.
# The input to your function is a dataframe and the kwargs that were used in the plot command.
# Here's an example.

def plot_describe(df, **kwargs):
    x_name = kwargs.get('x')
    y_name = kwargs.get('y')  # noqa
    return f"Scatter plot with the x axis ranging from {df[x_name].min()} to {df[x_name].max()}"


class Bot:
    def reply(self, statement):
        """ Generate an invoice or timecard for a project """
        log.warning('Timcard reply in progress...')
        responses = []
        match = regex.match(r'(\bplot[-_.:,;\s]{0,3}describe\b\s*)(.*)', statement.lower())
        if match:
            responses.append((1.0, f"Here's your plot_describe {plot_describe(match.groups()[-1])}"))
        return responses
