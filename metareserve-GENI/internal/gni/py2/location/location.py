import geni.aggregate.apt
import geni.aggregate.cloudlab
import geni.aggregate.protogeni

mapping = {
    geni.aggregate.cloudlab.Clemson.name: geni.aggregate.cloudlab.Clemson,
    geni.aggregate.cloudlab.Utah.name: geni.aggregate.cloudlab.Utah,
    geni.aggregate.cloudlab.Wisconsin.name: geni.aggregate.cloudlab.Wisconsin,
    geni.aggregate.apt.Apt.name: geni.aggregate.apt.Apt,
    geni.aggregate.protogeni.UTAH_PG.name: geni.aggregate.protogeni.UTAH_PG,
    geni.aggregate.protogeni.UTAH_PG.name: geni.aggregate.protogeni.UTAH_PG
}


def location_get(obj):
    if isinstance(obj, geni.aggregate.protogeni.PGCompute):
        return obj
    if isinstance(obj, str):
        lower = obj.lower()
        if not lower in mapping:
            raise KeyError('Cannot find location for given string "{}". Options: {}'.format(lower, mapping.keys()))
        return mapping[lower]
    else:
        raise RuntimeError('Cannot find location for object of type "{}"'.format(type(obj)))


def location_str(obj):
    return obj.name