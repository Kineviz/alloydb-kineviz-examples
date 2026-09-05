"""Initialize local demo credentials once; never prints or overwrites secrets."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
password = secrets.token_hex(24)
path = root / '.env'
with path.open('x') as f:
    path.chmod(0o600)
    f.write('PGHOST=127.0.0.1\nPGPORT=55432\nPGDATABASE=kineviz_demo\nPGUSER=postgres\n')
    f.write(f'PGPASSWORD={password}\nPOSTGRES_PASSWORD={password}\nPGSSLMODE=disable\n')
print('Created .env (mode 600). Copy the password from it only into your local demo connector.')
