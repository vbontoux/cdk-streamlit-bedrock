#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_chat.cdk_secret_manager import SecretManagerStack
from cdk_chat.cdk_container_pipeline import EcrPipelineStack

properties = { "stack": "cdk-batch-"}

app = cdk.App()

SecretManagerStack(app, "SecretManagerStack", properties)

EcrPipelineStack(app, "EcrPipelineStack", properties)

# EcsStack(app, "EcsStack", properties)

app.synth()

