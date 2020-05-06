from django.db import models
from django.contrib.auth.models import User
import string
import random


def generate_id(length=16):
    pool = string.ascii_lowercase + string.digits
    return ''.join(random.choice(pool) for i in range(length))


def generate_code(length=12):
    pool = string.ascii_uppercase + string.digits + string.digits
    return ''.join(random.choice(pool) for i in range(length))


class Ausgabe(models.Model):
    name = models.CharField(max_length=64)
    publish_date = models.DateField('Erscheinungsdatum', blank=True, null=True)
    force_visible = models.BooleanField(verbose_name="Sichtbarkeit erzwingen", default=False)
    number = models.IntegerField('Ausgaben-Nr.', primary_key=True)
    file_identifier = models.CharField(
        max_length=16, default=generate_id, unique=True)
    file = models.FileField('Datei', upload_to='ausgaben')
    leseprobe = models.FileField(upload_to='leseproben', blank=True)
    thumbnail = models.FileField(upload_to='thumbnails')

    def __str__(self):
        return "%s (#%s)" % (self.name, self.number)

    class Meta:
        verbose_name = "Ausgabe"
        verbose_name_plural = "Ausgaben"


class Code(models.Model):
    code = models.CharField(
        max_length=12, primary_key=True)
    creation = models.DateTimeField('Erstellung', auto_now_add=True)
    ausgabe = models.ForeignKey(
        Ausgabe, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None,
                             blank=True, null=True, verbose_name='Benutzer')
    redeemed = models.DateTimeField(
        'Zeitpunkt', default=None, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_code()
        super(Code, self).save(*args, **kwargs)

    def __str__(self):
        return "%s****" % (self.code[:-4])

    class Meta:
        verbose_name = "Code"
        verbose_name_plural = "Codes"


class Configuration(models.Model):
    name = models.CharField(
        max_length=16, default="Einstellungen", unique=True)
    wartung_voll = models.BooleanField(
        verbose_name="Wartungsmodus (Voll)", default=False)
    wartung_auth = models.BooleanField(
        verbose_name="Wartungsmodus (Auth)", default=False)
    wartung_signup = models.BooleanField(
        verbose_name="Wartungsmodus (Registrierung)", default=False)
    wartung_viewer = models.BooleanField(
        verbose_name="Wartungsmodus (Viewer)", default=False)
    wartung_corona = models.BooleanField(
        verbose_name="Wartungsmodus (Corona-Bestellsystem)", default=False)

    class Meta:
        verbose_name = "Konfiguration"
        verbose_name_plural = "Konfiguration"

    def __str__(self):
        return "Einstellungen"
