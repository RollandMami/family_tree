from datetime import date, timedelta
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image

from apps.genealogy.models import Personne
from .models import EvenementFamilial

def redimensionner_image_evenement(evenement, max_width=1200, max_height=600):
    """Redimensionne l'image de l'événement pour tenir dans le cadre."""
    if not evenement.image:
        return

    try:
        image_path = evenement.image.path
        img = Image.open(image_path)

        # Si déjà dans la taille = rien à faire
        if img.width <= max_width and img.height <= max_height:
            return

        img.thumbnail((max_width, max_height), Image.LANCZOS)

        output = BytesIO()
        format = img.format or 'JPEG'
        if format.upper() == 'JPG':
            format = 'JPEG'

        if format.upper() == 'PNG':
            img.save(output, format='PNG', optimize=True)
        else:
            img = img.convert('RGB')
            img.save(output, format='JPEG', quality=85, optimize=True)

        output.seek(0)
        evenement.image.save(evenement.image.name, ContentFile(output.read()), save=False)
        evenement.save(update_fields=['image'])
    except Exception as e:
        # En cas d'échec, on ignore pour ne pas bloquer l'enregistrement
        print('Erreur de redimensionnement image:', e)


def obtenir_agenda_proche(jours=5):
    aujourdhui = date.today()
    date_limite = aujourdhui + timedelta(days=jours)
    
    # 1. Anniversaires de naissance (si en vie)
    anniversaires = Personne.objects.filter(
        est_en_vie=True,
        date_naissance__month=aujourdhui.month,
        date_naissance__day__range=(aujourdhui.day, date_limite.day)
    )

    # 2. Commémorations de décès (Anniversaires de mort)
    deces_commem = Personne.objects.filter(
        est_en_vie=False,
        date_deces__month=aujourdhui.month,
        date_deces__day__range=(aujourdhui.day, date_limite.day)
    )

    # 3. Événements programmés (Mariages, etc.)
    evenements = EvenementFamilial.objects.filter(
        date_evenement__range=(aujourdhui, date_limite)
    )

    return {
        'anniversaires': anniversaires,
        'commemorations': deces_commem,
        'evenements': evenements
    }