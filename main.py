import sys

import bc.server.server
import bc.client.client

def main():
    if "server" in sys.argv:
        print("Starting main.")
        bc.server.server.server_main()
    else:
        print("Starting client.")
        bc.client.client.client_main()

if __name__ == '__main__':
    main()
