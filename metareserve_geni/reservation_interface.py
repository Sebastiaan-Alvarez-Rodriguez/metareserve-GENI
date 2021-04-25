
from metareserve.reservation import ReservationWait as _ReservationWait
import metareserve.ReservationInterface as _BaseInterface
import internal.gni.py2bridge as _py2bridge

class GENIReservationInterface(_BaseInterface):

    def reserve(reservation_request):
        '''Perform a reservation, as specified by the reservation request.
        Must return immediately without blocking.
        Time-consuming reservation systems should use a separate thread for reservation logic.
        Args:
            reservationRequest (ReservationRequest): Object containing request information.

        Returns:
            ReservationWait object.'''
        if (not isinstance(reservation_request, GENIReservationRequest)) and not isinstance(reservation_request, GENITimeSlotReservationRequest):
            raise ValueError('Need a GENIReservationRequest or GENITimeSlotReservationRequest to reserve. Found "{}".'.format(type(reservation_request)))
        expiration = reservation_request.duration_minutes if isinstance(reservation_request, GENIReservationRequest) else reservation_request.duration_end
        return _ReservationWait(_py2bridge.allocate, expiration, reservation_request)


    def stopReservation(reservation):
        '''Stops a reservation.
        Must return immediately without blocking.
        Time-consuming reservation systems should use a separate thread for reservation logic.
        Args:
            reservation (Reservation): Object containing reservation.

        Returns:
            Nothing.'''
        pass