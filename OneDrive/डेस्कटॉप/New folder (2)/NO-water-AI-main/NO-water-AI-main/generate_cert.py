import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

"""Utility to create a self‑signed certificate (cert.pem/key.pem) for localhost.

The script prefers to invoke `openssl` if it is available.  If openssl is
missing we fall back to a pure‑Python generator using the `cryptography`
package (which is added to requirements).  If neither method works the user
is shown manual instructions.
The certificate is valid for 1 year and uses a 2048‑bit RSA key.
"""

# try importing cryptography so we can generate a cert without external tools
try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
except ImportError:
    x509 = None  # indicates fallback unavailable


def _generate_with_cryptography(cert_path: str, key_path: str) -> bool:
    """Return True if generation succeeded, False otherwise."""
    if x509 is None:
        return False

    # create private key
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
        )
        .sign(private_key, hashes.SHA256(), default_backend())
    )

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    with open(key_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            )
        )
    return True


def main():
    cert = "cert.pem"
    key = "key.pem"

    if os.path.exists(cert) and os.path.exists(key):
        print(f"Certificates already exist ({cert}, {key}), skipping generation.")
        return

    print("Generating a self-signed certificate for localhost...")

    # first try openssl
    cmd = [
        "openssl",
        "req",
        "-x509",
        "-nodes",
        "-days",
        "365",
        "-newkey",
        "rsa:2048",
        "-keyout",
        key,
        "-out",
        cert,
        "-subj",
        "/CN=localhost",
    ]

    try:
        subprocess.check_call(cmd)
        print(f"Created {cert} and {key} using openssl.")
        return
    except FileNotFoundError:
        print("`openssl` command not found, falling back to Python (cryptography).")
    except subprocess.CalledProcessError as e:
        print(f"openssl returned error code {e.returncode}, attempting Python fallback.")

    # try Python fallback
    if _generate_with_cryptography(cert, key):
        print(f"Created {cert} and {key} using cryptography library.")
        return

    # last resort: manual instructions
    print(
        "Unable to automatically create certificates.\n"
        "Either install OpenSSL or install the `cryptography` Python package:\n"
        "    pip install cryptography\n"
        "Then re-run this script, or create the files manually using:\n"
        "  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\    \"-keyout key.pem -out cert.pem -subj \"/CN=localhost\"\n",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
