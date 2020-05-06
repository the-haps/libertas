from django.http.response import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from libertas.models import Ausgabe
from django.contrib import messages
from django.http import Http404
from libertas.models import Code, User, Configuration
from datetime import date, datetime
from django.contrib.auth import logout


def ual(request, type, name, number):
    user = User.objects.get(username=request.user)
    if type == "v":
        user.profile.ual += "V [" + str(datetime.now()) + "] Zugriff auf Viewer: " + \
            name + " (#" + number + ") - " + \
            request.META.get('REMOTE_ADDR') + " - " + \
            request.META['HTTP_USER_AGENT'] + "\n"
    if type == "d":
        user.profile.ual += "D [" + str(datetime.now()) + "] Zugriff auf Datei:    " + \
            name + " (#" + str(number) + ") - " + \
            request.META.get('REMOTE_ADDR') + " - " + \
            request.META['HTTP_USER_AGENT'] + "\n"
    user.save()


def wartung(request):
    if Configuration.objects.get(name="Einstellungen").wartung_voll:
        if request.user.is_superuser:
            messages.error(request, 'Wartungsmodus (Voll) aktiviert!')
        else:
            return "voll"

    if Configuration.objects.get(name="Einstellungen").wartung_auth:
        if request.user.is_authenticated:
            if request.user.is_superuser:
                messages.error(
                    request, 'Wartungsmodus (Authentifizierungssystem) aktiviert!')
            else:
                messages.warning(
                    request, 'Du wurdest aufgrund von Wartungsarbeiten abgemeldet.')
                logout(request)

    if Configuration.objects.get(name="Einstellungen").wartung_signup:
        if request.user.is_superuser:
            messages.error(request, 'Wartungsmodus (Registrierung) aktiviert!')

    if Configuration.objects.get(name="Einstellungen").wartung_viewer:
        if request.user.is_superuser:
            messages.error(request, 'Wartungsmodus (Viewer) aktiviert!')
        else:
            return "viewer"


def viewer(request, number, view_type):
    if wartung(request) == "voll":
        return render(request, 'libertas/wartung.html')
    elif wartung(request) == "viewer" and view_type != "thumbnail":
        messages.error(
            request, """Aufgrund von Wartungsarbeiten lassen sich zurzeit keine digitalen Ausgaben und Leseproben lesen.
            <a href="https://status.thehaps.de/">Hier</a> findest du mehr Informationen.""")
        return redirect('index')

    ausgabe = get_object_or_404(Ausgabe, number=number)
    if view_type == "read" and request.user.is_authenticated:
        if date.today() >= ausgabe.publish_date:
            user = User.objects.get(username=request.user)
            if Code.objects.filter(user=user, ausgabe=ausgabe).exists():
                ual(request, "v", ausgabe.name, number)
                pdf_data = "%s/0" % ausgabe.file_identifier
                pdf_name = ausgabe.name
            else:
                messages.error(request, """<strong>Du bist nicht im Besitz dieser Ausgabe.</strong>
                                        Wenn du im Besitz eines Codes bist, löse ihn ein,
                                        um Zugriff auf die Ausgabe zu bekommen.""")
                return redirect('redeem')
        else:
            raise Http404()
    elif view_type == "leseprobe" and request.user.is_authenticated:
        if date.today() >= ausgabe.publish_date or ausgabe.force_visible:
            if ausgabe.leseprobe:
                pdf_data = "%s/1" % ausgabe.file_identifier
                pdf_name = "%s (Leseprobe)" % ausgabe.name
            else:
                raise Http404()
        else:
            raise Http404()
    elif view_type == "thumbnail":
        if date.today() >= ausgabe.publish_date or ausgabe.force_visible:
            if ausgabe.thumbnail:
                return FileResponse(ausgabe.thumbnail)
            else:
                raise Http404()
        else:
            raise Http404()
    else:
        messages.error(
            request, """Du musst dich zuerst anmelden um eine Ausgabe oder Leseprobe zu lesen.""")
        return redirect('signin')

    return render(request, 'viewer/viewer.html', {'pdf_data': pdf_data, 'pdf_name': pdf_name})


def protected_file(request, identifier, view_type):
    if wartung(request) == "voll":
        return render(request, 'libertas/wartung.html')
    elif wartung(request) == "viewer":
        messages.error(
            request, """Aufgrund von Wartungsarbeiten lassen sich zurzeit keine digitalen Ausgaben und Leseproben lesen.
            <a href="https://status.thehaps.de/">Hier</a> findest du mehr Informationen.""")
        return redirect('index')

    ausgabe = get_object_or_404(Ausgabe, file_identifier=identifier)
    if view_type == "0" and request.user.is_authenticated and date.today() >= ausgabe.publish_date:
        ual(request, "d", ausgabe.name, ausgabe.number)
        user = User.objects.get(username=request.user)
        if Code.objects.filter(user=user, ausgabe=ausgabe).exists():
            return FileResponse(ausgabe.file)
        else:
            raise Http404()
    elif view_type == "1" and request.user.is_authenticated and \
            (date.today() >= ausgabe.publish_date or ausgabe.force_visible):
        return FileResponse(ausgabe.leseprobe)
    else:
        raise Http404()
