

def spop_to_str(res):
    if res is not None:
        return res.decode('utf-8')
    return None


def pop_to_str(res):
    print(f"Got res: '{res}'")
    if res is not None and len(res) >= 2:
        if res[1] is not None:
            return res[1].decode('utf-8')
    return None
