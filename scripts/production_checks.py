"""Validate production configuration with synthetic secrets, without contacting services."""
import os
import secrets
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
env=os.environ.copy()
env.update(DEBUG='false',SECRET_KEY=secrets.token_urlsafe(64),ALLOWED_HOSTS='store.example.test',
    SITE_URL='https://store.example.test',CSRF_TRUSTED_ORIGINS='https://store.example.test',
    DATABASE_URL='postgresql://kyma:placeholder@127.0.0.1:5432/kyma',PAYMENT_MODE='stripe',
    STRIPE_SECRET_KEY='sk_test_placeholder',STRIPE_WEBHOOK_SECRET='whsec_placeholder',
    EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',EMAIL_HOST='smtp.example.test')
raise SystemExit(subprocess.run([sys.executable,str(ROOT/'manage.py'),'check','--deploy'],env=env,cwd=ROOT).returncode)
