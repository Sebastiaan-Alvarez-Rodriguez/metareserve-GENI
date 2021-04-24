class RawConnectInfo(object):
    '''Object storing needed info to connect to physical allocated resources. Each physical node must have a unique name.'''
    def __init__(self, name, user, ip_local, ip_public, port=22):
        self.name = name
        self.user = user
        self.ip_local = ip_local
        self.ip_public = ip_public
        self.port = int(port)


    def __str__(self):
        return '|'.join([self.name, self.user, self.ip_local, self.ip_public, str(self.port)])


    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, RawConnectInfo):
            return False
        return self.name == other.name


    @staticmethod
    def from_string(string):
        return RawConnectInfo(*string.split('|'))