from metareserve.reservation import ReservationRequest as _ReservationRequest

class GENINode(object):
    '''Trivial object holding information about a GENI node.
    Args:
        name (str): Hostname for this node.
        hw_type (str): Hardware type. Check the available hardware types and their specifications at (e.g.) https://www.cloudlab.us/resinfo.php.
        image (str): OS image to boot on node.'''
    def __init__(self, name, hw_type, image):
        self._name = name
        self._hw_type = hw_type
        self._image = image

    @property
    def name(self):
        return self._name

    @property
    def hw_type(self):
        return self._hw_type

    @property
    def image(self):
        return self._image

    @staticmethod
    def from_string(self, string):
        '''Constructs a `GENINode` from a string.'''
        return GENINode(*string.split('|'))

    def __str__(self):
        return '|'.join([self._name, self._hw_type, self._image])



class GENIReservationProfile(object):
    '''Trivial object to hold a reservation profile.'''
    def __init__(self):
        self.nodeprofiles = dict()

    @property
    def nodes(self):
        return self.nodeprofiles.values()
    
    def add(self, node):
        '''Add a `GENINodeProfile` to the reservation profile.'''
        self.nodeprofiles[node.name] = node
    
    @staticmethod
    def from_string(self, string):
        '''Constructs a `GENIReservationProfile` from a string.'''
        val = GENIReservationProfile()
        for line in string.strip().split('\n'):
            val.add(GENINode.from_string(line))
        return val


    @staticmethod
    def make(num_nodes, hw_type, image):
        '''Constructs a `GENIReservationRequest` following standard patterns: 1 image for all nodes, 1 hw_type for all nodes, nodes named as node0, node1, ....
        Args:
            num_nodes (int): Number of nodes in profile.
            hw_type (str): Hardware specification to use.
            image (str, optional): Image to boot on each node.
        Returns:
            Constructed `GENIReservationProfile`.'''
        profile = GENIReservationProfile()
        for idx in range(num_nodes):
            profile.add(GENINode('node{}'.format(idx), hw_type, image))
        return profile

    def __str__(self):
        return '\n'.join(str(x) for x in nodes)

    def __len__(self):
        return len(self.nodeprofiles)



class GENIReservationRequest(_ReservationRequest):
    '''Object representing a regular reservation request (request nodes for X minutes).'''
    def __init__(self, duration_minutes, location, slicename, reservation_profile):
        '''Args:
            duration_minutes (int): Number of minutes to reserve nodes.
            location (str): Location for reserved nodes.
            slicename (str): Slicename to use for allocation.
            reservation_profile (GENIReservationProfile): ReservationProfile to use for allocation.'''
        super.__init__(len(reservation_profile), duration_minutes, location=location)
        if duration_minutes >= 7200:
            raise ValueError('GENI only allows to allocate for 7199 minutes or less.')
        self.nodes = None
        self.slicename = slicename


    @staticmethod
    def make(num_nodes, duration_minutes, location, hw_type, image='urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', slicename='metareserve'):
        '''Constructs a `GENIReservationRequest` following standard patterns: 1 image for all nodes, 1 hw_type for all nodes, nodes named as node0, node1, ....
        Args:
            num_nodes (int): Number of nodes in reservation.
            duration_minutes (int): Number of minutes to reserve nodes.
            location (str): Location for reserved nodes.
            hw_type (str): Hardware specification to use.
            image (str, optional): Image to boot on each node.
            slicename (str, optional): Slicename to use for allocation.
        Returns:
            Constructed `GENIReservationRequest`.'''
        profile = GENIReservationProfile.make(num_nodes, hw_type, image)
        return GENIReservationRequest(duration_minutes, location, slicename, profile)



# class GENITimeSlotReservationRequest(TimeSlotReservationRequest):
#     '''Object representing a timeslot reservation request (request nodes from datetime X, ending at datetime Y).
#     Args:
#         num_nodes (int): Number of nodes in reservation.
#         duration_start (datetime): Start time for reserved nodes.
#         duration_end (datetime): End time for reserved nodes.
#         location (str, optional): Location for reserved nodes.'''
#     def __init__(self, num_nodes, duration_start, duration_end, location=''):
#         super.__init__(num_nodes, _duration_start, _duration_end, location=location)
#         self.nodes = dict()


#     def add(self, node=None):
#         self.nodes[node.name] = node
