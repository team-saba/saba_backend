def dumper(obj):
    try:
        return obj.to_json()
    except:
        return obj.__dict__
