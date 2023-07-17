import graphene
import pyodbc
import hashlib
from flask import Flask, jsonify, request
from graphene import ObjectType, String, Schema, List, Field
import warnings
from starlette.applications import Starlette
from starlette_graphene3 import GraphQLApp
import uvicorn
from graphql import parse

warnings.filterwarnings("ignore")

server = 'USKOLNIKRANJAN1'
database = 'AdventureWorks2014'
username = 'US\\nikranjan' 
conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};Trusted_Connection=yes')

persisted_queries = {}

def generate_query_id(query):
    return hashlib.md5(query.encode('utf-8')).hexdigest()


def execute_query(query):
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    except pyodbc.Error as e:
        print(f"An error occurred: {e}")
        return []

class User(ObjectType):
    facultyID = String()
    name = String()
    department = String()
    country = String()
    city = String()
    address = String()
    appointment = String()
	
class Query(ObjectType):
    users = List(User)

    def resolve_users(self, info):
        query = "SELECT FACULTY_ID, Name, Department, COUNTRY, City, ADDRESS, APPOINTMENT FROM AdventureWorks2014.dbo.FACULTY"
        result = execute_query(query)
        return [User(
            facultyID=row[0],
            name=row[1],
            department=row[2],
            country=row[3],
            city=row[4],
            address=row[5],
            appointment=row[6]
        ) for row in result]

schema = Schema(query=Query)


query = '''
query {
  users {
    facultyID
    name
    department
  }
}
'''

query_id = generate_query_id(query)
persisted_queries[query_id] = query

app = Flask(__name__)


@app.route("/persistedqueries", methods=["POST"])
def persisted_queries_endpoint():
    if request.method == 'POST':
        persisted_query_id = request.json.get('persistedQueryId')
        query = persisted_queries.get(persisted_query_id)

        if query:
            result = schema.execute(query)  
            return jsonify(result.data)
        else:
            return jsonify({'errors': [{'message': 'Persisted query not found.'}]})

    return jsonify({'message': 'Persisted queries endpoint'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
