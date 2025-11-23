"""
Użycie:
1) Ustaw zmienną środowiskową DATABASE_URL (przykłady poniżej).
2) Uruchom: python create_db.py
To stworzy tabele zdefiniowane w models.Base na wskazanej bazie.
"""
from models import Base
from database import engine

def create_tables():
    print("Creating tables on:", engine.url)
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    create_tables()