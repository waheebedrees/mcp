import os
import sys
import sqlite3
import threading
from datetime import datetime
from statistics import mean, median
from mcp.server.fastmcp import FastMCP


utility_mcp = FastMCP("UtilityTools")

DB_FILE = "example.db"

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


@utility_mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@utility_mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


@utility_mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers. Raises error if dividing by zero."""
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b


@utility_mcp.tool()
def stats(numbers: list[float]) -> dict:
    """Compute basic statistics (mean, median, min, max) of a list of numbers."""
    if not numbers:
        raise ValueError("Empty list provided.")
    return {
        "mean": mean(numbers),
        "median": median(numbers),
        "min": min(numbers),
        "max": max(numbers),
    }


@utility_mcp.tool()
def list_files(path: str = ".") -> list[str]:
    """List all files and directories in the given path."""
    return os.listdir(path)


@utility_mcp.tool()
def read_file(path: str) -> str:
    """Read the contents of a text file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"No such file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@utility_mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write text content to a file. Overwrites if file exists."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File written: {path}"


@utility_mcp.tool()
def system_info() -> dict:
    """Return basic system information (platform, Python version, current directory)."""
    return {
        "platform": sys.platform,
        "python_version": sys.version,
        "cwd": os.getcwd(),
    }




@utility_mcp.tool()
def create_table():
    """Create a demo table in SQLite database if not exists."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    conn.commit()
    conn.close()
    return "Table 'users' ensured."


@utility_mcp.tool()
def insert_user(name: str, age: int):
    """Insert a user into the SQLite 'users' table."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
    conn.commit()
    conn.close()
    return f"User {name} added."


@utility_mcp.tool()
def get_users() -> list[dict]:
    """Fetch all users from the SQLite 'users' table."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, name, age FROM users")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "age": r[2]} for r in rows]


@utility_mcp.tool()
def current_time() -> str:
    """Return the current server time in ISO format."""
    return datetime.utcnow().isoformat()


if __name__ == "__main__":
    utility_mcp.run(transport="stdio")
