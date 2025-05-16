# https://github.com/abiosoft/colima
# > brew install colima
# > colima start

# build it
docker build -t chatapp .
# test it
docker run -p 8080:8501 --rm -it localhost/chatapp