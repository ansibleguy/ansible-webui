from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.urls import path
from django.contrib.auth.decorators import login_required

from aw.utils.http import ui_endpoint_wrapper, ui_endpoint_wrapper_kwargs
from aw.model.job import JobExecution, JobExecutionResultHost
from aw.model.job_credential import JobGlobalCredentials, JobUserCredentials
from aw.api_endpoints.job_util import get_viewable_jobs
from aw.utils.util import get_next_cron_execution_str, is_set
from aw.utils.permission import has_credentials_permission, CHOICE_PERMISSION_READ
from aw.views.forms.job import job_edit, job_clone, job_credentials_edit, job_repository_static_edit, \
    job_repository_git_edit

LIMIT_JOB_RESULTS = 10
LIMIT_JOB_LOG_RESULTS = 50


@login_required
@ui_endpoint_wrapper
def manage(request) -> HttpResponse:
    jobs_viewable = get_viewable_jobs(request.user)
    executions = {}
    next_executions = {}
    execution_results_hosts = {}
    credentials_user = JobUserCredentials.objects.filter(user=request.user)
    credentials_global = [
        creds for creds in JobGlobalCredentials.objects.all()
        if has_credentials_permission(user=request.user, credentials=creds, permission_needed=CHOICE_PERMISSION_READ)
    ]

    for job in jobs_viewable:
        executions[job.id] = JobExecution.objects.filter(job=job).order_by('-updated')[:LIMIT_JOB_RESULTS]

        cron = '-'
        try:
            if is_set(job.schedule):
                cron = get_next_cron_execution_str(job.schedule)

        except ValueError:
            pass

        next_executions[job.id] = cron

        for execution in executions[job.id]:
            if execution.result is not None:
                execution_results_hosts[execution.id] = JobExecutionResultHost.objects.filter(
                    result=execution.result,
                ).order_by('-created')

    return render(
        request, status=200, template_name='jobs/manage.html',
        context={
            'jobs': jobs_viewable, 'executions': executions, 'next_executions': next_executions,
            'show_update_time': True, 'execution_results_hosts': execution_results_hosts,
            'credentials_user': credentials_user, 'credentials_global': credentials_global,
        }
    )


@login_required
@ui_endpoint_wrapper_kwargs
def job_logs(request) -> HttpResponse:
    return render(request, status=200, template_name='jobs/logs.html', context={'show_update_time': True})


@login_required
@ui_endpoint_wrapper_kwargs
def job_credentials(request) -> HttpResponse:
    return render(request, status=200, template_name='jobs/credentials.html', context={'show_update_time': True})


@login_required
@ui_endpoint_wrapper_kwargs
def job_repository(request) -> HttpResponse:
    return render(request, status=200, template_name='jobs/repository.html', context={'show_update_time': True})


urlpatterns_jobs = [
    path('ui/jobs/credentials/<int:credentials_id>', job_credentials_edit),
    path('ui/jobs/credentials', job_credentials),
    path('ui/jobs/log', job_logs),
    path('ui/jobs/manage/job/clone/<int:job_id>', job_clone),
    path('ui/jobs/manage/job/<int:job_id>', job_edit),
    path('ui/jobs/manage/job', job_edit),
    path('ui/jobs/repository/static/<int:repo_id>', job_repository_static_edit),
    path('ui/jobs/repository/git/<int:repo_id>', job_repository_git_edit),
    path('ui/jobs/repository', job_repository),
    path('ui/jobs/manage', manage),
]
