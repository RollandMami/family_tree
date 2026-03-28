from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.events.models import EvenementFamilial
from apps.notifications.models import Notification
from apps.events.utils import obtenir_agenda_proche
from apps.events.forms import EvenementForm
from .models import Personne, Couple
from .forms import AddMemberForm

@login_required
def home(request):
    # 1. Récupérer les événements récents (le "Feed")
    # On prend les 10 derniers événements publiés
    feed_events = EvenementFamilial.objects.all().order_by('-date_evenement')[:10]
    form_event = EvenementForm()

    # 2. Récupérer les alertes J-5 (Anniversaires/Décès)
    agenda = obtenir_agenda_proche(jours=5)

    # 3. Récupérer les notifications non lues de l'utilisateur
    notifications_recentes = Notification.objects.filter(
        destinataire=request.user, 
        est_lue=False
    ).order_by('-date_creation')[:5]

    context = {
        'form_event': form_event,
        'feed_events': feed_events,
        'anniversaires': agenda['anniversaires'],
        'commemorations': agenda['commemorations'],
        'notifications': notifications_recentes,
    }
    
    return render(request, 'genealogy/home.html', context)

@login_required
def person_details(request, person_id):
    personne = get_object_or_404(Personne, id=person_id)
    return render(request, 'genealogy/partials/person_aside.html', {'personne': personne})

@login_required
def person_details_ajax(request, person_id):
    personne = get_object_or_404(Personne, id=person_id)
    profil_personne = None
    if hasattr(request.user, 'profile') and request.user.profile.personne:
        profil_personne = request.user.profile.personne

    is_admin = request.user.is_staff or request.user.is_superuser
    relation = 'distant'

    if profil_personne:
        relation = profil_personne.get_relation_to(personne)

    if is_admin:
        relation = 'admin'

    return render(request, 'genealogy/partials/person_aside_content.html', {
        'personne': personne,
        'relation': relation,
        'is_admin': is_admin,
    })

@login_required
def add_member(request):
    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            related_person_id = form.cleaned_data['related_person_id']
            relation_type = form.cleaned_data['relation_type']
            prenom = form.cleaned_data['prenom']
            nom = form.cleaned_data['nom']
            genre = form.cleaned_data['genre']
            date_naissance = form.cleaned_data['date_naissance']
            date_deces = form.cleaned_data['date_deces']
            est_en_vie = form.cleaned_data['est_en_vie']

            if not est_en_vie and not date_deces:
                messages.error(request, "Pour une personne décédée, merci de saisir la date de décès.")
                return redirect('tree_view')

            parent = get_object_or_404(Personne, id=related_person_id)

            nouveau = Personne.objects.create(
                prenom=prenom,
                nom=nom,
                genre=genre,
                date_naissance=date_naissance,
                date_deces=date_deces,
                est_en_vie=est_en_vie,
            )

            if relation_type == 'enfant':
                if parent.genre == 'H':
                    nouveau.pere_bio = parent
                else:
                    nouveau.mere_bio = parent
                nouveau.save()
                messages.success(request, f"{nouveau.nom} ajouté(e) comme enfant de {parent.prenom}.")

            elif relation_type == 'conjoint':
                if parent.genre == 'H':
                    Couple.objects.create(homme=parent, femme=nouveau)
                else:
                    Couple.objects.create(homme=nouveau, femme=parent)
                messages.success(request, f"{nouveau.nom} ajouté(e) comme conjoint(e) de {parent.prenom}.")

            return redirect('tree_view')
        else:
            messages.error(request, "Erreur lors de l'ajout du membre. Vérifiez les champs.")
            return redirect('tree_view')


