class Scenario(object):
    def __init__(self,
                 project_cost, loan_term_in_years,
                 annual_interest_rate, annual_revenue):
        self.project_cost = project_cost
        self.loan_term_in_years = loan_term_in_years
        self.annual_interest_rate = annual_interest_rate
        self.annual_revenue = annual_revenue


class ScenarioTester(object):
    def __init__(self, scenario):
        self.scenario = scenario

    def test(self):
        results = ScenarioTestResults()
        return results


class ScenarioTestResults(object):
    def __init__(self):
        pass

    def summarise(self):
        pass

    def plot(self):
        pass
