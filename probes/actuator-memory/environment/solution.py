def predict(commands):
    """Initial static fit to the provided increasing sweep."""
    r=.173
    return [max(x-r,0) if x>=0 else min(x+r,0) for x in commands]
