def assoc_to_dict(assoc):
    result = {}
    for r in assoc:
        result.update({r[0]:r[1]})
    return result


