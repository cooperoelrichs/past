import itertools
import numpy as np

from .results_plotter import ResultsPlotter


class Scenario(object):
    def __init__(self,
                 name,
                 principle, annual_interest_rate, interest_only,
                 loan_term_in_years, lead_time_in_years,
                 revenue_unit, annual_revenue_factor,
                 max_loan_term):
        self.principle = principle
        self.annual_interest_rate = annual_interest_rate
        self.interest_only = interest_only
        self.loan_term_in_years = loan_term_in_years
        self.lead_time_in_years = lead_time_in_years
        self.revenue_unit = revenue_unit
        self.annual_revenue = revenue_unit * annual_revenue_factor
        self.max_loan_term = max_loan_term

    def calculate_repayment_amount(self):
        r = self.montly_interest()
        p = self.principle
        n = self.number_of_periods()

        if self.interest_only:
            c = r * p
        elif not self.interest_only:
            c = r * p / (1 - (1 + r) ** -n)
        return c

    def calculate_amount_repayed_by_month(self):
        X = self.cumulative_periods_vector()
        X[self.number_of_periods() + 1:] = np.max(X)
        X *= self.calculate_repayment_amount()
        return X

    def calculate_amount_owing_by_month(self):
        r = self.montly_interest()
        P = np.zeros(self.max_num_periods() + 1, dtype='float64')
        P[:self.number_of_periods() + 1] = self.principle
        N = self.cumulative_periods_vector()
        c = self.calculate_repayment_amount()

        P_f = P * ((1 + r) ** N) - c * (((1 + r) ** N - 1) / r)
        return P_f

    def calculate_cumulative_revenue_by_month(self):
        X = np.array(
            range(self.max_num_periods() + 1),
            dtype='float64'
        )
        # X[self.number_of_periods() + 1:] = np.max(X)
        X -= self.lead_time_in_months()
        X[X < 0] = 0
        X *= self.montly_revenue()
        return X

    def cumulative_periods_vector(self):
        cumulative_periods = np.zeros(
            self.max_num_periods() + 1,
            dtype='float64'
        )
        cumulative_periods[:self.number_of_periods() + 1] = np.array(
            range(self.number_of_periods() + 1),
            dtype='float64'
        )
        return cumulative_periods

    def calculate_annual_rate_of_return(self):
        return self.annual_revenue / self.principle

    def montly_interest(self):
        return self.annual_interest_rate / 12

    def montly_revenue(self):
        return self.annual_revenue / 12

    def number_of_periods(self):
        return self.loan_term_in_years * 12

    def lead_time_in_months(self):
        return self.lead_time_in_years * 12

    def max_num_periods(self):
        return self.max_loan_term * 12

    def label(self):
        return {
            'principle': self.principle,
            'loan_term': self.loan_term_in_years,
            'interest_rate': self.annual_interest_rate,
            'revenue': self.revenue_unit,
            'annual_rate_of_return': self.calculate_annual_rate_of_return()
        }


class ScenarioCollection(object):
    def __init__(self,
                 name,
                 principles, annual_interest_rates,
                 interest_only, loan_terms_in_years,
                 lead_times_in_years, revenue_units,
                 annual_revenue_factor):
        self.name = name
        self.principles = principles
        self.annual_interest_rates = annual_interest_rates
        self.interest_only = interest_only
        self.loan_terms_in_years = loan_terms_in_years
        self.lead_times_in_years = lead_times_in_years
        self.revenue_units = revenue_units
        self.annual_revenue_factor = annual_revenue_factor

        self.scenarios = self.combine()

    def combine(self):
        scenarios = [
            Scenario(
                self.name,
                p, ir, io, lt, ld, ru,
                self.annual_revenue_factor, self.max_loan_length()
            )
            for p, ir, io, lt, ld, ru in itertools.product(
                self.principles,
                self.annual_interest_rates,
                self.interest_only,
                self.loan_terms_in_years,
                self.lead_times_in_years,
                self.revenue_units
            )
        ]

        print('Created %i scenarios.' % len(scenarios))
        return scenarios

    def max_loan_length(self):
        return max(self.loan_terms_in_years)


