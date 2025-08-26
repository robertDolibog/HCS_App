from models.file_locations import FileLocation
from extensions import db  # Import db from extensions instead of app

class FileLocationRepository:
    @staticmethod
    def delete_all():
        db.session.query(FileLocation).delete()
        db.session.commit()

    @staticmethod
    def add(file_id, location):
        loc = FileLocation(file_id=file_id, location=location)
        db.session.add(loc)