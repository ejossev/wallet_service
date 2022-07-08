
from wallet.app.api import *
from sqlalchemy import or_, and_
from utl.redis import *
from utl.api import *
from sqlalchemy.sql import text
from Crypto.Cipher import AES
from wallet.wallet_config import WALLET_CONFIG
from wallet.app.api import api
from models.wallet.key import Key
from models import db
import log
import web3

logging = log.getLogger("wallet")


def decrypt_key(encrypted_key: bytes, nonce: bytes, tag: bytes) -> bytes:
    cipher = AES.new(WALLET_CONFIG.WALLET_SECRET_KEY, AES.MODE_EAX, nonce=nonce)
    key = cipher.decrypt(encrypted_key)
    try:
        cipher.verify(tag)
        return key
    except ValueError:
        return ""

def encrypt_key(plaintext_key: bytes) -> bytes:
    cipher = AES.new(WALLET_CONFIG.WALLET_SECRET_KEY, AES.MODE_EAX)
    nonce = cipher.nonce
    encrypted_key, tag = cipher.encrypt_and_digest(plaintext_key)
    return (encrypted_key, nonce, tag)

# Create new key, return its id.
@api.route("/v1/key", methods=["POST"])
def create_key():
    try:
        new_account = web3.Account.create()
        (encrypted_key, nonce, tag) = encrypt_key(new_account.key)
        key_entry = Key(private_key=encrypted_key, nonce=nonce, tag=tag, address=new_account.address)
        key_entry.create()
        rv = rsp_success(data = key_entry.json())
        rv.headers["Location"] = "/api/v1/key/%s" % key_entry.key_id
        return rv
    except Exception as e:
        db.session.rollback()
        error_msg = "Exception %s caught while processing request." % str(e)
        logging.error(error_msg)
        return rsp_err(msg=error_msg, status=500)

@api.route("/v1/key/search", methods=["GET"])
def find_key():
    try:
        form = get_form()
        address = form.get("address", "")
        key_entry = Key.query.filter_by(address=address).first()
        if key_entry is None:
            return make_response("Key not found", 404)
        return rsp_success(data={
            "items": [key_entry.key_id],
            "total_count": 1
        })
    except Exception as e:
        db.session.rollback()
        error_msg = "Exception %s caught while processing request." % str(e)
        logging.error(error_msg)
        return rsp_err(msg=error_msg, status=500)

@api.route("/v1/key/<string:key_id>", methods=["DELETE"])
def delete_key(key_id):
    try:
        key_entry = Key.query.filter_by(key_id=key_id).first()
        if key_entry is None:
            return make_response("Key not found", 404)
        key_entry.delete()
        return rsp_success()
    except Exception as e:
        db.session.rollback()
        error_msg = "Exception %s caught while processing request." % str(e)
        logging.error(error_msg)
        return rsp_err(msg=error_msg, status=500)

# Get address
@api.route("/v1/key/<string:key_id>/address", methods=["GET"])
def get_address(key_id):
    try:
        key_entry = Key.query.filter_by(key_id=key_id).first()
        if key_entry is None:
            return make_response("Key not found", 404)
        return rsp_success(data = key_entry.address)
    except Exception as e:
        db.session.rollback()
        error_msg = "Exception %s caught while processing request." % str(e)
        logging.error(error_msg)
        return rsp_err(msg=error_msg, status=500)

# Get signature of provided data
@api.route("/v1/key/<string:key_id>/sign_message", methods=["POST"])
def sign_message(key_id):
    try:
        from eth_account.messages import encode_defunct
        form = get_form()
        data = form.get("message", "")
        key_entry = Key.query.filter_by(key_id=key_id).first()
        if key_entry is None:
            return make_response("Key not found", 404)
        pk = decrypt_key(key_entry.private_key, key_entry.nonce, key_entry.tag)
        acc = web3.Account.from_key(pk)
        rv = acc.sign_message(encode_defunct(hexstr=data))
        rv = dict((k, rv[k] if k == "v" else hex(rv[k])) for k in ["r", "s", "v"])
        return rsp_success(data = rv)
    except Exception as e:
        db.session.rollback()
        error_msg = "Exception %s caught while processing request." % str(e)
        logging.error(error_msg)
        return rsp_err(msg=error_msg, status=500)

# Get signature of provided data
@api.route("/v1/key/<string:key_id>/sign_hash", methods=["POST"])
def sign_hash(key_id):
    try:
        from eth_account.messages import encode_defunct
        form = get_form()
        data = form.get("hash", "")
        key_entry = Key.query.filter_by(key_id=key_id).first()
        if key_entry is None:
            return make_response("Key not found", 404)
        pk = decrypt_key(key_entry.private_key, key_entry.nonce, key_entry.tag)
        acc = web3.Account.from_key(pk)
        try:
            rv = acc.signHash(data)
            rv = dict((k, rv[k] if k == "v" else hex(rv[k])) for k in ["r", "s", "v"])
            return rsp_success(data = rv)
        except ValueError:
            return make_response("The message hash must be exactly 32-bytes", 400)
    except Exception as e:
        db.session.rollback()
        error_msg = "Exception %s caught while processing request." % str(e)
        logging.error(error_msg)
        return rsp_err(msg=error_msg, status=500)

# Sign transaction
@api.route("/v1/key/<string:key_id>/sign_tx", methods=["POST"])
def sign_tx(key_id):
    try:
        form = get_form()
        data = form.get("transaction", "")
        key_entry = Key.query.filter_by(key_id=key_id).first()
        if key_entry is None:
            return make_response("Key not found", 404)
        pk = decrypt_key(key_entry.private_key, key_entry.nonce, key_entry.tag)
        acc = web3.Account.from_key(pk)
        try:
            rv = acc.sign_transaction(data)
            return rsp_success(data = rv)
        except ValueError as e:
            return make_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        error_msg = "Exception %s caught while processing request." % str(e)
        logging.error(error_msg)
        return rsp_err(msg=error_msg, status=500)