class ScenarioTester(object):
    def __init__(self, name, scenarios):
        self.name = name
        self.scenarios = scenarios

    def test(self):
        amount_repayed_by_month = self.calculate_amounts_repayed_by_month()
        amount_owing_by_month = self.calculate_amounts_owing_by_month()
        cumulative_revenue = self.calculate_cumulative_revenues_by_month()
        cumulative_profit = cumulative_revenue - amount_repayed_by_month
        annual_rates_of_return = self.calculate_annual_rates_of_return()

        results = ScenarioTestResults(
            self.name,
            amount_repayed_by_month, amount_owing_by_month,
            cumulative_revenue, cumulative_profit,
            annual_rates_of_return,
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

    def calculate_annual_rates_of_return(self):
        fns = [s.calculate_annual_rate_of_return for s in self.scenarios]
        return self.calculate_from_function(fns)

    def calculate_from_function(self, fns):
        X = np.array([
            fn() for fn in fns
        ])
        return X

    def labels(self):
        return [s.label() for s in self.scenarios]


class ScenarioTestResults(object):
    def __init__(self,
                 name,
                 amount_repayed, amount_owing,
                 cumulative_revenue, cumulative_profit,
                 annual_rates_of_return,
                 labels):
        self.name = name
        self.amount_repayed = amount_repayed
        self.amount_owing = amount_owing
        self.cumulative_revenue = cumulative_revenue
        self.cumulative_profit = cumulative_profit
        self.annual_rates_of_return = annual_rates_of_return

        self.plotter = ResultsPlotter(
            self.name,
            self.amount_repayed, self.amount_owing,
            self.cumulative_revenue, self.cumulative_profit,
            labels
        )
        pass

    def summarise(self):
        print(self.name)
        print(self.summarise_range_of_dollars(
            'Total Cost', self.amount_owing[:, 0]))
        print(self.summarise_range_of_dollars(
            'Monthly Repayment', self.amount_repayed[:, 1]))
        print(self.summarise_range_of_dollars(
            'Monthly Revenue',
            self.cumulative_revenue[:, -1] - self.cumulative_revenue[:, -2]))
        print(self.summarise_range_of_dollars(
            'Monthly Profit',
            self.cumulative_profit[:, -1] - self.cumulative_profit[:, -2]))
        print(self.summarise_range_of_dollars(
            'Total Profit', self.cumulative_profit[:, -1]))
        print(self.summarise_range_of_fractionals(
            'Annual Rate of Return', self.annual_rates_of_return))

    def plot(self, file_name):
        self.plotter.plot_and_savefig(file_name)

    def summarise_range_of_dollars(self, name, X):
        v_min, v_max = self.min_max(X)
        if len(X) == 1 or v_min == v_max:
            return '{0}: ${1:,.0f}'.format(name, X[0])
        else:
            return '{0}: ${1:,.0f} - ${2:,.0f}'.format(name, v_min, v_max)

    def summarise_range_of_fractionals(self, name, X):
        v_min, v_max = self.min_max(X)
        if len(X) == 1 or v_min == v_max:
            return '{0}: %{1:,.1f}'.format(name, X[0] * 100)
        else:
            return '{0}: %{1:,.1f} - %{2:,.1f}'.format(name, v_min * 100, v_max * 100)

    def min_max(self, X):
        return np.min(X), np.max(X)

    # def dollar_summary_str(self, name, v_min, v_max):
    #     return '{0}: ${1:,.0f} - ${2:,.0f}'.format(name, v_min, v_max)

    # def fractional_summary_str(self, name, v_min, v_max):
    #     return '{0}: %{1:,.1f} - %{2:,.1f}'.format(name, v_min * 100, v_max * 100)
