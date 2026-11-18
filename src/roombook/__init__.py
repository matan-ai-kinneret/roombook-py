"""roombook — הזמנת חדרי לימוד בספריית כנרת."""

from .models import Booking, Room
from .rules import overlaps, validate_booking
from .service import BookingError, BookingService

__all__ = ["Booking", "Room", "overlaps", "validate_booking", "BookingError", "BookingService"]
__version__ = "0.1.0"
