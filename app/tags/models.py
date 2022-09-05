from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class TaggedItemManager(models.Manager):
    # Create a custom manager class insted of ContentType.objects
    # Instants of this class can be accesed by using TaggedItem class
    def get_tags_for(self, obj_type, obj_id):
        """
        This is a custom function for get taged product ,
        it restuns a queryset
        obj_type: e.g Product,..
        obj_id : object id

        """
        content_type = ContentType.objects.get_for_model(obj_type)

        return TaggedItem.objects \
            .select_related('tag') \
            .filter(
                content_type=content_type,
                object_id=obj_id
            )


class Tag(models.Model):
    label = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.label


class TaggedItem(models.Model):
    objects = TaggedItemManager()
    # What tag applied to what object
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    # Content Type -- product, aricle...
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()  # Actual product

# Example for creating generic relationship
# conterntType is a model in django contain referece to all models
