from app import db, logging
from app.db_models.ticket import Ticket

logger = logging.getLogger()

def query_all_tickets_table():
    return Ticket.query.all()

def create_tickets(tickets_list: list):
    db.session.bulk_insert_mappings(Ticket, tickets_list)
    db.session.commit()
