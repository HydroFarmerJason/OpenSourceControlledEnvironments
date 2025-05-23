# === src/farm/api/__init__.py ===
"""
API Blueprint and routes
"""

from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from flask_restx import Api, Resource, fields, Namespace

from farm.security.config import require_auth, require_role
from farm.sensors import sensor_manager
from farm.actuators import actuator_manager
from farm.controllers import automation_controller

# Create blueprint
api_bp = Blueprint('api', __name__)

# Create API with documentation
api = Api(
    api_bp,
    version='1.0',
    title='OpenSource Controlled Environments API',
    description='Control and monitor your growing environment',
    doc='/docs'
)

# Namespaces
sensors_ns = api.namespace('sensors', description='Sensor operations')
actuators_ns = api.namespace('actuators', description='Actuator operations')
automation_ns = api.namespace('automation', description='Automation control')
system_ns = api.namespace('system', description='System operations')

# Models
sensor_model = api.model('Sensor', {
    'id': fields.String(required=True, description='Sensor ID'),
    'type': fields.String(required=True, description='Sensor type'),
    'value': fields.Float(required=True, description='Current value'),
    'unit': fields.String(required=True, description='Measurement unit'),
    'timestamp': fields.DateTime(required=True, description='Reading timestamp'),
    'status': fields.String(description='Sensor status')
})

actuator_model = api.model('Actuator', {
    'id': fields.String(required=True, description='Actuator ID'),
    'type': fields.String(required=True, description='Actuator type'),
    'state': fields.String(required=True, description='Current state'),
    'value': fields.Float(description='Current value (if applicable)'),
    'timestamp': fields.DateTime(required=True, description='Last update timestamp')
})

# Sensor endpoints
@sensors_ns.route('/')
class SensorList(Resource):
    @require_auth
    @api.doc('list_sensors')
    @api.marshal_list_with(sensor_model)
    def get(self):
        """List all sensors"""
        return sensor_manager.get_all_sensors()


@sensors_ns.route('/<string:sensor_id>')
@api.param('sensor_id', 'The sensor identifier')
class Sensor(Resource):
    @require_auth
    @api.doc('get_sensor')
    @api.marshal_with(sensor_model)
    def get(self, sensor_id):
        """Get sensor reading"""
        sensor_data = sensor_manager.get_sensor_reading(sensor_id)
        if not sensor_data:
            api.abort(404, f"Sensor {sensor_id} not found")
        return sensor_data


@sensors_ns.route('/<string:sensor_id>/history')
@api.param('sensor_id', 'The sensor identifier')
class SensorHistory(Resource):
    @require_auth
    @api.doc('get_sensor_history')
    def get(self, sensor_id):
        """Get sensor history"""
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', 100, type=int)
        
        history = sensor_manager.get_sensor_history(
            sensor_id, start_time, end_time, limit
        )
        return jsonify(history)


# Actuator endpoints
@actuators_ns.route('/')
class ActuatorList(Resource):
    @require_auth
    @api.doc('list_actuators')
    @api.marshal_list_with(actuator_model)
    def get(self):
        """List all actuators"""
        return actuator_manager.get_all_actuators()


@actuators_ns.route('/<string:actuator_id>')
@api.param('actuator_id', 'The actuator identifier')
class Actuator(Resource):
    @require_auth
    @api.doc('get_actuator')
    @api.marshal_with(actuator_model)
    def get(self, actuator_id):
        """Get actuator state"""
        actuator_data = actuator_manager.get_actuator_state(actuator_id)
        if not actuator_data:
            api.abort(404, f"Actuator {actuator_id} not found")
        return actuator_data
    
    @require_auth
    @api.doc('control_actuator')
    def post(self, actuator_id):
        """Control actuator"""
        data = request.get_json()
        action = data.get('action')  # 'on', 'off', 'set'
        value = data.get('value')
        
        result = actuator_manager.control_actuator(actuator_id, action, value)
        if not result:
            api.abort(400, "Failed to control actuator")
        
        return jsonify(result)


# Automation endpoints
@automation_ns.route('/rules')
class AutomationRules(Resource):
    @require_auth
    @api.doc('list_automation_rules')
    def get(self):
        """List automation rules"""
        return jsonify(automation_controller.get_rules())
    
    @require_role('admin')
    @api.doc('create_automation_rule')
    def post(self):
        """Create automation rule"""
        data = request.get_json()
        rule = automation_controller.create_rule(data)
        return jsonify(rule), 201


@automation_ns.route('/rules/<string:rule_id>')
@api.param('rule_id', 'The rule identifier')
class AutomationRule(Resource):
    @require_auth
    @api.doc('get_automation_rule')
    def get(self, rule_id):
        """Get automation rule"""
        rule = automation_controller.get_rule(rule_id)
        if not rule:
            api.abort(404, f"Rule {rule_id} not found")
        return jsonify(rule)
    
    @require_role('admin')
    @api.doc('update_automation_rule')
    def put(self, rule_id):
        """Update automation rule"""
        data = request.get_json()
        rule = automation_controller.update_rule(rule_id, data)
        if not rule:
            api.abort(404, f"Rule {rule_id} not found")
        return jsonify(rule)
    
    @require_role('admin')
    @api.doc('delete_automation_rule')
    def delete(self, rule_id):
        """Delete automation rule"""
        if automation_controller.delete_rule(rule_id):
            return '', 204
        api.abort(404, f"Rule {rule_id} not found")


# System endpoints
@system_ns.route('/status')
class SystemStatus(Resource):
    @require_auth
    @api.doc('get_system_status')
    def get(self):
        """Get system status"""
        return jsonify({
            'sensors': sensor_manager.get_status(),
            'actuators': actuator_manager.get_status(),
            'automation': automation_controller.get_status(),
            'timestamp': datetime.utcnow().isoformat()
        })


@system_ns.route('/logs')
class SystemLogs(Resource):
    @require_role('admin')
    @api.doc('get_system_logs')
    def get(self):
        """Get recent system logs"""
        limit = request.args.get('limit', 100, type=int)
        category = request.args.get('category')
        severity = request.args.get('severity')
        
        logs = current_app.error_handler.get_recent_errors(
            category=category,
            severity=severity,
            limit=limit
        )
        return jsonify(logs)


@system_ns.route('/backup')
class SystemBackup(Resource):
    @require_role('admin')
    @api.doc('trigger_backup')
    def post(self):
        """Trigger system backup"""
        backup_type = request.get_json().get('type', 'manual')
        # In production, this would trigger the backup script
        return jsonify({
            'message': 'Backup initiated',
            'type': backup_type,
            'timestamp': datetime.utcnow().isoformat()
        }), 202


