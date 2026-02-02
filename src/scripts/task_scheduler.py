import sys
import subprocess

def create(name, cmd, schedule="DAILY", time_str="10:00"):
    subprocess.run(["schtasks", "/Create", "/SC", schedule, "/TN", name, "/TR", cmd, "/ST", time_str], shell=False)

def delete(name):
    subprocess.run(["schtasks", "/Delete", "/TN", name, "/F"], shell=False)

def list_tasks():
    subprocess.run(["schtasks", "/Query"], shell=False)

def main():
    if len(sys.argv) < 2:
        print("usage: task_scheduler.py <create|delete|list> [args]")
        sys.exit(1)
    action = sys.argv[1]
    if action == "create":
        if len(sys.argv) < 5:
            print("create <NAME> <CMD> <TIME> [DAILY|HOURLY]")
            sys.exit(1)
        name = sys.argv[2]
        cmd = sys.argv[3]
        time_str = sys.argv[4]
        schedule = sys.argv[5] if len(sys.argv) > 5 else "DAILY"
        create(name, cmd, schedule, time_str)
    elif action == "delete":
        if len(sys.argv) < 3:
            print("delete <NAME>")
            sys.exit(1)
        delete(sys.argv[2])
    elif action == "list":
        list_tasks()
    else:
        print("unknown")
        sys.exit(1)

if __name__ == "__main__":
    main()
