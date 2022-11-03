from datetime import datetime
from random import choice

from app import app, logging, redis_manager

from app.db_actions import concerts as concerts_db_actions
from app.db_actions import seating_plan as seating_plan_db_actions
from app.db_actions import tickets as tickets_db_actions
from app.db_actions.bands import get_band_details
from app.db_actions import users as user_db_actions

from app.db_models.gate import SeatingType
from app.dto_models.aisle import AisleDTO, BaseAisleDTO
from app.dto_models.concert import BaseConcertDTO, ConcertDTO, SeatingPlanDTO
from app.dto_models.gate import BaseGateDTO, GateDTO
from app.dto_models.seat import BaseSeatDTO, SeatDTO
from app.dto_models.ticket import BaseTicketDTO, TicketDTO

from app.static.exceptions import KeyNotFound
from flask_jwt_extended import get_jwt_identity, jwt_required

logger = logging.getLogger()
REDIS_SAVE_TICKETS_PREFIX = "save_tickets"

def create_new_concert(request_data: dict):
    new_concert = BaseConcertDTO(request_data["band_id"], datetime.strptime(request_data["date"], '%d/%m/%Y'), request_data["tickets_available"])
    concerts_db_actions.create_concert(new_concert)

# @jwt_required()
def get_concert_details(concert_id: int):
    concert = concerts_db_actions.get_concert_details(concert_id=concert_id)
    if concert:
        band = get_band_details(concert.band_id)
        concert_seating_types = [row["seating_type"] for row in seating_plan_db_actions.get_concert_gate_seating_types(concert_id)]
        concert_dto = ConcertDTO(concert.band_id, concert.date, concert.tickets_available, concert.id, band.name, concert_seating_types)
        return concert_dto
    else:
        raise KeyNotFound(f"Concert doesn't exist")

# lazy creation
def create_seating_plan_for_concert(concert_id: int, request_data: dict):
    concert = concerts_db_actions.get_concert_details(concert_id=concert_id)
    if concert:
        number_of_standing_gates = request_data.get("number_of_standing_gates", 0)
        standing_per_gate = request_data.get("standing_per_gate", 0)
        price_per_non_seated = 10

        number_of_virtual_gates = request_data.get("number_of_virtual_gates", 0)
        virtual_per_gate = request_data.get("virtual_per_gate", 0)
        price_per_non_seated = 10

        number_of_seated_gates = request_data.get("number_of_seated_gates", 0)
        aisles_per_gate = request_data.get("aisles_per_seated_gate", 0)
        seats_per_row = request_data.get("seats_per_row", 0)
        price_per_seated = 20

        total_number_of_gates = number_of_standing_gates + number_of_virtual_gates + number_of_seated_gates

        gates_list = []
        aisles_list = []
        seats_list = []
        if (number_of_standing_gates * standing_per_gate) + (number_of_virtual_gates * virtual_per_gate) + (number_of_seated_gates * aisles_per_gate * seats_per_row) <= concert.tickets_available:
            # Bulk insert gates
            for _ in range(number_of_standing_gates):
                new_gate_dto = BaseGateDTO(concert_id, SeatingType.standing, standing_per_gate, total_number_of_gates)
                gates_list.append(new_gate_dto.asdict())
                total_number_of_gates -= 1

            for _ in range(number_of_virtual_gates):
                new_gate_dto = BaseGateDTO(concert_id, SeatingType.virtual, virtual_per_gate, total_number_of_gates)
                gates_list.append(new_gate_dto.asdict())
                total_number_of_gates -= 1

            for _ in range(number_of_seated_gates):
                new_gate_dto = BaseGateDTO(concert_id, SeatingType.seated, aisles_per_gate * seats_per_row, total_number_of_gates)
                gates_list.append(new_gate_dto.asdict())
                total_number_of_gates -= 1
            
            seating_plan_db_actions.create_gates(gates_list)
            
            # Bulk insert aisles
            for seating_type in list(SeatingType):
                seat_type_gates = seating_plan_db_actions.get_concert_gates(concert_id=concert_id, seating_type=seating_type)
                concert_gate_ids = [gate.id for gate in seat_type_gates]
                for gate_id in concert_gate_ids:
                    if seating_type == SeatingType.seated:
                        for aisle_number in range(1, aisles_per_gate + 1):
                            new_aisle_dto = BaseAisleDTO(gate_id, aisle_number)
                            aisles_list.append(new_aisle_dto.asdict())
                    else:
                        new_aisle_dto = BaseAisleDTO(gate_id, 1)
                        aisles_list.append(new_aisle_dto.asdict())
            
            seating_plan_db_actions.create_aisles(aisles_list)
            
            # Bulk insert seats
            for seating_type in list(SeatingType):
                seat_type_gates = seating_plan_db_actions.get_concert_gates(concert_id=concert_id, seating_type=seating_type)
                gates_aisles = seating_plan_db_actions.get_gate_aisles([gate.id for gate in seat_type_gates])
                number_of_seats = seats_per_row if seating_type == SeatingType.seated else virtual_per_gate if seating_type == SeatingType.virtual else standing_per_gate
                seat_price = price_per_seated if seating_type == SeatingType.seated else price_per_non_seated
                for aisle in gates_aisles:  
                    for seat_number in range(1, number_of_seats + 1):
                        new_seat_dto = BaseSeatDTO(aisle.id, seat_number, True, seat_price)
                        seats_list.append(new_seat_dto.asdict())

            seating_plan_db_actions.create_seats(seats_list)

        return gates_list
    else:
        raise Exception("Concert doesn't exist")

