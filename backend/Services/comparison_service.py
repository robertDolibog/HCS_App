import hashlib

class ComparisonService:
    def compute_hash(self, data_bytes: bytes) -> str:
        return hashlib.sha256(data_bytes).hexdigest()

    def group_by_hash(self, entries):
        groups = {}
        for e in entries:
            groups.setdefault(e['file_hash'], []).append(e)
        return groups

    def compute_backup_counts(self, groups):
        return {h: max(len(v) - 1, 0) for h, v in groups.items()}
