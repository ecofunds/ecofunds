from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.db.utils import IntegrityError
from ecofunds.user.models import UserType

#definicoes das permissoes customizadas para a aplicacao
PERMISSIONS = {
        ('ecofunds','organization'):(
           ('edit your own', 'ownedit_organization'),
           ('edit your region', 'regionedit_organization'),
           ('edit in your organization','orgedit_organization'),
           ),
        ('ecofunds','project'):(
           ('edit your own', 'ownedit_project'),
           ('edit your region', 'regionedit_project'), 
           ('edit in your organization','orgedit_project'),
           ),
        ('ecofunds','investment'):(
           ('edit your own', 'ownedit_investment'),
           ('edit your region', 'regionedit_investment'), 
           ('edit in your organization','orgedit_investment'),
           ),
        }
#definicao de tipos de usuarios e ligacao com as permissoes (customizadas ou nao)
#superadmin nao eh necessario pois eh possivel usar o super_user para o mesmo papel
USER_TYPE_PERMISSIONS = {
        #exatamente o q o usuario regular pode fazer? verificar.
        'incompleteuser':(),
        'superadmin':(),
        'regularuser':('add_project','ownedit_project',
            'add_organization','ownedit_organization',
            'add_investment','ownedit_investment'),
        'organizationadmin':('add_project','orgedit_project',
            'add_organization','orgedit_organization',
            'add_investment','orgedit_investment'),
        'focalpoint':('add_project','ownedit_project','regionedit_project',
            'add_organization','ownedit_organization','regionedit_organization',
            'add_investment','ownedit_investment','regionedit_investment'),
        }

#precisa criar as permissoes, os user_types, e ja atribuir ela aos user_types
def create_permissions():
    for item in PERMISSIONS:
        app , modelname = item
        contenttype = ContentType.objects.get(app_label=app,model=modelname)
        for permname in PERMISSIONS[item]:
            try:
                p,created = Permission.objects.get_or_create(name=permname[0],
                        codename=permname[1],
                        content_type=contenttype)
            except IntegrityError:
                #ja foi cadastrado. A chave primaria eh composta, entao
                #o get_or_create nao funciona direito
                print 'integrity errror'
                pass
            if created:
                print "permission %s created"%p 

def relate_user_type():
    for typename in USER_TYPE_PERMISSIONS:
        user_type,created = UserType.objects.get_or_create(name=typename )
        user_type.save()
        if created:
            for  permcode in USER_TYPE_PERMISSIONS[typename]:
                perm = Permission.objects.get(codename=permcode)
                user_type.permissions.add(perm)
                print 'permissao %s adicionada a user_type %s'%(perm,user_type)
            print "UserType %s created"%typename
    
def edit_allowance(obj,userprofile):
    return userprofile.is_allowed(obj,'change') or userprofile.is_allowed(obj,'regionedit') or userprofile.is_allowed(obj,'orgedit') or userprofile.is_allowed(obj,'ownedit')

#retorna o content type de um objeto
#eh necessario para verificar as permissoes relativas a ele
def get_content_type(obj):
    modelname = obj.__class__.__name__.lower()
    modulename = obj.__class__.__module__
    modules = modulename.split('.')
    app = modules[-2:-1][0].lower()
    contenttype = ContentType.objects.get(app_label=app,model=modelname)
    return contenttype
