import diskcache
worker_status = diskcache.Cache(directory='cache/scan_result')
worker_status.clear()

sign_result = diskcache.Cache(directory="./cache/sign_result")
sign_result.clear()