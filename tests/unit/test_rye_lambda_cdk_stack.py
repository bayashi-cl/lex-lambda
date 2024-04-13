import aws_cdk as core
import aws_cdk.assertions as assertions

from rye_lambda_cdk.rye_lambda_cdk_stack import RyeLambdaCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in rye_lambda_cdk/rye_lambda_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RyeLambdaCdkStack(app, "rye-lambda-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
