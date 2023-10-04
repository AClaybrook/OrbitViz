from flask import Flask, request
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from your_models import TLE

app = Flask(__name__)
engine = create_engine('sqlite:///your_database.db')
Session = sessionmaker(bind=engine)

# A mapping from string operators to SQLAlchemy functions
operator_mapping = {
    "<": "__lt__",
    "<=": "__le__",
    "==": "__eq__",
    "!=": "__ne__",
    ">": "__gt__",
    ">=": "__ge__",
}

@app.route('/query', methods=['POST'])
def query_tle():
    # Extract parameters from JSON object received from front end
    params = request.json
    
    # Validate the parameters (not implemented here, but very important)
    
    # Convert the parameters into SQLAlchemy filter expressions
    filter_expressions = []
    for column, operations in params.items():
        for operator_str, value in operations.items():
            operator_func = getattr(getattr(TLE, column), operator_mapping[operator_str])
            filter_expressions.append(operator_func(value))
    
    # Create a session and query the database
    session = Session()
    results = session.query(TLE).filter(and_(*filter_expressions)).all()
    
    # Transform results into a format that can be sent back to the front end
    results_data = [{"name": result.name, "satellite_number": result.satellite_number} for result in results]
    
    # Close the session
    session.close()
    
    # Return the results as JSON
    return {"results": results_data}
