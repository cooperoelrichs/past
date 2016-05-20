import itertools
import numpy as np


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
        X = np.empty((self.number_of_periods() + 1))
        X[:] = self.calculate_repayment_amount()
        return X

    def montly_interest(self):
        return self.annual_interest_rate / 12

    def number_of_periods(self):
        return self.loan_term_in_years * 12


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
        repayment_amount = self.calculate_repayment_amount()
        amount_repayed_by_month = self.calculate_amount_repayed_by_month()
        amount_owing_by_month = self.calculate_amount_owing_by_month()

        results = ScenarioTestResults(
            repayment_amount, amount_repayed_by_month,
            amount_owing_by_month,
            cumulative_revenue, cumulative_profit
        )
        return results

    def calculate_repayment_amount(self):
        fns = [s.calculate_repayment_amount for s in self.scenarios]
        repayment_amount = self.calculate_from_function(fns)
        return repayment_amount

    def calculate_amount_repayed_by_month(self):
        fns = [s.calculate_amount_repayed_by_month for s in self.scenarios]
        amount_repayed = self.calculate_from_function(fns)
        return amount_repayed

    def calculate_from_function(self, fns):
        X = np.array([
            fn() for fn in fns
        ])
        return X


class ScenarioTestResults(object):
    def __init__(self,
                 amount_payed, amount_owing,
                 cumulative_revenue, cumulative_profit):
        self.amount_payed = amount_payed
        self.amount_owing = amount_owing
        self.cumulative_revenue = cumulative_revenue
        self.cumulative_profit = cumulative_profit
        pass

    def summarise(self):
        pass

    def plot(self):
        pass
