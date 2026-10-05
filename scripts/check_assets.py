"""Public-asset audit; prints only findings, never secret values."""
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
private=['SECRET_KEY','STRIPE_SECRET_KEY','STRIPE_WEBHOOK_SECRET','EMAIL_HOST_PASSWORD','DATABASE_URL']
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
findings=[]
for path in (ROOT/'static').rglob('*'):
    if not path.is_file(): continue
    if path.name.startswith('.') or path.suffix in ('.sqlite3','.env','.map'): findings.append(f'Unexpected public file: {path.name}')
    data=path.read_bytes()
    for key in private:
        value=os.getenv(key,'')
        if value and len(value)>12 and value.encode() in data: findings.append(f'Exposed environment variable: {key}')
    for marker in (b'sk_live_',b'sk_test_',b'whsec_',b'BEGIN PRIVATE KEY'):
        if marker in data: findings.append(f'Credential marker in {path.name}')
if findings:
    print('\n'.join(findings));raise SystemExit(1)
print('Public asset audit passed: no private environment values or credential markers found.')
