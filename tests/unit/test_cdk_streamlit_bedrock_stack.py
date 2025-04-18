import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_chat.cdk_streamlit_chat_stack import CdkStreamlitBedrockStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_streamlit_bedrock/cdk_streamlit_bedrock_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkStreamlitBedrockStack(app, "cdk-streamlit-bedrock")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
