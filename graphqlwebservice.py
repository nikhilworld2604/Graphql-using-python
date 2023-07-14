import graphene
import pyodbc
from fastapi import FastAPI
from starlette.applications import Starlette
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
import uvicorn
#

server = 'USKOLNIKRANJAN1'
database = 'AdventureWorks2014'
username = 'US\\nikranjan' 
conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};Trusted_Connection=yes')

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

class User(graphene.ObjectType):
    facultyID = graphene.String()
    name = graphene.String()
    department = graphene.String()
    country = graphene.String()
    city = graphene.String()
    address = graphene.String()
    appointment = graphene.String()

class Query(graphene.ObjectType):
    users = graphene.List(User)

    def resolve_users(self, info):
        query = "SELECT * FROM AdventureWorks2014.dbo.FACULTY"
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

schema = graphene.Schema(query=Query)

app = Starlette()
app.mount("/", GraphQLApp(schema, on_get=make_graphiql_handler()))
