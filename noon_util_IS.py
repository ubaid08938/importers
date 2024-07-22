import logging
import os
from noonhelpers.v1.auth_team import get_auth_session
from noonutil.v1 import logutil, engineutil
from noonutil.v1 import remoteconfig
from google.api_core.exceptions import PermissionDenied

def get_creds(db):
	if os.getenv('ENV') not in ('staging','stg','prd','prod'):
	    return {
	        "user": 'root',
	        "password": 'root',
	        "host": 'mysql.default.svc.cluster.local'
	    }

	if db not in engineutil.ENGINE_CONFIGS:
		engineutil.define_engine(db, f"mysql+mysqldb://db-{db}/")
	try:
	    creds = engineutil.get_engine_parameters(db)
	    return {
	        "user": creds['user'],
	        "password": creds['pwd'],
	        "host": creds['host']
	    }
	except Exception as e:
	    raise e
