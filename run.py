import wpath
from wallet.wallet_config import WALLET_CONFIG
from wallet.manage import app
import ssl


def run():
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(WALLET_CONFIG.CA_FILE)
    context.load_cert_chain(certfile=WALLET_CONFIG.CERT_FILE, keyfile=WALLET_CONFIG.KEY_FILE)
    app.run(
        host=WALLET_CONFIG.HTTPS_HOST, port=WALLET_CONFIG.HTTPS_PORT, debug=WALLET_CONFIG.DEBUG, ssl_context=context
    )


if __name__ == "__main__":
    run()
