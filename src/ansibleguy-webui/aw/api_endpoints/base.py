from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils.html import escape as escape_html
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import BaseHasAPIKey
from drf_spectacular.utils import OpenApiResponse

from aw.model.api import AwAPIKey
from aw.base import USERS, GROUPS
from aw.utils.util import is_set


class HasAwAPIKey(BaseHasAPIKey):
    model = AwAPIKey


API_PERMISSION = [IsAuthenticated | HasAwAPIKey]


# see: rest_framework_api_key.permissions.BaseHasAPIKey:get_from_header
def get_api_user(request) -> USERS:
    if isinstance(request.user, AnonymousUser):
        try:
            return AwAPIKey.objects.get_from_key(
                request.META.get(getattr(settings, 'API_KEY_CUSTOM_HEADER'))
            ).user

        except ObjectDoesNotExist:
            # invalid api key
            pass

    return request.user


class BaseResponse(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class GenericResponse(BaseResponse):
    msg = serializers.CharField()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GROUPS


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = USERS


class LogDownloadResponse(BaseResponse):
    binary = serializers.CharField()


def api_docs_put(item: str) -> dict:
    return {
        200: OpenApiResponse(response=GenericResponse, description=f'{item} updated'),
        400: OpenApiResponse(response=GenericResponse, description=f'Invalid {item} data provided'),
        403: OpenApiResponse(response=GenericResponse, description=f'Not privileged to edit the {item}'),
        404: OpenApiResponse(response=GenericResponse, description=f'{item} does not exist'),
    }


def api_docs_delete(item: str) -> dict:
    return {
        200: OpenApiResponse(response=GenericResponse, description=f'{item} deleted'),
        400: OpenApiResponse(response=GenericResponse, description=f'Invalid {item} data provided'),
        403: OpenApiResponse(response=GenericResponse, description=f'Not privileged to delete the {item}'),
        404: OpenApiResponse(response=GenericResponse, description=f'{item} does not exist'),
    }


def api_docs_post(item: str) -> dict:
    return {
        200: OpenApiResponse(response=GenericResponse, description=f'{item} created'),
        400: OpenApiResponse(response=GenericResponse, description=f'Invalid {item} data provided'),
        403: OpenApiResponse(response=GenericResponse, description=f'Not privileged to create {item}'),
    }


def not_implemented(*args, **kwargs):
    del args, kwargs
    return JsonResponse({'error': 'Not yet implemented'}, status=404)


def validate_no_xss(value: str, field: str, shell_cmd: bool = False, single_quote: bool = False):
    if is_set(value) and isinstance(value, str):
        # ignore characters shell-commands may need
        if single_quote or shell_cmd:
            value = value.replace("'", '')

        if shell_cmd:
            value = value.replace('&', '')

        if value != escape_html(value):
            raise ValidationError(f"Found illegal characters in field '{field}'")
