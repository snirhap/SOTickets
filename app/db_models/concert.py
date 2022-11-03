from app import db

class Concert(db.Model):
    __tablename__ = "concerts"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    tickets_available = db.Column(db.Integer)
    band_id = db.Column(db.Integer, db.ForeignKey("bands.id", ondelete="CASCADE"))
    band = db.relationship("Band", foreign_keys=band_id, back_populates="concerts")

    gates = db.relationship("Gate", back_populates="concert")

    def __init__(self, band_id, date, tickets_available) -> None:
        self.band_id = band_id
        self.date = date
        self.tickets_available = tickets_available
