import json
import os
import psycopg2
from psycopg2.extras import DictCursor
import sys

def generate_schema_json(db_config, output_dir='data'):
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor(cursor_factory=DictCursor)

        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [row['table_name'] for row in cursor.fetchall()]
        schema = {'tables': [], 'relations': []}

        for table in tables:
            cursor.execute(f"""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = '{table}'
            """)
            fields = []
            for row in cursor.fetchall():
                field_type = 'PK' if row['column_default'] and 'nextval' in row['column_default'] else ''
                fields.append({'name': row['column_name'], 'type': field_type, 'dataType': row['data_type']})
            schema['tables'].append({'name': table, 'fields': fields, 'x': 0, 'y': 0})

        cursor.execute("""
            SELECT 
                tc.table_name AS from_table, kcu.column_name AS from_column,
                ccu.table_name AS to_table, ccu.column_name AS to_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
        """)
        for row in cursor.fetchall():
            schema['relations'].append({'from': f"{row['from_table']}.{row['from_column']}", 'to': f"{row['to_table']}.{row['to_column']}"})

        cursor.close()
        conn.close()

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        file_path = os.path.abspath(os.path.join(output_dir, f"{db_config['name']}_schema.json"))
        with open(file_path, 'w') as f:
            json.dump(schema, f)
        return file_path
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            db_config = json.loads(sys.argv[1])
            file_path = generate_schema_json(db_config)
            if file_path:
                print(file_path)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input - {str(e)}", file=sys.stderr)