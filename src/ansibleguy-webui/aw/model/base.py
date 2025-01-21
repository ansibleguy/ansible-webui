from django.db import models

CHOICES_BOOL = (
    (True, 'Yes'),
    (False, 'No')
)
DEFAULT_NONE = {'null': True, 'default': None, 'blank': True}
JOB_EXEC_STATUS_WAIT = 0
JOB_EXEC_STATUS_START = 1
JOB_EXEC_STATUS_RUN = 2
JOB_EXEC_STATUS_FAILED = 3
JOB_EXEC_STATUS_SUCCESS = 4
JOB_EXEC_STATUS_STOPPING = 5
JOB_EXEC_STATUS_RETRY = 7
CHOICES_JOB_EXEC_STATUS = [
    (JOB_EXEC_STATUS_WAIT, 'Waiting'),
    (JOB_EXEC_STATUS_START, 'Starting'),
    (JOB_EXEC_STATUS_RUN, 'Running'),
    (JOB_EXEC_STATUS_FAILED, 'Failed'),
    (JOB_EXEC_STATUS_SUCCESS, 'Finished'),
    (JOB_EXEC_STATUS_STOPPING, 'Stopping'),
    (6, 'Stopped'),
    (JOB_EXEC_STATUS_RETRY, 'Retry'),
]
JOB_EXEC_STATI_ACTIVE = [
    JOB_EXEC_STATUS_WAIT,
    JOB_EXEC_STATUS_START,
    JOB_EXEC_STATUS_RUN,
    JOB_EXEC_STATUS_STOPPING,
    JOB_EXEC_STATUS_RETRY,
]


class BareModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class BaseModel(BareModel):
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
