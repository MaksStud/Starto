import sqlite3
import json 
import os
import sys


class DataBase:
    def __init__(self, DB_NAME):
        self.DB_NAME = self.get_writable_db_path(DB_NAME)
        with sqlite3.connect(self.DB_NAME) as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS group_program (
                group_id INTEGER,
                program_id INTEGER,
                FOREIGN KEY(group_id) REFERENCES groups(id),
                FOREIGN KEY(program_id) REFERENCES programs(id)
            );
            """)    
        try:
            self.alter_program_table()
        except sqlite3.OperationalError:
            pass

    def get_all_programs(self):
        with sqlite3.connect(self.DB_NAME) as conn:
            return conn.execute("SELECT id, name FROM programs").fetchall()

    def add_group_with_programs(self, group_name, program_ids):
        with sqlite3.connect(self.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO groups (name) VALUES (?)", (group_name,))
            group_id = cursor.lastrowid
            for pid in program_ids:
                cursor.execute("INSERT INTO group_program (group_id, program_id) VALUES (?, ?)", (group_id, pid))
            return group_id

    def get_programs_by_group(self, group_id):
        with sqlite3.connect(self.DB_NAME) as conn:
            return conn.execute("""
                SELECT p.name, p.path FROM programs p
                JOIN group_program gp ON p.id = gp.program_id
                WHERE gp.group_id = ?
            """, (group_id,)).fetchall()

    def get_all_groups(self):
        with sqlite3.connect(self.DB_NAME) as conn:
            return conn.execute("SELECT id, name FROM groups").fetchall()

    def delete_group(self, group_id):
        with sqlite3.connect(self.DB_NAME) as conn:
            conn.execute("""
                DELETE FROM programs
                WHERE id IN (
                    SELECT program_id FROM group_program
                    WHERE group_id = ?
                )
            """, (group_id,))
            conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))

    def alter_program_table(self,):
        with sqlite3.connect(self.DB_NAME) as conn:
            conn.execute("ALTER TABLE programs ADD COLUMN path TEXT")

    def add_program(self, name: str, path: str) -> int:
        with sqlite3.connect(self.DB_NAME) as conn:
            cursor = conn.execute(
                "INSERT INTO programs (name, path) VALUES (?, ?)",
                (name, path)
            )
            return cursor.lastrowid

    def link_program_to_group(self, group_id: int, program_id: int):
        with sqlite3.connect(self.DB_NAME) as conn:
            conn.execute(
                "INSERT INTO group_program (group_id, program_id) VALUES (?, ?)",
                (group_id, program_id)
            )

    def get_group_details(self, group_id: int) -> str:
        with sqlite3.connect(self.DB_NAME) as conn:
            cursor = conn.cursor()
            group_name = cursor.execute("SELECT name FROM groups WHERE id = ?", (group_id,)).fetchone()[0]
            programs = cursor.execute("""
                SELECT p.name, p.path FROM programs p
                JOIN group_program gp ON p.id = gp.program_id
                WHERE gp.group_id = ?
            """, (group_id,)).fetchall()

            program_list = [{'name': name, 'path': path} for name, path in programs]

            data = {
                'id': group_id,
                'name': group_name,
                'programs': program_list
            }
            return json.dumps(data)

    def update_group(self, group_id, new_name, new_program_list):
        with sqlite3.connect(self.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE groups SET name = ? WHERE id = ?", (new_name, group_id))

            cursor.execute("""
                DELETE FROM programs
                WHERE id IN (SELECT program_id FROM group_program WHERE group_id = ?)
            """, (group_id,))
            cursor.execute("DELETE FROM group_program WHERE group_id = ?", (group_id,))

            for program in new_program_list:
                cursor.execute(
                    "INSERT INTO programs (name, path) VALUES (?, ?)",
                    (program['name'], program['path'])
                )
                program_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO group_program (group_id, program_id) VALUES (?, ?)",
                    (group_id, program_id)
                )

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def get_writable_db_path(self, db_name):
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))

        db_path = os.path.join(exe_dir, db_name)

        if not os.path.exists(db_path):
            open(db_path, 'a').close()

        return db_path
