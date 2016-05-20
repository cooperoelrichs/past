import numpy as np

%matplotlib inline
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.collections import LineCollection

matplotlib.rcParams['figure.figsize'] = (10.0, 8.0)
plt.style.use('ggplot')


ns = np.array(range(processor.repayment_periods())) + 1
amount_payed = mlc(ns, fr.amount_payed)
amount_owing = mlc(ns, fr.amount_owing)
cumulative_revenue = mlc(ns, fr.cumulative_revenue)
cumulative_income = mlc(ns, fr.cumulative_income)

ax = plt.subplot(1, 1, 1)

ax.add_collection(LineCollection(amount_owing, colors='r', label='Amount Owing on Loan'), autolim=True)
ax.fill_between(ns, amount_owing[0][:, 1], amount_owing[1][:, 1], facecolor='r', alpha=0.5)

ax.add_collection(LineCollection(amount_payed, colors='y', label='Cumulative Loan Repayments'), autolim=True)
ax.fill_between(ns, amount_payed[0][:, 1], amount_payed[1][:, 1], facecolor='y', alpha=0.5)

ax.add_collection(LineCollection(cumulative_revenue, colors='b', label='Cumulative Rent'), autolim=True)
ax.fill_between(ns, cumulative_revenue[0][:, 1], cumulative_revenue[1][:, 1], facecolor='b', alpha=0.5)

ax.add_collection(LineCollection(cumulative_income, colors='g', label='Cumulative Profit'), autolim=True)
ax.fill_between(ns, cumulative_income[0][:, 1], cumulative_income[1][:, 1], facecolor='g', alpha=0.5)

plt.xlabel('Months')
yl = plt.ylabel('$  ')

plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
yl.set_rotation(0)
ax.get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: format(x, ',.0f')))
ax.autoscale_view()
plt.show()
