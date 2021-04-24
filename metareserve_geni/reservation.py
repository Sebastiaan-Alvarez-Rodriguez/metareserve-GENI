from metareserve.reservation import ReservationRequest as _ReservationRequest

class GENINode(object):
    '''Trivial object holding information about GENI nodes.
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




class GENIReservationRequest(_ReservationRequest):
    '''Object representing a regular reservation request (request nodes for X minutes).'''
    def __init__(self, num_nodes, duration_minutes, location, slicename):
        '''Args:
            num_nodes (int): Number of nodes in reservation.
            duration_minutes (int): Number of minutes to reserve nodes.
            location (str): Location for reserved nodes.
            slicename (str): Slicename to use for allocation.'''
        super.__init__(num_nodes, duration_minutes, location=location)
        if duration_minutes >= 7200:
            raise ValueError('GENI only allows to allocate for 7199 minutes or less.')
        self.nodes = {idx: GENINode(hw_type, )}
        self.slicename = slicename


    def add(self, node):
        '''Add a node to the request.'''
        self.nodes[node.name] = node


    @staticmethod
    def make(num_nodes, duration_minutes, location, hw_type, image='urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', slicename='metareserve'):
        '''Constructs a `GENIReservationRequest` following standard patterns.
        Args:
            num_nodes (int): Number of nodes in reservation.
            duration_minutes (int): Number of minutes to reserve nodes.
            location (str): Location for reserved nodes.
            hw_type (str): Hardware specification to use.
            image (str, optional): Image to boot on each node.
            slicename (str, optional): Slicename to use for allocation.'''
        val = GENIReservationRequest(num_nodes, duration_minutes, location, slicename)
        for idx in range(num_nodes):
            val.add(GENINode('node{}'.format(idx), hw_type, image))
        return val



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
