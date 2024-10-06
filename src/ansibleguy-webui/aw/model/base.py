from django.db import models

CHOICES_BOOL = (
    (True, 'Yes'),
    (False, 'No')
)
DEFAULT_NONE = {'null': True, 'default': None, 'blank': True}
JOB_EXEC_STATUS_SUCCESS = 4
JOB_EXEC_STATUS_FAILED = 3
CHOICES_JOB_EXEC_STATUS = [
    (0, 'Waiting'),
    (1, 'Starting'),
    (2, 'Running'),
    (JOB_EXEC_STATUS_FAILED, 'Failed'),
    (JOB_EXEC_STATUS_SUCCESS, 'Finished'),
    (5, 'Stopping'),
    (6, 'Stopped'),
]
JOB_EXEC_STATUS_ACTIVE = [0, 1, 2, 5]


class BareModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class BaseModel(BareModel):
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