@login_required
def delete_member(request, person_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    personne = get_object_or_404(Personne, id=person_id)
    personne.delete()

    return JsonResponse({'success': True})


@login_required
def tree_view(request):
    # 1. On récupère toutes les personnes qui n'ont pas de parents enregistrés (ancêtres)
    ancetres = Personne.objects.filter(
        pere_bio__isnull=True,
        mere_bio__isnull=True
    )

    # 2. On veut exclure les conjoints qui ne sont « pas des ancêtres » (partenaire d'une personne ayant déjà des parents)
    conjoints_a_exclure = set()
    for couple in Couple.objects.select_related('homme', 'femme'):
        # Si l'un des deux partenaires a un parent, on ne doit pas considérer l'autre sans parents comme une racine séparée
        homme_est_fils = couple.homme.pere_bio or couple.homme.mere_bio
        femme_est_fille = couple.femme.pere_bio or couple.femme.mere_bio

        if homme_est_fils and not femme_est_fille:
            conjoints_a_exclure.add(couple.femme_id)
        if femme_est_fille and not homme_est_fils:
            conjoints_a_exclure.add(couple.homme_id)

    # 3. Filtres sur les ancêtres évitant les doublons de branches
    ancetres = ancetres.exclude(id__in=conjoints_a_exclure)

    racines_finales = []
    vus = set()

    for p in ancetres:
        if p.id in vus:
            continue

        racines_finales.append(p)
        vus.add(p.id)

        union = p.unions_h.first() or p.unions_f.first()
        if union:
            conjoint = union.femme if p.genre == 'H' else union.homme
            if conjoint:
                vus.add(conjoint.id)

    def build_tree(node_personne, visited, allowed_ids=None, depth=None):
        if node_personne.id in visited:
            return None
        if allowed_ids is not None and node_personne.id not in allowed_ids:
            return None
        if depth is not None and depth < 0:
            return None

        visited.add(node_personne.id)

        union = node_personne.unions_h.first() or node_personne.unions_f.first()
        conjoint = None
        if union:
            if node_personne.genre == 'H':
                if union.femme and (allowed_ids is None or union.femme.id in allowed_ids):
                    conjoint = union.femme
            else:
                if union.homme and (allowed_ids is None or union.homme.id in allowed_ids):
                    conjoint = union.homme

        enfants = []
        if depth is None or depth > 0:
            for enfant in node_personne.enfants_bio:
                child_tree = build_tree(enfant, visited, allowed_ids, None if depth is None else depth - 1)
                if child_tree is not None:
                    enfants.append(child_tree)

        return {
            'personne': node_personne,
            'conjoint': conjoint,
            'enfants': enfants,
        }

    pivot_id = request.GET.get('pivot')
    pivot = None
    tree_data = []
    if pivot_id:
        try:
            pivot = Personne.objects.get(id=pivot_id)
        except Personne.DoesNotExist:
            pivot = None

    if pivot:
        pivot_parents = [p for p in [pivot.pere_bio, pivot.mere_bio] if p]
        pivot_grands = [gp for p in pivot_parents for gp in [p.pere_bio, p.mere_bio] if gp]
        pivot_siblings = list(pivot.get_freres_soeurs_purs()) + list(pivot.get_demi_freres_soeurs())
        pivot_children = list(pivot.enfants_bio)

        allowed_ids = {pivot.id}
        allowed_ids.update(p.id for p in pivot_parents)
        allowed_ids.update(gp.id for gp in pivot_grands)
        allowed_ids.update(s.id for s in pivot_siblings)
        allowed_ids.update(c.id for c in pivot_children)

        root_candidates = pivot_grands or pivot_parents or [pivot]

        visited_ids = set()
        for root in root_candidates:
            root_tree = build_tree(root, visited_ids, allowed_ids=allowed_ids, depth=4)
            if root_tree:
                tree_data.append(root_tree)
    else:
        visited_ids = set()
        for root in racines_finales:
            root_tree = build_tree(root, visited_ids)
            if root_tree:
                tree_data.append(root_tree)

    context = {
        'tree_data': tree_data,
        'racines': racines_finales,
        'pivot': pivot,
    }
    return render(request, 'genealogy/tree.html', context)