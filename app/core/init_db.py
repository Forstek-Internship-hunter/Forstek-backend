from app.core.database import engine, Base
from app.models.models import Offer, Application

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

if __name__ == "__main__":
    init_db()