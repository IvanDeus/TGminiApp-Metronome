import sys
import psutil
import os
import sqlite3
from app_cfg import *

# --- Function to check and initialize the database ---
def init_database():
    db_path = os.path.join(script_directory, DATABASE)
    if not os.path.exists(db_path):
        print("Database does not exist. Creating and initializing...")
        try:
            conn = sqlite3.connect(db_path)
            with open(os.path.join(script_directory, 'schema.sql'), 'r') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.commit()
            print(f"Database created at {db_path}")
        except Exception as e:
            print(f"Error initializing database: {e}")
            sys.exit(1)
        finally:
            conn.close()
    else:
        print("Database exists.")

# --- Process filtering and killing functions ---
def filter_processes_by_port(bot_lport):
    filtered_processes = []
    pid_list = []
    for process in psutil.process_iter():
        try:
            for connection in process.net_connections():
                if connection.laddr.port == bot_lport:
                    filtered_processes.append(process)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    pid_list = [p.pid for p in filtered_processes]
    return filtered_processes, pid_list

def kill_processes(pid_list):
    for pid in pid_list:
        try:
            process = psutil.Process(pid)
            process.terminate()
            process.wait(timeout=3)
            print(f"Successfully terminated process {pid}")
        except psutil.NoSuchProcess:
            print(f"No such process: {pid}")
        except psutil.AccessDenied:
            print(f"Access denied: {pid}")
        except psutil.TimeoutExpired:
            print(f"Timeout expired for process {pid}")

# --- Main logic ---
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)  # Ensure correct working directory

if len(sys.argv) == 1:
    print("Usage: {} [start|stop|status]".format(sys.argv[0]))
    sys.exit(1)

action = sys.argv[1]

if action == "start":
    filtered_processes, pids_tokill = filter_processes_by_port(bot_lport)
    if filtered_processes:
        print("App is already running.")
    else:
        # Initialize DB before starting Gunicorn
        init_database()

        # Start Gunicorn
        psutil.Popen(
            ["gunicorn",
             "-b", "localhost:{}".format(bot_lport),
             "-w", "2",
             "-t", "65",
             "--log-file={}".format(logfpath),
             "app:app",
             "--chdir", script_directory]
        )
        print("App started.")

elif action == "stop":
    filtered_processes, pids_tokill = filter_processes_by_port(bot_lport)
    if pids_tokill:
        kill_processes(pids_tokill)
    else:
        print("App is stopped.")

elif action == "status":
    filtered_processes, pids_tokill = filter_processes_by_port(bot_lport)
    if filtered_processes:
        print(filtered_processes)
    else:
        print("App is not running.")

else:
    print("Usage: {} [start|stop|status]".format(sys.argv[0]))
    sys.exit(1)