def get_all_secured_tickets_for_concert(concert_id: int, seating_type: SeatingType, gate_id: int = None, user_name: str = None):
    result = []
    users_secured_seats = redis_manager.scan_within_pattern(f"{REDIS_SAVE_TICKETS_PREFIX}:{concert_id}:{seating_type}*{f':{gate_id}*' if gate_id else ''}{f':{user_name}*' if user_name else ''}")
    logger.info(f'users_secured_seats: {users_secured_seats}')

    for user in users_secured_seats:
        result.extend(redis_manager.lrange_key(user))
    
    return [int(seat) for seat in result]

def get_seating_plan_for_concert(concert_id: int):
    gates_result = []
    gates_available_tickets = 0
    purchased_tickets = 0

    concert_gates = concerts_db_actions.get_concert_gates(concert_id)
    for gate in concert_gates:
        gates_available_tickets += gate.number_of_seats
        gate_aisles = []
        for aisle in gate.aisles:
            aisle_seats = []
            for seat in aisle.seats:
                if not seat.available:
                    purchased_tickets += 1
                aisle_seats.append(SeatDTO(aisle.id, seat.seat_number, seat.available, seat.price, seat.id).asdict())
            gate_aisle = AisleDTO(gate.id, aisle.aisle_number, aisle.id, aisle_seats)
            gate_aisles.append(gate_aisle.asdict())
        gates_result.append(GateDTO(concert_id, gate.seating_type, gate.number_of_seats, gate.gate_number, gate.id, gate_aisles).asdict())
    
    # calculate saved tickets for concert <id> in cache
    saved_tickets_in_cache = 0
    for type in list(SeatingType):
        secured_tickets = get_all_secured_tickets_for_concert(concert_id, type)
        saved_tickets_in_cache += len(secured_tickets)

    return SeatingPlanDTO(number_purchased_tickets=purchased_tickets, 
                         number_of_available_tickets=gates_available_tickets - purchased_tickets - saved_tickets_in_cache, 
                         gates=gates_result)

def get_non_seated_gate_free_seats_in_db(gate_id: int):
    gate_aisle = seating_plan_db_actions.get_gate_aisles([gate_id])[0]
    return seating_plan_db_actions.get_aisle_free_seats(gate_aisle.id)

