from django.conf.urls.defaults import patterns, url
from utilisateurs.views import login, logout, add_user, list_user, delete_user, ajax_user, edit_user, set_password, export_user

urlpatterns = patterns('',
                       (r'^connexion/$', login),
                       (r'^deconnexion/$', logout),
                       (r'^utilisateurs/ajout/$', add_user),
                       (r'^utilisateurs/editer/(?P<user_id>.+?)$', edit_user),
                       (r'^utilisateurs/supprimer/(?P<user_id>.+?)$', delete_user),
                       (r'^utilisateurs/mot-de-passe/(?P<user_id>.+?)$', set_password),
                       (r'^utilisateurs/ajax/$', ajax_user),
                       (r'^utilisateurs/$', list_user),
                       (r'^utilisateurs/export/(?P<filetype>.+?)/$', export_user),
)
