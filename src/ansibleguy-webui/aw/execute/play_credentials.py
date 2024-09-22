from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist

from aw.model.job import Job, JobExecution
from aw.model.job_credential import BaseJobCredentials, JobUserCredentials
from aw.utils.permission import has_credentials_permission, CHOICE_PERMISSION_READ
from aw.base import USERS
from aw.utils.debug import log  # log_warn
from aw.utils.util import is_set, is_null, write_file_0600
from aw.execute.util import config_error


def get_pwd_file(path_run: (str, Path), attr: str) -> str:
    return f"{path_run}/.aw_{attr}"


def get_pwd_file_arg(credentials: BaseJobCredentials, attr: str, path_run: (Path, str)) -> (str, None):
    if is_null(getattr(credentials, attr)):
        return None

    return f"--{BaseJobCredentials.SECRET_ATTRS_ARGS[attr]} {get_pwd_file(path_run=path_run, attr=attr)}"


def write_pwd_file(credentials: BaseJobCredentials, attr: str, path_run: (Path, str)):
    if credentials is None or is_null(getattr(credentials, attr)):
        return None

    return write_file_0600(
        file=get_pwd_file(path_run=path_run, attr=attr),
        content=getattr(credentials, attr),
    )


def _scheduled_or_has_credentials_access(user: USERS, credentials: BaseJobCredentials) -> bool:
    if user is None:
        # scheduled execution; permission has been checked at creation-time
        # todo: add 'owner' to jobs so we can re-check the permissions of scheduled jobs (?)
        return True

    permitted = has_credentials_permission(
        user=user,
        credentials=credentials,
        permission_needed=CHOICE_PERMISSION_READ,
    )
    if not permitted:
        log(
            msg=f"User '{user.username}' has no permission to use credentials {credentials.name}",
            level=7,
        )

    return permitted


def get_credentials_to_use(job: Job, execution: JobExecution) -> (BaseJobCredentials, None):
    credentials = None

    # todo: write warn log if user tried to execute job using non-permitted credentials (if execution.cred*)
    if execution.user is not None and is_set(execution.credential_user) and \
            execution.credential_user.user.id == execution.user.id:
        credentials = execution.credential_user

    elif is_set(execution.credential_global) and _scheduled_or_has_credentials_access(
        user=execution.user, credentials=execution.credential_global,
    ):
        credentials = execution.credential_global

    elif is_set(job.credentials_default) and _scheduled_or_has_credentials_access(
        user=execution.user, credentials=job.credentials_default,
    ):
        credentials = job.credentials_default

    elif job.credentials_needed and is_set(execution.user):
        # get user credentials that match the job credential-category
        if is_set(job.credentials_category):
            for user_creds in JobUserCredentials.objects.filter(user=execution.user):
                if user_creds.category == job.credentials_category:
                    credentials = user_creds
                    break

        if credentials is None:
            # try to get default user-credentials as a last-resort if the job needs some credentials
            try:
                credentials = JobUserCredentials.objects.filter(user=execution.user).first()

            except ObjectDoesNotExist:
                pass

    if job.credentials_needed and credentials is None:
        config_error(
            'The job is set to require credentials - but none were provided or readable! '
            'Make sure you have privileges for the configured credentials or create user-specific ones.'
        )

    return credentials


def get_runner_credential_args(creds: BaseJobCredentials) -> dict:
    args = {}

    if is_set(creds.ssh_key):
        args['ssh_key'] = creds.ssh_key

    if is_set(creds.connect_pass) or is_set(creds.become_pass) or is_set(creds.vault_pass):
        args['passwords'] = {}

        if is_set(creds.connect_pass):
            args['passwords']['SSH password:'] = creds.connect_pass

        if is_set(creds.become_pass):
            args['passwords']['BECOME password:'] = creds.become_pass

        if is_set(creds.vault_pass):
            args['passwords']['Vault password:'] = creds.vault_pass

    return args
