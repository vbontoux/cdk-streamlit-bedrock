from aws_cdk import (
    SecretValue,
    CfnOutput
)
from constructs import Construct
import aws_cdk as cdk

class SecretManagerStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, properties, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        secret_value_parameter = cdk.CfnParameter(self, "gittoken", type="String", description="The value of the git token.")

        secret = cdk.aws_secretsmanager.Secret(self, "GitTokenSecret",
            secret_string_value=SecretValue.unsafe_plain_text(secret_value_parameter.value_as_string),
            description="This is my Git secret"
        )
        properties["GitSecret"] = secret

        # Output the secret ARN
        CfnOutput(self, "GitTokenSecretArn",
            value=secret.secret_arn,
            description="The ARN of the git token secret"
        )
        CfnOutput(self, "GitTokenSecretName",
            value=secret.secret_name,
            description="The Name of the git token secret"
        )
