import os
import json
import asyncio
from mcp_server import adapter, search, insert, aggregate, database_schema

async def main():
    print("--- Verifying SQLite MCP Server ---\n")
    
    # Check tables
    tables = adapter.list_tables()
    print(f"1. Database Tables Found: {tables}")
    
    # Check Search Tool
    print("\n2. Testing 'search' Tool on 'students'...")
    search_res = await search(
        table="students", 
        filters=[{"column": "cohort", "operator": "=", "value": "A1"}],
        limit=2
    )
    print("Search Result:", search_res)

    # Check Insert Tool
    print("\n3. Testing 'insert' Tool on 'courses'...")
    insert_res = await insert(
        table="courses",
        values={"title": "Introduction to FastMCP", "credits": 5}
    )
    print("Insert Result:", insert_res)
    
    # Check Aggregate Tool
    print("\n4. Testing 'aggregate' Tool on 'students'...")
    agg_res = await aggregate(
        table="students",
        metric="avg",
        column="score",
        group_by="cohort"
    )
    print("Aggregate Result:", agg_res)

    # Check Resources
    print("\n5. Testing Resource 'schema://database'...")
    db_schema_res = await database_schema()
    print("Schema Result length:", len(db_schema_res), "characters")

    print("\nVerification completed.")

if __name__ == "__main__":
    asyncio.run(main())
