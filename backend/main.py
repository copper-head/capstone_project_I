from db.database import DatabaseManager
from api import create_app


# RUN THE APP
db_manager = DatabaseManager()
app = create_app(db_manager)



