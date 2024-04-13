import aws_cdk as cdk

from rye_lambda_cdk import RyeLambdaCdkStack

app = cdk.App()
RyeLambdaCdkStack(app, "RyeLambdaCdkStack")

app.synth()
