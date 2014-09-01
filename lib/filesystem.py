def file_to_string(path, mode="rb", do_repr=False):
    with open(path, mode) as f:
        buf = f.read()
    if do_repr:
        buf = repr(buf).strip("'")
    return buf

def string_to_file(string, path, mode="wb", do_eval=False):
    if do_eval:
        # Do repr to avoid the binary string.
        string = eval(repr(string))
    with open (path, mode) as f:
        f.write(string)
    return None

def listdir(path):
    import os
    return os.listdir(path)

def basename(path):
    import os.path
    return os.path.basename(path)
