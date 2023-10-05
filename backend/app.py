from flask import Flask, request
from sqlalchemy import create_engine, and_
from backend.data.models import TLE
from data.models import db_session, get_engine

app = Flask(__name__)

engine = get_engine()

# A mapping from string operators to SQLAlchemy functions
operator_mapping = {
    "<": "__lt__",
    "<=": "__le__",
    "==": "__eq__",
    "!=": "__ne__",
    ">": "__gt__",
    ">=": "__ge__",
}

@app.route('/query', methods=['GET'])
@db_session(engine)
def query_tle(session):
    # Extract parameters from JSON object received from front end
    params = request.json
    
    # Validate the parameters
    def validate_params(params):
        valid_cols = set(TLE.__table__.columns)
        valid_params = {}
        for column, operations in params.items():
            if column not in valid_cols:
                continue
            valid_params[column] = {}
            for operator_str, value in operations.items():
                if operator_str in operator_mapping:
                    valid_params[column][operator_str] = value
        return valid_params
    params = validate_params(params)
    
    # Convert the parameters into SQLAlchemy filter expressions
    filter_expressions = []
    for column, operations in params.items():
        for operator_str, value in operations.items():
            operator_func = getattr(getattr(TLE, column), operator_mapping[operator_str])
            filter_expressions.append(operator_func(value))
    
    # Create a session and query the database
    results = session.query(TLE).filter(and_(*filter_expressions)).all()
    
    # Transform results into a format that can be sent back to the front end
    results_data = [{"name": result.name, "satellite_number": result.satellite_number} for result in results]

    # Return the results as JSON
    return {"results": results_data}
