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
                 name,
                 amount_repayed, amount_owing,
                 cumulative_revenue, cumulative_profit,
                 labels):
        self.name = name
        self.amount_repayed = amount_repayed
        self.amount_owing = amount_owing
        self.cumulative_revenue = cumulative_revenue
        self.cumulative_profit = cumulative_profit
        self.formats = plot_formats
        self.labels = labels

    def plot_and_savefig(self, file_name):
        plt.figure()
        self.plot_it()
        plt.savefig(file_name, bbox_inches='tight')
        plt.close()

    def plot_it(self):
        ax = plt.subplot(1, 1, 1)

        ax = self.add_zero_line(ax, self.amount_repayed)
        ax = self.add_series_and_fill(ax, self.amount_repayed, 'AR', -1)
        ax = self.add_series_and_fill(ax, self.amount_owing, 'AO', 0)
        ax = self.add_series_and_fill(ax, self.cumulative_revenue, 'CR', -1)
        ax = self.add_series_and_fill(ax, self.cumulative_profit, 'CP', -1)

        # ax = self.label_series(ax, self.cumulative_profit)
        ax = self.add_summary_label(ax)

        plt.title('Oh Cabins - Comparison of Different Scenarios\n%s' % self.name)
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
        X = self.make_x(series)
        collection = self.make_line_collection(
            X, series, self.formats[name]
        )
        ax.add_collection(collection, autolim=True)

        Y_max = np.max(series, axis=0)
        Y_min = np.min(series, axis=0)
        ax.fill_between(
            X, Y_min, Y_max,
            facecolor=self.formats[name]['colour'], alpha=0.4
        )
        return ax

    def make_line_collection(self, X, series, format_):
        # series [series, y]
        # Lines [series, x, y]
        lines = np.zeros((series.shape[0], series.shape[1], 2))
        lines[:, :, 0] = X
        lines[:, :, 1] = series

        lc = LineCollection(
            lines,
            colors=format_['colour'],
            label=format_['label'],
            alpha=1
        )
        return lc

    def add_zero_line(self, ax, series):
        X = self.make_x(series)
        ax.plot(X, X, c=grey_colour, linewidth=2, alpha=0.7, zorder=1)
        return ax

    def make_x(self, series):
        X = np.array(range(series.shape[1]), dtype='float64')
        X /= 12
        return X

    def add_summary_label(self, ax):
        series = self.cumulative_profit
        if series.shape[0] > 1:
            best_i, worst_i = self.max_and_min_index(self.cumulative_profit)
            best = self.make_summary_label(self.labels[best_i])
            worst = self.make_summary_label(self.labels[worst_i])
            label_str = 'best case: %s\nworst case: %s' % (best, worst)
        else:
            single_case = self.make_summary_label(self.labels[0])
            label_str = 'case summary: %s' % single_case

        ax.text(
            0.02, 0.79,
            label_str,
            # verticalalignment=verticalalignment,
            horizontalalignment='left',
            transform=ax.transAxes,
            color=grey_colour,
            fontsize=10,
            fontstyle='normal',
            # fontweight='100',
            bbox={
                # 'facecolor': 'red',
                # 'alpha': 0.5,
                # 'pad': 10
            }
        )
        return ax

    def max_and_min_index(self, series):
        i_max = np.argmax(series[:, -1])
        i_min = np.argmin(series[:, -1])
        return i_max, i_min

    def make_summary_label(self, label):
        return '; '.join([
            '\${:,.0f}'.format(label['principle']),
            '{:,.0f} y'.format(label['loan_term']),
            '{:,.1f}% i.r.'.format(label['interest_rate'] * 100),
            '\${:,.0f} p.w.'.format(label['revenue']),
            '{:,.1f}% a.r.o.r.'.format(label['annual_rate_of_return'] * 100)
        ])

    def label_series(self, ax, series):
        X = self.make_x(series)
        i_max = np.argmax(series[:, -1])
        i_min = np.argmin(series[:, -1])

        if series.shape[0] > 1:
            label_indicies = [(i_max, 'max'), (i_min, 'min')]
        else:
            label_indicies = [(i_max, 'max')]

        for i, p in label_indicies:
            label_str = self.make_aror_label(self.labels[i])
            ax = self.put_label_on_y(ax, X, series[i], label_str, p)

        return ax

    def make_aror_label(self, label):
        aror = label['annual_rate_of_return']
        label_str = '{:,.0f}% a.r.o.r.'.format(aror * 100)
        return label_str

    def put_label_on_y(self, ax, X, Y, label, min_or_max):
        x_position = X[-1]
        y_position = Y[-1]

        if min_or_max == 'min':
            verticalalignment = 'bottom'
        elif min_or_max == 'max':
            verticalalignment = 'bottom'
        else:
            raise RuntimeError()

        ax.text(
            x_position, y_position,
            label,
            verticalalignment=verticalalignment,
            horizontalalignment='right',
            # transform=ax.transAxes,
            color=grey_colour,
            fontsize=10,
            fontstyle='normal',
            # fontweight='100'
        )
        return ax
