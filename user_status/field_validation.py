from cerberus import Validator
from datetime import datetime


#KX - cerberus library for field validation --> Validation rules can be found: https://cerberus-sanhe.readthedocs.io/usage.html#validation-rules
def put_field_validation(req_body):
    field_vali = Validator()
    to_date = lambda s: datetime.strptime(s, '%Y-%m-%d')
    schema = {
        'status': {'required': False, 'type': 'string','empty': False,'allowed': ['Active', 'Terminated']},
        'employee_environment': {'required': False, 'type': 'string','empty': False,'allowed': ['Internal', 'External','Other']},
        'department': {'required': False, 'type': 'string','nullable': True},
        'work_type': {'required': False, 'type': 'string','empty': False,'allowed': ['Permanent', 'Temporary', 'Contract']},
        'manager_id': {'required': False, 'type': 'string','nullable': True},
        'work_location': {'required': False, 'type': 'string','nullable': True,'allowed': ['Canada','USA','EU','NULL']},
        'gender': {'required': False, 'type': 'string','nullable': True,'allowed': ['Male', 'Female', 'Intersex','NULL']},
        'birth_date': {'required': False, 'type': 'datetime','coerce': to_date,'nullable': True},
        'start_date': {'required': False, 'type': 'datetime','coerce': to_date,'nullable': True},
        'end_date': {'required': False, 'type': 'datetime','coerce': to_date,'nullable': True},
    }

    #KX - if field validation pass, then it will return True, otherwise will return False 
    vali_result = field_vali.validate(req_body, schema)

    #KX - it will return the field validation error message if it dont pass
    vali_error = field_vali.errors

    return vali_result, vali_error



#KX - cerberus library for field validation --> Validation rules can be found: https://cerberus-sanhe.readthedocs.io/usage.html#validation-rules
def post_field_validation(req_body):
    field_vali = Validator()
    to_date = lambda s: datetime.strptime(s, '%Y-%m-%d')
    schema = {
        'domain_rhonda_id': {'required': True, 'type': 'string','empty': False},
        'status': {'required': True, 'type': 'string','empty': False,'allowed': ['Active', 'Terminated']},
        'employee_environment': {'required': True, 'type': 'string','empty': False,'allowed': ['Internal', 'External','Other']},
        'department': {'required': False, 'type': 'string','nullable': True},
        'work_type': {'required': True, 'type': 'string','empty': False,'allowed': ['Permanent', 'Temporary', 'Contract']},
        'manager_id': {'required': False, 'type': 'string','nullable': True},
        'work_location': {'required': False, 'type': 'string','nullable': True,'allowed': ['Canada','USA','EU','NULL']},
        'gender': {'required': False, 'type': 'string','nullable': True,'allowed': ['Male', 'Female', 'Intersex','NULL']},
        'birth_date': {'required': False, 'type': 'datetime','coerce': to_date,'nullable': True},
        'start_date': {'required': False, 'type': 'datetime','coerce': to_date,'nullable': True},
        'end_date': {'required': False, 'type': 'datetime','coerce': to_date,'nullable': True},
    }
    
    #KX - if field validation pass, then it will return True, otherwise will return False 
    vali_result = field_vali.validate(req_body, schema)

    #KX - it will return the field validation error message if it dont pass
    vali_error = field_vali.errors

    return vali_result, vali_error

