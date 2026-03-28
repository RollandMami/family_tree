from datetime import date, timedelta
from apps.genealogy.models import Personne
from .models import EvenementFamilial

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