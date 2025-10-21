from flask import Blueprint, jsonify, request

records_bp = Blueprint('records', __name__)

# Sample in-memory storage for records
records = []

@records_bp.route('/records', methods=['GET'])
def list_records():
    return jsonify(records), 200

@records_bp.route('/records/<int:record_id>', methods=['GET'])
def get_record(record_id):
    record = next((r for r in records if r['id'] == record_id), None)
    if record is None:
        return jsonify({'error': 'Record not found'}), 404
    return jsonify(record), 200

@records_bp.route('/records/<int:record_id>/retry', methods=['POST'])
def retry_record(record_id):
    record = next((r for r in records if r['id'] == record_id), None)
    if record is None:
        return jsonify({'error': 'Record not found'}), 404
    # Logic for retrying the record
    return jsonify({'message': 'Record retried successfully'}), 200

@records_bp.route('/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    global records
    records = [r for r in records if r['id'] != record_id]
    return jsonify({'message': 'Record deleted successfully'}), 204

@records_bp.route('/records/statistics', methods=['GET'])
def get_statistics():
    # Sample statistics logic
    total_records = len(records)
    return jsonify({'total_records': total_records}), 200
