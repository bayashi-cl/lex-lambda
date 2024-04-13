import aws_cdk as cdk

from .stack import LexLambdaStack


def main() -> int:
    app = cdk.App()
    LexLambdaStack(app, "LexLambdaStack")

    app.synth()
    return 0
