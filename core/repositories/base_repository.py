from django.core.paginator import Paginator

class BaseRepository:
    model = None
    
    @classmethod
    def get_all(cls, page=1, per_page=10):
        queryset = cls.model.objects.all()
        paginator = Paginator(queryset, per_page)
        return paginator.get_page(page)
    
    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.model.objects.get(id=id)
        except cls.model.DoesNotExist:
            return None
    
    @classmethod
    def create(cls, **kwargs):
        return cls.model.objects.create(**kwargs)
    
    @classmethod
    def update(cls, id, **kwargs):
        instance = cls.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
        return instance
    
    @classmethod
    def delete(cls, id):
        instance = cls.get_by_id(id)
        if instance:
            instance.delete()
            return True
        return False
