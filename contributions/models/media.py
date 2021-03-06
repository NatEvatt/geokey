from django.db import models
from django.conf import settings

from ..manager import MediaFileManager
from ..base import MEDIA_STATUS


class MediaFile(models.Model):
    """
    Base class for all media files. Not to be instaciate; instaciate one of
    the child classes instead.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    contribution = models.ForeignKey(
        'contributions.Observation', related_name='files_attached'
    )
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        choices=MEDIA_STATUS,
        default=MEDIA_STATUS.active,
        max_length=20
    )

    objects = MediaFileManager()

    class Meta:
        ordering = ['id']
        app_label = 'contributions'

    @property
    def type_name(self):
        """
        Returns the type of media file. To be implemented by child classes.
        """
        raise NotImplementedError(
            'The property `type_name` has not been implemented for this '
            'subclass of `MediaFile`.'
        )

    def delete(self):
        """
        Deletes a file by setting its status to active
        """
        self.status = MEDIA_STATUS.deleted
        self.save()


class ImageFile(MediaFile):
    """
    Stores images uploaded by users.
    """
    image = models.ImageField(upload_to='user-uploads/images')

    class Meta:
        ordering = ['id']
        app_label = 'contributions'

    @property
    def type_name(self):
        """
        Returns 'ImageFile'
        """
        return 'ImageFile'


class VideoFile(MediaFile):
    """
    Stores images uploaded by users.
    """
    video = models.ImageField(upload_to='user-uploads/videos')
    youtube_id = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='user-uploads/videos', null=True)
    youtube_link = models.URLField(max_length=255, null=True, blank=True)
    swf_link = models.URLField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['id']
        app_label = 'contributions'

    @property
    def type_name(self):
        """
        Returns 'VideoFile'
        """
        return 'VideoFile'