def check_availabilty_for_non_seated(concert_id: int, non_seated_tickets: list, seating_type: SeatingType, user_name: str = None):
    if non_seated_tickets:
        for gate_request in non_seated_tickets:
            tickets_requested = gate_request["number_of_tickets"]
            gate_id = gate_request["gate"]

            # Check gate type
            db_gate = seating_plan_db_actions.get_gate_details(gate_id)
            if not (db_gate and seating_plan_db_actions.get_gate_seating_type(gate_id).seating_type == seating_type):
                raise Exception("Wrong gate seating type")

            # Get secured non-seats in cache
            gate_secured_in_cache = get_all_secured_tickets_for_concert(concert_id, seating_type, gate_id)
            
            # Get all seats information from DB regarding available seats in this gate
            free_seats = get_non_seated_gate_free_seats_in_db(gate_request["gate"])

            if user_name:
                # Buying process

                # Get current_user secured tickets for this gate
                # Check if new tickets were requested
                # e.g. user X saved 3 tickets before and when buying he asked for 4, then `new_tickets_requested` will be 1
                user_gate_secured_in_cache = get_all_secured_tickets_for_concert(concert_id, seating_type, gate_id, user_name)
                new_tickets_requested = tickets_requested - len(user_gate_secured_in_cache)
                if not (new_tickets_requested + len(gate_secured_in_cache)) <= len(free_seats):
                    return False
            else:
                if not (tickets_requested + len(gate_secured_in_cache)) <= len(free_seats):
                    return False
    return True

def check_availabilty_for_seated(concert: dict, requested_seated_tickets: list, user_name: str = None):
    if requested_seated_tickets:
        logger.info(f'seated_tickets: {requested_seated_tickets}')

        # Check if seated_tickets list are marked as available in DB
        available_seats_in_db = seating_plan_db_actions.get_available_seats_from_seats_list(requested_seated_tickets)
        if len(available_seats_in_db) == len(requested_seated_tickets):
            # Seats are available in DB, check if they are being secured in cache
            secured_tickets = get_all_secured_tickets_for_concert(concert.id, SeatingType.seated)
            logger.info(f'secured_tickets: {secured_tickets}')

            if user_name:
                # Buying process
                user_secured_seats = get_all_secured_tickets_for_concert(concert.id, SeatingType.seated, user_name=user_name)
                new_requested_seats = list(set(requested_seated_tickets) - set(user_secured_seats)) + list(set(user_secured_seats) - set(requested_seated_tickets))
                logger.info(f'user_secured_seats: {user_secured_seats}')
                logger.info(f'new_requested_seats: {new_requested_seats}')

                if any(seat in new_requested_seats for seat in secured_tickets):
                    raise Exception("Not all seats requested were available, some are being secured")

            elif any(seat in requested_seated_tickets for seat in secured_tickets):
                raise Exception("Not all seats requested were available, some are being secured")
            return True
        else:
            return False
    return True

def generate_available_seats_for_non_seated_gate(gate_request_data: dict, seating_type: SeatingType, concert_id: int, user_name: str = None):
    secured_in_cache = get_all_secured_tickets_for_concert(concert_id, seating_type, gate_request_data["gate"])
    free_seats = get_non_seated_gate_free_seats_in_db(gate_request_data["gate"])
    if user_name:
        # Buying process
        user_secured_seats = get_all_secured_tickets_for_concert(concert_id, seating_type, gate_request_data["gate"], user_name=user_name)
        if user_secured_seats:
            new_tickets_requested = gate_request_data["number_of_tickets"] - len(user_secured_seats)
            if gate_request_data["number_of_tickets"] <= len(user_secured_seats):
                # User asked less or excatly as he secured
                return user_secured_seats[:gate_request_data["number_of_tickets"]]
            else:
                # User asked more than he secured, add the diff to already secured seats
                return user_secured_seats + [int(seat.id) for seat in free_seats if int(seat.id) not in secured_in_cache][:new_tickets_requested]
    selected_free_seats = [int(seat.id) for seat in free_seats if int(seat.id) not in secured_in_cache][:gate_request_data["number_of_tickets"]]
    return selected_free_seats

