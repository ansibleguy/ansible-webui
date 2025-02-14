#!/usr/bin/env bash

set -e

if [ -z "$1" ]
then
  echo 'YOU NEED TO SUPPLY A VERSION!'
  exit 1
fi

set -u

VERSION="$1"

cd "$(dirname "$0")/../docker"

IMAGE_REPO="ansible0guy/webui"
IMAGE_REPO_UNPRIV="${IMAGE_REPO}-unprivileged"
IMAGE_REPO_AWS="${IMAGE_REPO}-aws"

# todo: allow for multi-platform builds
# RELEASE_ARCHS="linux/arm/v7,linux/arm64/v8,linux/amd64"

image="${IMAGE_REPO}:${VERSION}"
image_latest="${IMAGE_REPO}:latest"

image_unpriv="${IMAGE_REPO_UNPRIV}:${VERSION}"
image_unpriv_latest="${IMAGE_REPO_UNPRIV}:latest"

image_aws="${IMAGE_REPO_AWS}:${VERSION}"
image_aws_latest="${IMAGE_REPO_AWS}:latest"

container="ansible-webui-${VERSION}"

read -r -p "Build version ${VERSION} as latest? [y/N] " -n 1

function cleanup_container() {
  if docker ps -a | grep -q "$container"
  then
    docker stop "$container"
    docker rm "$container"
  fi
}

echo ''
echo "### CLEANUP ###"
cleanup_container

if docker image ls | grep "$IMAGE_REPO" | grep -q "$VERSION"
then
  docker image rm "$image" || true
  docker image rm "$image_unpriv" || true
  docker image rm "$image_aws" || true
fi

if [[ "$REPLY" =~ ^[Yy]$ ]]
then
  if docker image ls | grep "$IMAGE_REPO" | grep -q 'latest'
  then
    docker image rm "$image_latest" || true
    docker image rm "$image_unpriv_latest" || true
    docker image rm "$image_aws_latest" || true
  fi
fi

echo ''
echo "### BUILDING IMAGE ${image} ###"
docker build -f Dockerfile_production -t "$image" --network host --build-arg "AW_VERSION=${VERSION}" --no-cache .

if [[ "$REPLY" =~ ^[Yy]$ ]]
then
  docker build -f Dockerfile_production -t "$image_latest" --network host --build-arg "AW_VERSION=${VERSION}" .
fi

echo ''
echo "### BUILDING IMAGE ${image_unpriv} ###"
docker build -f Dockerfile_production_unprivileged -t "$image_unpriv" --network host --build-arg "AW_VERSION=${VERSION}" --no-cache .

if [[ "$REPLY" =~ ^[Yy]$ ]]
then
  docker build -f Dockerfile_production_unprivileged -t "$image_unpriv_latest" --network host --build-arg "AW_VERSION=${VERSION}" .
fi

echo ''
echo "### BUILDING IMAGE ${image_aws} ###"
docker build -f Dockerfile_production_aws -t "$image_aws" --network host --build-arg "AW_VERSION=${VERSION}" --no-cache --progress=plain .

if [[ "$REPLY" =~ ^[Yy]$ ]]
then
  docker build -f Dockerfile_production_aws -t "$image_aws_latest" --network host --build-arg "AW_VERSION=${VERSION}" .
fi
