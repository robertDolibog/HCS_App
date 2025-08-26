from flask import Blueprint, jsonify
from Services.sync_service import SyncService

sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/sync', methods=['POST'])
def sync():
    count = SyncService().run()
    return jsonify({'files_processed': count}), 200

@sync_bp.route('/files', methods=['GET'])
def list_files():
    from models.file import File  
    files = File.query.all()
    result = []
    for f in files:
        result.append({
            'id': str(f.id),
            'name': f.name,
            'path': f.path,
            'size': f.size,
            'last_modified': f.last_modified.isoformat(),
            'sensitivity': f.sensitivity,
            'backup_count': f.backup_count,
            'updated_at': f.updated_at.isoformat(),
            'locations': [loc.location for loc in f.locations]
        })
    return jsonify(result), 200

@sync_bp.route('/all-files', methods=['GET'])
def all_files():
    _collect_entries = SyncService()._collect_entries()
    return jsonify(_collect_entries), 200