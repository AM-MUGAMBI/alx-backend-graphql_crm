import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Logs a heartbeat message and optionally checks GraphQL 'hello' endpoint.
    Appends a timestamped message to /tmp/crm_heartbeat_log.txt.
    """
    log_path = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Try to reach the GraphQL endpoint (optional health verification)
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
            timeout=5,  # prevent hanging
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        query = gql("{ hello }")
        result = client.execute(query)

        hello_response = result.get("hello")
        if hello_response:
            message += f" - GraphQL says: {hello_response}"
        else:
            message += " - GraphQL responded but no 'hello' field found"

    except Exception as e:
        message += f" - GraphQL check failed: {e}"

    # Append to log file
    try:
        with open(log_path, "a") as f:
            f.write(message + "\n")
    except Exception as file_error:
        print(f"Error writing to log file: {file_error}")

    # Optional console output (useful when testing manually)
    print(message)
