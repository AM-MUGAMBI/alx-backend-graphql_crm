import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from crm.models import Product



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

    # Optional console output
    print(message)


def update_low_stock():
    """
    Runs every 12 hours to restock products with low stock via GraphQL mutation.
    Logs updated products and stock levels to /tmp/low_stock_updates_log.txt.
    """
    log_path = "/tmp/low_stock_updates_log.txt"
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    mutation = gql("""
        mutation {
            updateLowStockProducts {
                message
                updatedProducts {
                    name
                    stock
                }
            }
        }
    """)

    try:
        result = client.execute(mutation)
        message = result["updateLowStockProducts"]["message"]
        updated = result["updateLowStockProducts"]["updatedProducts"]

        with open(log_path, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
            for p in updated:
                f.write(f"    - {p['name']}: stock={p['stock']}\n")

    except Exception as e:
        with open(log_path, "a") as f:
            f.write(f"[{timestamp}] ERROR running update_low_stock: {e}\n")
