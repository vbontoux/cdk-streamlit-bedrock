# build it
podman build -t chatapp .
# test it
podman run --rm -it localhost/chatapp