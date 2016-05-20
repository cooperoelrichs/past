import pandas as pd
import numpy as np
import math


class ProjectVariable(object):
    def is_str(self, variable_name, x):
        self.is_type(str, variable_name, x)

    def is_optional_str(self, variable_name, x):
        self.is_optional_type(float, variable_name, x)

    def is_optional_type(self, optional_type, variable_name, x):
        if x is None:
            pass
        else:
            self.is_type(str, variable_name, x)

    def is_flt(self, variable_name, x):
        self.is_type(float, variable_name, x)

    def is_type(self, required_type, variable_name, x):
        if isinstance(x, required_type):
            pass
        else:
            self.raise_type_error(required_type, variable_name, x)

    def is_float64(self, variable_name, x):
        self.is_dtype(np.float64, variable_name, x)

    def is_dtype(self, required_type, variable_name, x):
        if np.issubdtype(x.dtype, required_type):
            pass
        else:
            self.raise_type_error(required_type, variable_name, x)

    def raise_type_error(self, required_type, variable_name, x):
        raise TypeError(
            '%s (%s, %s) is not a %s.'
            % (variable_name, str(x), type(x), required_type.__name__)
        )

    def process_nan(self, x):
        if isinstance(x, float) and math.isnan(x):
            return None
        else:
            return x

    def validate_amount(self, amount):
        self.is_float64('amount', self.amount)
        self.amount_is_correct_len(self.amount)
        self.amount_is_correctly_ordered(self.amount)

    def amount_is_correct_len(self, x):
        correct_len = 2
        if len(x) != correct_len:
            raise RuntimeError(
                'Amount is not of length %i, len = %i, amount = '
                % (correct_len, len(x), str(x))
            )

    def amount_is_correctly_ordered(self, x):
        if not (x[0] <= x[1]):
            raise RuntimeError(
                'Amount is not ordered [min, max], amount = %s' % str(x)
            )


class ProjectUnit(ProjectVariable):
    def __init__(self, id, project, category, name,
                 description, amount_min, amount_max):
        self.id = id
        self.project = project
        self.category = category
        self.name = name
        self.description = self.process_nan(description)
        self.amount = self.new_amount(amount_min, amount_max)

        self.validate_self()

    def summary_str(self):
        return ', '.join(
            [self.id, self.name, formated_amount(self.amount)]
        )

    def validate_self(self):
        self.is_str('id', self.id)
        self.is_str('project', self.project)
        self.is_str('category', self.category)
        self.is_str('name', self.name)
        self.is_optional_str('description', self.description)
        self.validate_amount(self.amount)

    def new_amount(self, min, max):
        return np.array((min, max))


class Project(object):
    def __init__(self, units):
        self.units = units
        self.name = self.project_name_set().pop()
        self.categories = self.categories_set()

        self.validate_self()

    def print_summary(self):
        print('Project summary - %s:' % self.name)
        for cat in self.categories:
            print('  Category summary - %s' % cat)
            units_in_cat = self.in_category(cat)
            for u in units_in_cat:
                print('    - %s' % u.summary_str())
            print('    Subtotal: %s'
                  % formated_amount(self.category_total(cat)))
        print('Total: %s' % formated_amount(self.total()))

    def in_category(self, category):
        return [u for u in self.units if u.category == category]

    def total(self):
        return self.calc_total(self.units)

    def category_total(self, category):
        units_in_cat = self.in_category(category)
        return self.calc_total(units_in_cat)

    def calc_total(self, sub_units):
        t = sum([u.amount for u in sub_units])
        return t

    def project_name_set(self):
        return unique([u.project for u in self.units])

    def categories_set(self):
        return unique([u.category for u in self.units])

    def validate_self(self):
        names = self.project_name_set()
        if len(names) != 1:
            raise RuntimeError('Uncertain project name: %s' % str(names))


def formated_amount(t):
    return '${0:,.1f} - ${1:,.1f}'.format(*t)


def unique(seq):
    seen = set()
    unique = [x for x in seq if not (x in seen or seen.add(x))]
    return unique


def project_from_csv(file_path):
    data = pd.read_csv(file_path)
    units = [unit_from_row(r) for _, r in data.iterrows()]
    project = Project(units)
    return project


def unit_from_row(r):
    return ProjectUnit(*r)
