import os
import json
from fastmcp import FastMCP
from pydantic import Field
from typing import List, Optional, Any, Dict

from db import SQLiteAdapter, ValidationError

# Create the server object.
mcp = FastMCP("sqlite-lab")

# Initialize database path
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "sqlite_lab.db"))

# Ensure database exists or create it
if not os.path.exists(DB_PATH):
    import init_db
    init_db.create_database(DB_PATH)

adapter = SQLiteAdapter(DB_PATH)

@mcp.tool(description="🔍 Tìm kiếm và tra cứu dữ liệu (như xem danh sách học sinh, điểm số).")
async def search(
    table: str = Field(..., description="Tên danh mục cần tra cứu (nhập 'students' cho học sinh, 'courses' cho khóa học)"), 
    columns: Optional[List[str]] = Field(None, description="Các thông tin bạn muốn xem (ví dụ: chỉ xem tên và điểm). Bỏ trống nếu muốn xem tất cả."), 
    filters: Optional[List[Dict[str, Any]]] = Field(None, description="Danh sách các điều kiện lọc. Mỗi điều kiện gồm: cột cần xét (column), phép so sánh (operator như =, >, <), và giá trị (value). Ví dụ: Lọc những học sinh có điểm lớn hơn hoặc bằng 8.0"), 
    limit: int = Field(20, description="Số lượng kết quả tối đa muốn hiển thị trên một trang (mặc định 20)"), 
    offset: int = Field(0, description="Bỏ qua bao nhiêu kết quả đầu tiên (dùng để chuyển trang)"), 
    order_by: Optional[str] = Field(None, description="Tên cột dùng để sắp xếp kết quả (ví dụ: sắp xếp theo điểm)"), 
    descending: bool = Field(False, description="Đánh dấu True nếu bạn muốn sắp xếp giảm dần (từ cao xuống thấp)")
) -> str:
    """
    🔍 Tìm kiếm và tra cứu dữ liệu (như xem danh sách học sinh, điểm số).
    """
    try:
        results = adapter.search(
            table=table, 
            columns=columns, 
            filters=filters, 
            limit=limit, 
            offset=offset, 
            order_by=order_by, 
            descending=descending
        )
        return json.dumps({"status": "success", "data": results}, indent=2)
    except ValidationError as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": f"Internal error: {str(e)}"}, indent=2)

@mcp.tool(description="➕ Thêm một hồ sơ hoặc dữ liệu mới vào hệ thống.")
async def insert(
    table: str = Field(..., description="Tên danh mục bạn muốn thêm dữ liệu (ví dụ: 'students')"), 
    values: Dict[str, Any] = Field(..., description="Thông tin cụ thể của dữ liệu mới. Nhập từng phần thông tin. Ví dụ: Tên là Nam, Lớp là A1, Điểm là 9.5")
) -> str:
    """
    ➕ Thêm một hồ sơ hoặc dữ liệu mới vào hệ thống.
    """
    try:
        inserted = adapter.insert(table, values)
        return json.dumps({"status": "success", "data": inserted}, indent=2)
    except ValidationError as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": f"Internal error: {str(e)}"}, indent=2)

@mcp.tool(description="📊 Tính toán thống kê (như tính điểm trung bình, đếm tổng số học sinh).")
async def aggregate(
    table: str = Field(..., description="Tên danh mục bạn muốn thống kê (ví dụ: 'students')"), 
    metric: str = Field(..., description="Phép tính bạn muốn dùng: 'count' (đếm), 'avg' (trung bình), 'sum' (tổng), 'min' (nhỏ nhất), 'max' (lớn nhất)"), 
    column: Optional[str] = Field(None, description="Cột chứa dữ liệu để tính toán (ví dụ: cột điểm số)"), 
    filters: Optional[List[Dict[str, Any]]] = Field(None, description="Điều kiện lọc trước khi tính (giống như ở phần tìm kiếm)"), 
    group_by: Optional[str] = Field(None, description="Gom nhóm kết quả (ví dụ: gom nhóm theo lớp để tính điểm trung bình của từng lớp)")
) -> str:
    """
    📊 Tính toán thống kê (như tính điểm trung bình, đếm tổng số học sinh).
    """
    try:
        results = adapter.aggregate(
            table=table, 
            metric=metric, 
            column=column, 
            filters=filters, 
            group_by=group_by
        )
        return json.dumps({"status": "success", "data": results}, indent=2)
    except ValidationError as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": f"Internal error: {str(e)}"}, indent=2)

@mcp.resource("schema://database")
async def database_schema() -> str:
    """📦 Xem toàn bộ cấu trúc các danh mục dữ liệu trong hệ thống."""
    try:
        if adapter is None:
            # Re-init just in case resource is called before lifespan hook 
            # (though FastMCP usually guarantees lifespan)
            temp_adapter = SQLiteAdapter(DB_PATH)
        else:
            temp_adapter = adapter
            
        tables = temp_adapter.list_tables()
        schema_info = {}
        for table in tables:
            schema_info[table] = temp_adapter.get_table_schema(table)
        return json.dumps({"status": "success", "schema": schema_info}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)

@mcp.resource("schema://table/{table_name}")
async def table_schema(table_name: str) -> str:
    """📄 Xem cấu trúc chi tiết của một danh mục cụ thể."""
    try:
        if adapter is None:
            temp_adapter = SQLiteAdapter(DB_PATH)
        else:
            temp_adapter = adapter
            
        schema = temp_adapter.get_table_schema(table_name)
        return json.dumps({"status": "success", "table": table_name, "schema": schema}, indent=2)
    except ValidationError as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)

if __name__ == "__main__":
    mcp.run()
