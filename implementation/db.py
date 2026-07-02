import sqlite3

class ValidationError(Exception):
    """Raised when a request cannot be safely executed."""
    pass

class SQLiteAdapter:
    def __init__(self, db_path):
        self.db_path = db_path
        self._schema_cache = {}
        self._refresh_schema()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _refresh_schema(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row['name'] for row in cursor.fetchall()]
        
        self._schema_cache = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = [row['name'] for row in cursor.fetchall()]
            self._schema_cache[table] = columns
        conn.close()

    def list_tables(self):
        return list(self._schema_cache.keys())

    def get_table_schema(self, table):
        if table not in self._schema_cache:
            raise ValidationError(f"Unknown table: {table}")
        
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table});")
        columns_info = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return columns_info

    def _validate_table_and_columns(self, table, columns=None):
        if table not in self._schema_cache:
            raise ValidationError(f"Unknown table: {table}")
        if columns:
            allowed_cols = set(self._schema_cache[table])
            for col in columns:
                if col not in allowed_cols:
                    raise ValidationError(f"Unknown column '{col}' in table '{table}'")

    def _validate_filters(self, table, filters):
        """
        filters: list of dicts [{"column": "x", "operator": "=", "value": 1}]
        Supported operators: =, >, <, >=, <=, LIKE, IN
        """
        if not filters:
            return "", []
            
        allowed_operators = {"=", ">", "<", ">=", "<=", "LIKE", "IN"}
        clauses = []
        params = []
        
        for f in filters:
            col = f.get("column")
            op = f.get("operator", "=").upper()
            val = f.get("value")
            
            self._validate_table_and_columns(table, [col])
            
            if op not in allowed_operators:
                raise ValidationError(f"Unsupported operator: {op}")
            
            if op == "IN":
                if not isinstance(val, list) or len(val) == 0:
                    raise ValidationError("Operator IN requires a non-empty list of values.")
                placeholders = ", ".join(["?"] * len(val))
                clauses.append(f"{col} IN ({placeholders})")
                params.extend(val)
            else:
                clauses.append(f"{col} {op} ?")
                params.append(val)
                
        return " WHERE " + " AND ".join(clauses), params

    def search(self, table, columns=None, filters=None, limit=20, offset=0, order_by=None, descending=False):
        self._validate_table_and_columns(table, columns)
        
        select_cols = "*" if not columns else ", ".join(columns)
        where_clause, params = self._validate_filters(table, filters)
        
        query = f"SELECT {select_cols} FROM {table}{where_clause}"
        
        if order_by:
            self._validate_table_and_columns(table, [order_by])
            direction = "DESC" if descending else "ASC"
            query += f" ORDER BY {order_by} {direction}"
            
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise ValidationError("Limit must be an integer between 1 and 1000")
        if not isinstance(offset, int) or offset < 0:
            raise ValidationError("Offset must be a non-negative integer")
            
        query += f" LIMIT {limit} OFFSET {offset}"
        
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            rows = [dict(row) for row in cursor.fetchall()]
            return rows
        finally:
            conn.close()

    def insert(self, table, values):
        if not values or not isinstance(values, dict):
            raise ValidationError("Values must be a non-empty dictionary")
            
        self._validate_table_and_columns(table, values.keys())
        
        columns = list(values.keys())
        placeholders = ", ".join(["?"] * len(columns))
        col_names = ", ".join(columns)
        params = [values[col] for col in columns]
        
        query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
        
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            
            # Fetch the inserted row
            row_id = cursor.lastrowid
            # Determine primary key column (assuming 'id' for simplicity, or we can get schema)
            # A more robust way is to query the rowid
            cursor.execute(f"SELECT * FROM {table} WHERE rowid = ?", (row_id,))
            inserted_row = dict(cursor.fetchone())
            return inserted_row
        finally:
            conn.close()

    def aggregate(self, table, metric, column=None, filters=None, group_by=None):
        allowed_metrics = {"count", "avg", "sum", "min", "max"}
        metric = metric.lower()
        if metric not in allowed_metrics:
            raise ValidationError(f"Invalid aggregate metric: {metric}")
            
        self._validate_table_and_columns(table)
        
        if metric == "count" and not column:
            agg_expr = "COUNT(*)"
        else:
            if not column:
                raise ValidationError(f"Metric {metric} requires a column")
            self._validate_table_and_columns(table, [column])
            agg_expr = f"{metric.upper()}({column})"
            
        where_clause, params = self._validate_filters(table, filters)
        
        select_clause = f"{agg_expr} AS value"
        if group_by:
            self._validate_table_and_columns(table, [group_by])
            select_clause = f"{group_by}, " + select_clause
            
        query = f"SELECT {select_clause} FROM {table}{where_clause}"
        
        if group_by:
            query += f" GROUP BY {group_by}"
            
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            rows = [dict(row) for row in cursor.fetchall()]
            return rows
        finally:
            conn.close()
