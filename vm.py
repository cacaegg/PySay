import __builtin__
import re
import datetime
from primitives.operations import *
from primitives.types import *
from primitives.keywords import *
from lib import filesystem
from lib import machine
from lib.usbx_handler import *
import vmconfig
import types

global_bindings = {}

def init_env():
    global global_bindings
    global_bindings = {}
    filter_list = ("open", "file", "slice", "len", "eval", "zip",
                   "max", "min", "dir")
    builtin_func_dic = map(
            lambda fn: {fn:getattr(__builtin__, fn)},
            filter(lambda fn: fn not in filter_list,
                   dir(__builtin__)))
    map(global_bindings.update, builtin_func_dic)
    global_bindings.update({
        "cond" : Cond,
        "otherwise" : Otherwise,
        "Lambda" : CLambda,
        "define" : Define,
        "data" : Data,
        "dict" : lambda args: Dict()(args),
        "unquote" : my_eval,
        "begin" : Begin,
        "update" : Update,
        "expand" : Expand,
        })
    global_bindings.update({
        "add" : add,
        "sub" : sub,
        "mul" : mul,
        "index" : index,
        "slice" : pys_slice,
        "apply" : my_apply,
        "logical_and" : logical_and,
        "logical_or" : logical_or,
        "less_than" : less_than,
        "less_equal" : less_equ,
        "equal" : equal,
        "greater_equal" : greater_equal,
        "greater" : greater,
        "load" : load,
        "dot" : dot,
        "pysay_in" : is_in,
        "str" : to_string,
        })
    global_bindings.update({
        "usandbox" : usandbox_handler,
        "datetime" : datetime,
        })
    global_bindings.update({
        "file_to_string" : filesystem.file_to_string,
        "string_to_file" : filesystem.string_to_file,
        "listdir" : filesystem.listdir,
        "basename" : filesystem.basename,
        })
    global_bindings.update({
        "machine" : Machine,
        "connect" : machine.connect,
        "execute" : machine.execute,
        "display" : machine.display,
        "sleep" : machine.sleep,
        "vmstatus": machine.vmstatus,
        })

def load(pysfile):
    with open(pysfile) as pys:
        statements = pys.read().strip()
        for stat in statements.split("#eos"):
            if len(stat) != 0:
                start_exec(stat)

def start_exec(expr):
    if vmconfig.DEBUG:
        print "start_exec:", expr
    my_expr = eval(expr, global_bindings)
    return my_eval(my_expr, [global_bindings,])

def eval_arglist(arguments, env):
    results = []
    for arg in arguments:
        if is_expand(arg):
            arg = first(rest(arg))
            if is_identifier(arg):
                arg = handle_identifier(arg, env)
                results += arg
            else:
                results += my_eval(arg, env)
        else:
            results.append(my_eval(arg, env))
    return tuple(results)

def bind_func_args(func, arglist):
    new_bindings = {}
    expand_identifier = None
    if len(func.args) > 0 and is_expand(func.args[-1]):
        expand_identifier = first(rest(func.args[-1]))
        param_list = [expand_identifier] * len(arglist)
        param_list[0:len(func.args)-1] = func.args[0:-1]
        new_bindings[expand_identifier] = []
    else:
        param_list = func.args
    for parameter, argument in zip(param_list, arglist):
        if parameter == expand_identifier:
            new_bindings[expand_identifier] += [argument]
        else:
            new_bindings.update({parameter : argument})
    return new_bindings

def my_apply(action, arguments, env):
    if vmconfig.DEBUG:
        print "my_apply:", action, arguments

    if action is my_apply:
        action = first(arguments)
        arglist = rest(first(rest(arguments)))
        # print "apply!!:", action, arglist
        if len(arglist) == 1:
            return my_apply(action, arglist, env)
        else:
            return my_apply(action, arglist, env)

    arglist = eval_arglist(arguments, env)

    if is_lambda(action) or is_identifier(action) or type(action) is tuple:
        action = my_eval(action, env)
        # print "function", action, arglist

    if type(action) is Function:
        env = action.env + env
        new_bindings = bind_func_args(action, arglist)
        # if is_expand(action.args[-1]):
        #     print "!!!!!!", new_bindings
        map(lambda k,v: new_bindings.update({k:v}), action.args, arglist)
        new_env = extend_env(env, new_bindings)
        result = None
        for statement in action.body:
            result = my_eval(statement, new_env)
        return result
    elif is_primitive(action) or action in [Machine, Dict]:
        # print action, arglist
        return action(*arglist)
    else:
        msg = "Apply Error: action(%s) arguments(%s)" % (action, arguments)
        raise Exception(msg)

