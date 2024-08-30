from flask import Flask, request, Response
import requests
import itertools
import threading
import time

app = Flask(__name__)

backend_servers = [
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003"
]

health_check_interval = 2

healthy_servers = backend_servers.copy()  # Track healthy servers
server_cycle = itertools.cycle(healthy_servers)


def health_check():
    while True:
        for server in backend_servers:
            try:
                response = requests.get(server, timeout=1)
                if response.status_code == 200:
                    if server not in healthy_servers:
                        print(f"Server {server} is back online")
                        healthy_servers.append(server)
                        update_cycle()
                    else:
                        print(f"Server {server} is online")
                else:
                    if server in healthy_servers:
                        print(f"Server {server} is not healthy")
                        healthy_servers.remove(server)
                        update_cycle()

            except requests.exceptions.RequestException:
                if server in healthy_servers:
                    print(f"Server {server} is down")
                    healthy_servers.remove(server)
                    update_cycle()
        time.sleep(health_check_interval)

def update_cycle():
    global server_cycle
    server_cycle = itertools.cycle(healthy_servers)


@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def catch_all(path):
    if not healthy_servers:
        return Response("No backend servers available", status=503)

    target_server = next(server_cycle)
    target_url = f"{target_server}/{path}"

    try:
        if request.method == "GET":
            resp = requests.get(target_url, params=request.args, headers=request.headers)
        elif request.method == "POST":
            resp = requests.post(target_url, data=request.data, headers=request.headers)
        elif request.method == "PUT":
            resp = requests.put(target_url, data=request.data, headers=request.headers)
        elif request.method == "DELETE":
            resp = requests.delete(target_url, headers=request.headers)
        elif request.method == "PATCH":
            resp = requests.patch(target_url, data=request.data, headers=request.headers)
        else:
            return Response("Method Not Allowed", status=405)
    except requests.exceptions.RequestException as e:
        return Response(f"Error connecting to backend server: {str(e)}", status=502)
    
    return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))


if __name__ == '__main__':
    threading.Thread(target=health_check, daemon=True).start()
    
    app.run(port=8000, debug=True)
