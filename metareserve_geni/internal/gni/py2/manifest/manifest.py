from enum import Enum
import datetime
import pprint
import xmltodict

from connectinfo import RawConnectInfo


class ManifestType(Enum):
    CREATE_SLIVER = 0
    RENEW_OR_LIST_SLIVER = 1


class Manifest(object):
    '''Object to store parsed manifest'''

    def __init__(self, manifest, do_parse=True):
        self.data = xmltodict.parse(manifest.text) if do_parse else manifest
        if self.__has_indices('rspec', 'node', 0):
            self.__type = ManifestType.CREATE_SLIVER
            self.__num_nodes = len(self.data['rspec']['node'])
        else:
            self.__type = ManifestType.RENEW_OR_LIST_SLIVER
            self.__num_nodes = 1


    @property
    def manifest_type(self):
        return self.__type

    @property
    def num_nodes(self):
        return self.__num_nodes

    @property
    def expiration(self):
        tmp = self.data['rspec']['@expires'] if ManifestType.CREATE_SLIVER else self.data['rspec']['pg_expires']
        return datetime.datetime.strptime(tmp, '%Y-%m-%dT%H:%M:%SZ')
    

    def __len__(self):
        return self.__num_nodes


    def __str__(self):
        return str(self.data)


    def __repr__(self):
        return self.__str__()

    def print_full(self):
        pprint.pprint(self.data)

    def __has_indices(self, *indices):
        ptr = self.data
        try:
            for x in indices:
                ptr = ptr[x]
            return True
        except KeyError as e:
            return False


    def get_connect_info(self):
        '''Returns iterable of `RawConnectInfo`:(name, user, ip_local, ip_public, port) for all found nodes'''
        if self.__type == ManifestType.CREATE_SLIVER:
            return (RawConnectInfo(
                str(self.data['rspec']['node'][idx]['@client_id']),
                str(self.data['rspec']['node'][idx]['services']['login']['@username']),
                str(self.data['rspec']['node'][idx]['interface']['ip']['@address']),
                str(self.data['rspec']['node'][idx]['host']['@ipv4']),
                str(self.data['rspec']['node'][idx]['services']['login']['@port'])) for idx in range(self.__num_nodes))
        else:
            name = str(self.data['rspec']['node']['@client_id'])
            user = str(self.data['rspec']['node']['services']['login']['@username'])
            ip_local = str(self.data['rspec']['node'][idx]['interface']['ip']['@address'])
            ip_public = str(self.data['rspec']['node']['host']['@ipv4'])
            port = str(self.data['rspec']['node']['services']['login']['@port'])
            return [RawConnectInfo(name, user, ip_local, ip_public, port)]
