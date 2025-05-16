# https://github.com/abiosoft/colima
# > brew install colima
# > colima start

# build it
docker build -t chatapp .

# test it
docker run -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
           -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
           -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
           -p 8080:8501\
           --rm -it chatapp
