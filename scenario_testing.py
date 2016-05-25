import itertools
import numpy as np

from .results_plotter import ResultsPlotter


class Scenario(object):
    def __init__(self,
                 project_cost, loan_term_in_years,
                 annual_interest_rate, annual_revenue):
        self.project_cost = project_cost
        self.loan_term_in_years = loan_term_in_years
        self.annual_interest_rate = annual_interest_rate
        self.annual_revenue = annual_revenue

    def calculate_repayment_amount(self):
        r = self.montly_interest()
        p = self.project_cost
        n = self.number_of_periods()

        c = r * p / (1 - (1 + r) ** -n)
        return c

    def calculate_amount_repayed_by_month(self):
        # X = np.ones(self.number_of_periods() + 1)
        X = self.cumulative_periods_vector()
        X *= self.calculate_repayment_amount()
        return X

    def calculate_amount_owing_by_month(self):
        r = self.montly_interest()
        P = np.zeros(self.number_of_periods() + 1, dtype='float64')
        P[:] = self.project_cost
        N = self.cumulative_periods_vector()
        c = self.calculate_repayment_amount()

        P_f = P * ((1 + r) ** N) - c * (((1 + r) ** N - 1) / r)
        return P_f

    def calculate_cumulative_revenue_by_month(self):
        X = self.cumulative_periods_vector()
        X *= self.montly_revenue()
        return X

    def cumulative_periods_vector(self):
        return np.array(range(self.number_of_periods() + 1), dtype='float64')

    def montly_interest(self):
        return self.annual_interest_rate / 12

    def montly_revenue(self):
        return self.annual_revenue / 12

    def number_of_periods(self):
        return self.loan_term_in_years * 12

    def label(self):
        return {
            'project_cost': self.project_cost,
            'loan_term_in_years': self.loan_term_in_years,
            'annual_interest_rate': self.annual_interest_rate,
            'annual_revenue': self.annual_revenue
        }


class ScenarioCollection(object):
    def __init__(self,
                 project_costs, loan_term_in_years,
                 annual_interest_rates, annual_revenues):
        self.project_costs = project_costs
        self.loan_term_in_years = loan_term_in_years
        self.annual_interest_rates = annual_interest_rates
        self.annual_revenues = annual_revenues
        self.scenarios = self.combine()

    def combine(self):
        scenarios = [
            Scenario(pc, lt, ai, ar)
            for pc, lt, ai, ar in itertools.product(
                self.project_costs,
                [self.loan_term_in_years],
                self.annual_interest_rates,
                self.annual_revenues
            )
        ]

        print('Created %i scenarios.' % len(scenarios))
        return scenarios


class ScenarioTester(object):
    def __init__(self, scenarios):
        self.scenarios = scenarios

    def test(self):
        amount_repayed_by_month = self.calculate_amounts_repayed_by_month()
        amount_owing_by_month = self.calculate_amounts_owing_by_month()
        cumulative_revenue = self.calculate_cumulative_revenues_by_month()
        cumulative_profit = cumulative_revenue - amount_repayed_by_month

        results = ScenarioTestResults(
            amount_repayed_by_month, amount_owing_by_month,
            cumulative_revenue, cumulative_profit,
            self.labels()
        )
        return results

    def calculate_repayment_amounts(self):
        fns = [s.calculate_repayment_amount for s in self.scenarios]
        return self.calculate_from_function(fns)

    def calculate_amounts_repayed_by_month(self):
        fns = [s.calculate_amount_repayed_by_month for s in self.scenarios]
        return self.calculate_from_function(fns)

    def calculate_amounts_owing_by_month(self):
        fns = [s.calculate_amount_owing_by_month for s in self.scenarios]
        return self.calculate_from_function(fns)

    def calculate_cumulative_revenues_by_month(self):
        fns = [s.calculate_cumulative_revenue_by_month for s in self.scenarios]
        return self.calculate_from_function(fns)

    def calculate_from_function(self, fns):
        X = np.array([
            fn() for fn in fns
        ])
        return X

    def labels(self):
        return [s.label for s in self.scenarios]


class ScenarioTestResults(object):
    def __init__(self,
                 amount_repayed, amount_owing,
                 cumulative_revenue, cumulative_profit,
                 labels):
        self.amount_repayed = amount_repayed
        self.amount_owing = amount_owing
        self.cumulative_revenue = cumulative_revenue
        self.cumulative_profit = cumulative_profit

        self.plotter = ResultsPlotter(
            self.amount_repayed, self.amount_owing,
            self.cumulative_revenue, self.cumulative_profit,
            labels
        )
        pass

    def summarise(self):
        print(self.summary_str(
            'Total cost', self.amount_owing[:, 0]))
        print(self.summary_str(
            'Monthly repayment', self.amount_repayed[:, 1]))
        print(self.summary_str(
            'Monthly revenue', self.cumulative_revenue[:, 1]))
        print(self.summary_str(
            'Monthly profit', self.cumulative_profit[:, 1]))
        print(self.summary_str(
            'Total profit', self.cumulative_profit[:, -1]))

    def plot(self):
        self.plotter.plot_and_savefig('results.png')

    def summary_str(self, name, X):
        v_min = np.min(X)
        v_max = np.max(X)
        return self.min_max_str(name, v_min, v_max)

    def min_max_str(self, name, v_min, v_max):
        return '{0}: ${1:,.0f} - ${2:,.0f}'.format(name, v_min, v_max)
