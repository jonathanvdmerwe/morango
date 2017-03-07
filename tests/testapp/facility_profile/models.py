from __future__ import unicode_literals

import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone
from morango.query import SyncableModelQuerySet
from morango.utils.morango_mptt import MorangoMPTTModel
from morango.utils.register_models import register_morango_profile
from morango.utils.uuids import UUIDField
from mptt.models import TreeForeignKey


FacilityDataSyncableModel = register_morango_profile(profile="facilitydata", partitions=("facility", "user"), module=__package__)


class BaseQuerySet(SyncableModelQuerySet):
    pass


class Facility(MorangoMPTTModel, FacilityDataSyncableModel):
    # Morango syncing settings
    morango_model_name = "facility"
    uuid_input_fields = ("name",)

    name = models.CharField(max_length=100)
    now_date = models.DateTimeField(default=timezone.now)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def get_partition_names(self, *args, **kwargs):
        return {}


class MyUser(AbstractBaseUser, FacilityDataSyncableModel):
    # Morango syncing settings
    morango_model_name = "user"
    uuid_input_fields = ("username",)

    USERNAME_FIELD = "username"

    username = models.CharField(max_length=20)

    objects = BaseQuerySet.as_manager()

    def get_partition_names(self, *args, **kwargs):
        return {}


class Log(FacilityDataSyncableModel):
    # Morango syncing settings
    morango_model_name = "contentsummarylog"
    uuid_input_fields = ("user_id", "content_id")

    user = models.ForeignKey(MyUser)
    content_id = UUIDField(db_index=True, default=uuid.uuid4)

    def get_partition_names(self, *args, **kwargs):
        pass


class ProxyParent(MorangoMPTTModel):

    kind = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        self._ensure_kind()
        super(ProxyParent, self).save(*args, **kwargs)

    def _ensure_kind(self):
        if self._KIND:
            self.kind = self._KIND

    def get_partition_names(self, *args, **kwargs):
        return {}


class ProxyManager(models.Manager):
    pass


class ProxyModel(ProxyParent):

    morango_model_name = 'proxy'
    _KIND = 'proxy'

    objects = ProxyManager()

    class Meta:
        proxy = True

    def get_partition_names(self, *args, **kwargs):
        return {}