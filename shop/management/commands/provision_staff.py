import getpass
from pathlib import Path
from django.core.management.base import BaseCommand,CommandError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group,Permission
from django_otp.plugins.otp_totp.models import TOTPDevice
from shop.models import Customer,Audit

class Command(BaseCommand):
    help = 'Provisiona staff por terminal privado; TOTP é obrigatório. Nunca use saída em logs públicos.'
    def add_arguments(self,parser):
        parser.add_argument('--email',required=True)
        parser.add_argument('--role',choices=['owner','catalog','support'],default='owner')
        parser.add_argument('--output',required=True,help='Arquivo privado para a URI do autenticador')
    def handle(self,*args,**opts):
        email=opts['email'].lower().strip()
        if Customer.objects.filter(email=email).exists(): raise CommandError('Conta já existente. Não há promoção automática.')
        password=getpass.getpass('Senha do administrador: ')
        user=Customer(email=email,username=email,is_staff=True,is_active=True,email_verified=True,is_superuser=opts['role']=='owner')
        try: validate_password(password,user)
        except ValidationError as exc: raise CommandError('; '.join(exc.messages))
        from django.db import transaction
        with transaction.atomic():
            user.set_password(password);user.save()
            if opts['role'] != 'owner':
                allowed = ['product','variant','productimage','category','collection','banner'] if opts['role']=='catalog' else ['order']
                group,_=Group.objects.get_or_create(name='KYMA '+opts['role'])
                perms=Permission.objects.filter(content_type__app_label='shop',content_type__model__in=allowed)
                if opts['role']=='support': perms=perms.filter(codename__in=['view_order','change_order'])
                group.permissions.set(perms);user.groups.add(group)
            device=TOTPDevice.objects.create(user=user,name='KYMA',confirmed=True)
            path=Path(opts['output']).resolve()
            if path.exists(): raise CommandError('Arquivo de destino já existe.')
            path.write_text(device.config_url,encoding='utf-8')
            Audit.objects.create(actor=user,action='staff:provision:'+opts['role'],object_id=str(user.pk))
        self.stdout.write('Conta criada. Importe a URI privada em seu autenticador; proteja e remova esse arquivo após configurar.')
