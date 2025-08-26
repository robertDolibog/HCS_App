from models.file import File
from extensions import db  # Import db from extensions instead of app

class FileRepository:
    @staticmethod
    def delete_all():
        db.session.query(File).delete()
        db.session.commit()

    @staticmethod
    def get_or_create(file_id, **kwargs):
        file = File.query.get(file_id)
        if not file:
            file = File(id=file_id, **kwargs)
            db.session.add(file)
        return file

    @staticmethod
    def commit():
        db.session.commit()