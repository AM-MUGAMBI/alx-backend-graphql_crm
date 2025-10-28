import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Logs a heartbeat message and optionally checks GraphQL 'hello' endpoint.
    """
    log_path = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Optional GraphQL check
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql("{ hello }")
        result = client.execute(query)
        if result.get("hello"):
            message += f" - GraphQL says: {result['hello']}"
        else:
            message += " - GraphQL response missing"
    except Exception as e:
        message += f" - GraphQL check failed: {e}"

    # Append log
    with open(log_path, "a") as f:
        f.write(message + "\n")