def my_eval(expr, env):
    if vmconfig.DEBUG:
        print "my_eval:", expr
    if type(expr) is int:
        return handle_int(expr)
    elif type(expr) is bool:
        return expr
    elif type(expr) is types.TypeType:
        return expr
    elif type(expr) is types.ModuleType:
        return expr
    elif expr is None:
        return None
    elif is_identifier(expr):
        return handle_identifier(expr, env)
    elif type(expr) is str:
        return handle_str(expr, env)
    elif is_primitive(expr):
        return expr
    elif is_data(expr):
        return handle_data(expr, env)
    elif is_lambda(expr):
        return handle_lambda(rest(expr), env)
    elif is_cond(expr):
        return handle_cond(get_cond_lines(expr), env)
    elif is_define(expr):
        return handle_define(get_define_identifier(expr),
                             get_define_body(expr), env)
    elif is_begin(expr):
        return handle_begin(rest(expr), env)
    elif is_update(expr):
        return handle_update(rest(expr), env)
    elif type(expr) is tuple:
        action = first(expr)
        args = rest(expr)
        return my_apply(action, args, env)
    else:
        raise Exception("Unknown Expression %s" % expr)

"""
Handlers
"""
handle_int = lambda expr: expr

def handle_str(expr, env):
    # print "handle_str", expr
    def subst(mat):
        # print "subst", mat.groups()[0]
        new_expr = mat.groups()[0]
        total_no_found = 0
        env_depth = len(env)
        for bindings in env:
            try:
                # print "eval_in_binding", new_expr
                new_expr = my_eval(eval(new_expr, global_bindings), [bindings,])
                break
            except NoIdentifierFound:
                total_no_found += 1
                if total_no_found == env:
                    raise
            except SyntaxError:
                new_expr = '"' + new_expr + '"'
                new_expr = my_eval(eval(new_expr, global_bindings), [bindings,])
            except TypeError:
                # Ignore if we can't do eval anymore
                break
        # print "subst return", new_expr
        return str(new_expr)
    def exe_unquote(mat):
        new_expr = mat.groups()[0].strip("'")
        return str("'"+my_eval(new_expr, env)+"'")
    pat = re.compile("~\((.*?)\)~")
    result = re.sub(pat, subst, expr)
    unq = re.compile("\(unquote , (.*?) ,\)")
    return re.sub(unq, exe_unquote, result)

def handle_data(expr, env):
    results = []
    for sub_expr in rest(expr):
        results.append(my_eval(sub_expr, env))
    return results

def handle_lambda(expr, env):
    parameters = first(expr)
    body = rest(expr)
    return Function(parameters, body, env)

def handle_identifier(expr, env):
    for e in env:
        if expr in e.keys():
            return e[expr]
    raise NoIdentifierFound("Unknown Identifier %s" % get_identifier(expr))

def handle_cond(lines, env):
    line = first(lines)
    if is_otherwise(line):
        return my_eval(cond_line_action(line), env)
    elif my_eval(cond_line_quiz(line), env) == True:
        return my_eval(cond_line_action(line), env)
    else:
        return handle_cond(rest(lines), env)

def handle_define(ident, body, env):
    result = my_eval(body, env)
    first(env).update({ident : result})
    return None

def handle_begin(sequences, env):
    for seq in sequences[:-1]:
        my_eval(seq, env)
    return my_eval(sequences[-1], env)

def handle_update(expr, env):
    iden = update_identifier(expr)
    val = my_eval(update_value(expr), env)
    for bindings in env:
        if iden in bindings.keys():
            bindings[iden] = val
            return
    raise NoIdentifierFound("Can't update %s in environment" % iden)
