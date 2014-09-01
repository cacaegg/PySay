class CONSTANTS:
    SYSTEM_DEFAULT = -1

def file_to_string(path, mode="text"):
    mode_dic = {"text": "r", "binary" : "rb"}

    with open(path, mode_dic[mode]) as f:
        buf = f.read()

    return repr(buf)
