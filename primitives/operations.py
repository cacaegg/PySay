from keywords import *
from types import Data
"""
Constans
"""
PRIMITIVE = "primitive"
IDENTIFIER = "_pysayvm_"

"""
Operations
"""
first = lambda expr: expr[0]
rest = lambda expr: expr[1:]

get_act_type = lambda token: token[0]
get_act_func = lambda token: token[1]
get_identifier = lambda expr: expr[len(IDENTIFIER):]
get_cond_lines = lambda expr: rest(expr)
cond_line_quiz = lambda expr: first(expr)
cond_line_action = lambda expr: first(rest(expr))
get_define_identifier = lambda expr: first(rest(expr))
get_define_body = lambda expr: first(rest(rest(expr)))
update_identifier = lambda expr: expr[0]
update_value = lambda expr: expr[1]

def extend_env(env, new_bindings):
    return [new_bindings,] + env

def right_associate(func, *operands):
    opr_len = len(operands)
    if opr_len <= 1:
        raise Exception("Not enough operand: %s" % str(operands))
    elif opr_len == 2:
        return func(operands[0], operands[1])
    else:
        return func(operands[0], right_associate(func, *operands[1:]))


"""
Predicates
"""
def is_primitive(expr):
    return "__call__" in dir(expr)

def is_data(expr):
    return first(expr) is Data

def is_lambda(expr):
    if type(expr) is not tuple:
        return False
    elif len(expr) < 3:
        return False
    return first(expr) is CLambda

def is_cond(expr):
    if type(expr) is not tuple:
        return False
    elif len(expr) <= 2:
        return False
    return first(expr) is Cond

def is_otherwise(expr):
    if type(expr) is not tuple:
        return False
    elif len(expr) != 2:
        return False
    return first(expr) is Otherwise

def is_identifier(expr):
    if type(expr) is not str:
        return False
    return expr.startswith(IDENTIFIER)

def is_define(expr):
    if type(expr) is not tuple:
        return False
    elif len(expr) != 3:
        return False
    return first(expr) is Define

def is_begin(expr):
    if type(expr) is not tuple:
        return False
    return first(expr) is Begin

def is_update(expr):
    if type(expr) is not tuple:
        return False
    return first(expr) is Update

def is_expand(expr):
    if type(expr) is not tuple:
        return False
    return first(expr) is Expand

"""
Logical and Bool
"""
def add(*operands):
    return right_associate(lambda a, b: a + b, *operands)

def sub(*operands):
    return right_associate(lambda a, b: a - b, *operands)

def mul(*operands):
    return right_associate(lambda a, b: a * b, *operands)

def pys_slice(seq, start=0, end=None, step=1):
    return seq[start:end:step]

def index(seq, number):
    return seq[number]

def logical_and(*operands):
    return right_associate(lambda a, b: a and b, *operands)

def logical_or(*operands):
    return right_associate(lambda a, b: a or b, *operands)

def less_than(a, b):
    return a < b

def less_equ(a, b):
    return a <= b

def equal(a, b):
    return a == b

def greater_equal(a, b):
    return a >= b

def greater(a, b):
    return a > b

def dot(operand, member):
    return getattr(operand, member)

def is_in(element, test_set):
    return element in test_set

def to_string(expr):
    return str(expr)
