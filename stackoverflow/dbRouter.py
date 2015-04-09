# DB router for stackoverflow
class StackverflowDBRouter(object):
    """
    A router to control stackoverflow db operations
    """
    def db_for_read(self, model, **hints):
        "Point all operations on stackoverflow models to 'db_stackoverflow'"
        from django.conf import settings
        if not settings.DATABASES.has_key('db_stackoverflow'):
            return None
        if model._meta.app_label == 'stackoverflow':
            return 'db_stackoverflow'
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on stackoverflow models to 'db_stackoverflow'"
        from django.conf import settings
        if not settings.DATABASES.has_key('db_stackoverflow'):
            return None
        if model._meta.app_label == 'stackoverflow':
            return 'db_stackoverflow'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in stackoverflow is involved"
        from django.conf import settings
        if not settings.DATABASES.has_key('db_stackoverflow'):
            return None
        if obj1._meta.app_label == 'stackoverflow' or obj2._meta.app_label == 'stackoverflow':
            return True
        return None

    def allow_syncdb(self, db, model):
        "Make sure the stackoverflow app only appears on the 'stackoverflow' db"
        from django.conf import settings
        if not settings.DATABASES.has_key('db_stackoverflow'):
            return None
        if db == 'db_stackoverflow':
            return model._meta.app_label == 'stackoverflow'
        elif model._meta.app_label == 'stackoverflow':
            return False
        return None
