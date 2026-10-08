from app.config import settings
from . import logger as local_audit
from . import dynamodb_logger as cloud_audit

if settings.USE_AWS:
    init_db = cloud_audit.init_db
    log_event = cloud_audit.log_event
    create_execution = cloud_audit.create_execution
    update_execution_status = cloud_audit.update_execution_status
    get_execution = cloud_audit.get_execution
    list_executions = cloud_audit.list_executions
    get_audit_trail = cloud_audit.get_audit_trail
else:
    init_db = local_audit.init_db
    log_event = local_audit.log_event
    create_execution = local_audit.create_execution
    update_execution_status = local_audit.update_execution_status
    get_execution = local_audit.get_execution
    list_executions = local_audit.list_executions
    get_audit_trail = None

__all__ = [
    "init_db",
    "log_event",
    "create_execution",
    "update_execution_status",
    "get_execution",
    "list_executions",
    "get_audit_trail",
]