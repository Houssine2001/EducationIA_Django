"""
Database Router pour diriger les modèles vers la bonne base de données
- SQLite (default): auth, sessions, admin, contenttypes
- MongoDB (mongodb): evaluation (tous les modèles de l'app evaluation)
"""

class DatabaseRouter:
    """
    Router pour gérer plusieurs bases de données
    """
    
    # Apps Django qui utilisent SQLite
    django_apps = {'auth', 'contenttypes', 'sessions', 'admin', 'messages'}
    
    # Apps personnalisées qui utilisent MongoDB
    mongodb_apps = {'evaluation'}
    
    def db_for_read(self, model, **hints):
        """
        Diriger les lectures vers la bonne base de données
        """
        if model._meta.app_label in self.mongodb_apps:
            return 'mongodb'
        if model._meta.app_label in self.django_apps:
            return 'default'
        return None
    
    def db_for_write(self, model, **hints):
        """
        Diriger les écritures vers la bonne base de données
        """
        if model._meta.app_label in self.mongodb_apps:
            return 'mongodb'
        if model._meta.app_label in self.django_apps:
            return 'default'
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Autoriser les relations entre objets de la même base
        """
        db1 = obj1._meta.app_label
        db2 = obj2._meta.app_label
        
        if db1 in self.mongodb_apps and db2 in self.mongodb_apps:
            return True
        if db1 in self.django_apps and db2 in self.django_apps:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Autoriser les migrations sur la bonne base
        """
        if app_label in self.mongodb_apps:
            return db == 'mongodb'
        if app_label in self.django_apps:
            return db == 'default'
        return None
