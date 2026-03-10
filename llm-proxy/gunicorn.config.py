import multiprocessing

# Project-specific settings
project = "proxy-api"
base = "/home/app"
virtualenv = f"{base}/.virtualenv/llm-proxy-python311"
chdir = f"{base}"
module = "main:app"

# Socket and log settings
bind = "0.0.0.0:9999"
logfile = f"{base}/llm-proxy-api-gunicorn.log"
access_log_format = '%(h)s|%(l)s|%(u)s|%(r)s|%(s)s|%(b)s'
errorlog = logfile
capture_output = True

# Server settings
workers = 4  # Matches uWSGI `processes`
threads = 8  # Matches uWSGI `threads`
worker_class = "uvicorn.workers.UvicornWorker"
preload_app = False
chdir = chdir
umask = 0o000  # Matches `chmod-socket = 666`

# timeout
timeout = 300
keepalive = 300
graceful_timeout = 300


# Limit request for memory
max_requests = 200
max_requests_jitter = 50