@jwt_required()
def save_tickets(concert_id: int, request_data: dict):
    try:
        concert = concerts_db_actions.get_concert_details(concert_id=concert_id)
        if concert:
            current_user = get_jwt_identity()
            standing_tickets = request_data.get("standing", None)
            virtual_tickets = request_data.get("virtual", None)
            seats_list = request_data.get("seats", None)
            
            # Check availabilty for standing and virtual
            requested_standing = check_availabilty_for_non_seated(concert_id, standing_tickets, SeatingType.standing)
            requested_virtual = check_availabilty_for_non_seated(concert_id, virtual_tickets, SeatingType.virtual)
            requested_seated = check_availabilty_for_seated(concert, seats_list)
            
            if requested_standing and requested_virtual and requested_seated:
                if seats_list:
                    redis_manager.lpush_key_value(f'{REDIS_SAVE_TICKETS_PREFIX}:{concert_id}:{SeatingType.seated}:{current_user}', seats_list, app.config["SAVE_TICKETS_DURATION_SECONDS"])
                if standing_tickets:
                    for gate_request_data in standing_tickets:
                        available_seats = generate_available_seats_for_non_seated_gate(gate_request_data, SeatingType.standing, concert_id)
                        redis_manager.lpush_key_value(f'{REDIS_SAVE_TICKETS_PREFIX}:{concert_id}:{SeatingType.standing}:{gate_request_data["gate"]}:{current_user}', available_seats, app.config["SAVE_TICKETS_DURATION_SECONDS"])
                if virtual_tickets:
                    for gate_request_data in virtual_tickets:
                        available_seats = generate_available_seats_for_non_seated_gate(gate_request_data, SeatingType.virtual, concert_id)
                        redis_manager.lpush_key_value(f'{REDIS_SAVE_TICKETS_PREFIX}:{concert_id}:{SeatingType.virtual}:{gate_request_data["gate"]}:{current_user}', available_seats, app.config["SAVE_TICKETS_DURATION_SECONDS"])
            else:
                raise Exception("There was a problem with seats picking, perhaps requested more tickets than available")
        else:
            raise Exception("Concert doesn't exist")
    except Exception as err:
        raise

@jwt_required()
def buy_tickets(concert_id: int, request_data: dict):
    try:
        new_tickets = []
        concert = concerts_db_actions.get_concert_details(concert_id=concert_id)
        if concert:
            current_user = get_jwt_identity()

            standing_tickets = request_data.get("standing", None)
            virtual_tickets = request_data.get("virtual", None)
            seats_list = request_data.get("seats", None)

            requested_standing = check_availabilty_for_non_seated(concert_id, standing_tickets, SeatingType.standing, current_user)
            requested_virtual = check_availabilty_for_non_seated(concert_id, virtual_tickets, SeatingType.virtual, current_user)
            requested_seated = check_availabilty_for_seated(concert, seats_list, current_user)

            if requested_standing and requested_virtual and requested_seated:
                user = user_db_actions.get_user_by_username(current_user)
                if seats_list:
                    for seat in seats_list:
                        db_seat = seating_plan_db_actions.get_seat_details(seat)
                        new_ticket = BaseTicketDTO(user.id, seat, db_seat.price)
                        new_tickets.append(new_ticket.asdict())
                        seating_plan_db_actions.update_seat_availability(seat, False)

                if standing_tickets:
                    for gate_request_data in standing_tickets:
                        available_seats = generate_available_seats_for_non_seated_gate(gate_request_data, SeatingType.standing, concert_id, current_user)
                        for seat in available_seats:
                            db_seat = seating_plan_db_actions.get_seat_details(seat)
                            new_ticket = BaseTicketDTO(user.id, seat, db_seat.price)
                            new_tickets.append(new_ticket.asdict())
                            seating_plan_db_actions.update_seat_availability(seat, False)

                if virtual_tickets:
                    for gate_request_data in virtual_tickets:
                        available_seats = generate_available_seats_for_non_seated_gate(gate_request_data, SeatingType.virtual, concert_id, current_user)
                        for gate_request_data in virtual_tickets:
                            available_seats = generate_available_seats_for_non_seated_gate(gate_request_data, SeatingType.virtual, concert_id)
                            for seat in available_seats:
                                db_seat = seating_plan_db_actions.get_seat_details(seat)
                                new_ticket = BaseTicketDTO(user.id, seat, db_seat.price)
                                new_tickets.append(new_ticket.asdict())
                                seating_plan_db_actions.update_seat_availability(seat, False)

                # Insert to DB
                tickets_db_actions.create_tickets(new_tickets)

                # Clear cache for user
                for key_cache in redis_manager.scan_within_pattern(f'{REDIS_SAVE_TICKETS_PREFIX}:{concert_id}*{current_user}*'):
                    redis_manager.delete_key(key_cache)

                return 'OK'
            else:
                raise Exception("There was a problem with seats picking, perhaps requested more tickets than available")
        else:
            raise Exception("Concert doesn't exist")
    except Exception as err:
        raise
        