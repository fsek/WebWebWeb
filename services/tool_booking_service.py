from db_models.tool_booking_model import ToolBooking_DB


# This method takes the bookings that might clash with your booking
# and returns how many tools are booked at the "booking peak".
def max_booked(bookings: list[ToolBooking_DB]):
    # The idea is that the booking peak must occur when one booking has just started
    # We check the amount that is booked at the beginning of each booking, and return the maximum
    max_booked = 0
    for starting_booking in bookings:
        booked_amount = 0
        for booking in bookings:
            if booking.start_time <= starting_booking.start_time and starting_booking.start_time < booking.end_time:
                booked_amount += booking.amount
        if max_booked < booked_amount:
            max_booked = booked_amount

    return max_booked
