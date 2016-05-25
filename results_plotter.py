import numpy as np

# %matplotlib inline
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.collections import LineCollection


matplotlib.rcParams['figure.figsize'] = (10.0, 8.0)
# plt.style.use('ggplot')


def to_rgba(rgb):
    return tuple([x / 255 for x in rgb])


grey_colour = to_rgba((85, 85, 85))

plot_formats = {
    'AR': {
        'colour': to_rgba((226, 74, 51)),  # E24A33
        'label': 'Cumulative Amount Repayed'
    },

    'AO': {
        'colour': to_rgba((166, 6, 40)),  # A60628
        'label': 'Amount Owing on Loan'
    },

    'CR': {
        'colour': to_rgba((52, 138, 189)),  # 348ABD
        'label': 'Cumulative Revenue'
    },

    'CP': {
        'colour': to_rgba((70, 120, 33)),  # 467821
        'label': 'Cumulative Profit'
    }
}


class ResultsPlotter(object):
    def __init__(self,
                 amount_repayed, amount_owing,
                 cumulative_revenue, cumulative_profit,
                 labels):
        self.amount_repayed = amount_repayed
        self.amount_owing = amount_owing
        self.cumulative_revenue = cumulative_revenue
        self.cumulative_profit = cumulative_profit
        self.formats = plot_formats
        self.labels = labels

    def plot_and_savefig(self, file_name):
        self.plot_it()
        plt.savefig(file_name, bbox_inches='tight')

    def plot_it(self):
        ax = plt.subplot(1, 1, 1)

        ax = self.add_zero_line(ax, self.amount_repayed)
        ax = self.add_series_and_fill(ax, self.amount_repayed, 'AR', -1)
        ax = self.add_series_and_fill(ax, self.amount_owing, 'AO', 0)
        ax = self.add_series_and_fill(ax, self.cumulative_revenue, 'CR', -1)
        ax = self.add_series_and_fill(ax, self.cumulative_profit, 'CP', -1)

        plt.title('Oh Cabins - Comparison of Different Scenarios')
        plt.xlabel('Years')
        yl = plt.ylabel('$  ')

        legend = plt.legend(
            loc="upper left",
            # frameon=False,
            bbox_to_anchor=(0, 1)
        )

        for text in legend.get_texts():
            plt.setp(text, color=grey_colour)  # fontsize=10

        yl.set_rotation(0)
        ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda x, p: format(x, ',.0f'))
        )
        # ax.tick_params(axis='both', which='both', length=0)
        ax.autoscale_view()

    def add_series_and_fill(self, ax, series, name, max_axis):
        x = self.make_x(series)
        collection = self.make_line_collection(
            x, series, self.formats[name]
        )
        ax.add_collection(collection, autolim=True)

        y_max = np.max(series, axis=0)
        y_min = np.min(series, axis=0)
        ax.fill_between(
            x, y_min, y_max,
            facecolor=self.formats[name]['colour'], alpha=0.4
        )
        return ax

    def make_line_collection(self, x, series, format_):
        # series [series, y]
        # Lines [series, x, y]
        lines = np.zeros((series.shape[0], series.shape[1], 2))
        lines[:, :, 0] = x
        lines[:, :, 1] = series

        lc = LineCollection(
            lines,
            colors=format_['colour'],
            label=format_['label'],
            alpha=1
        )
        return lc

    def add_zero_line(self, ax, series):
        x = self.make_x(series)
        ax.plot(x, x, c=grey_colour, linewidth=2, alpha=0.7, zorder=1)
        return ax

    def make_x(self, series):
        x = np.array(range(series.shape[1]), dtype='float64')
        x /= 12
        return x
