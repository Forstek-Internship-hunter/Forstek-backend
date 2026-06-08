from app.core.database import engine, Base
from app.models.models import Offer, Application, UserProfile, UserExperience
from app.models.user import User

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

if __name__ == "__main__":
    init_db()