- [x] Build the docker image again (pass the AWS credential as env variables)
```bash
docker run -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
           -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
           -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
           -p 8080:8501\
           --rm -it chatapp
```

- [ ] Create an agent in bedrock - use [sbs assume role script](../sbs-central/assume-sbcp-devopstest-rd.sh)
- [ ] Test the chatapp with this agent
- [ ] Build the docker image again (pass the AWS credential as env variables)
