import subprocess


def run_cmd(cmd):
    subprocess.run(cmd, shell=True, check=True)


def run_tests():
    run_cmd("pytest")


def watch_tests():
    run_cmd("ptw -- -s")


# def export_open_api_schema():
#     run_cmd("poetry install")
#     run_cmd("python -m scripts.export_open_api_schema")


def run_formatter():
    run_cmd("black .")

def run_server_development():
  run_cmd("uvicorn main:app --reload")

def run_server_production():
  run_cmd("uvicorn main:app --host 0.0.0.0")

# def run_task_queue_worker():
#     run_cmd("poetry install")
#     run_cmd("celery -A worker worker")


# def run_task_queue_api():
#     run_cmd("poetry install")
#     run_cmd("celery -A worker flower")
