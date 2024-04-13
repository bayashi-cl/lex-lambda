from aws_cdk import BundlingOptions, DockerImage, RemovalPolicy, Stack, aws_lambda, aws_logs
from constructs import Construct


class RyeLambdaCdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)
        runtime = aws_lambda.Runtime.PYTHON_3_12

        # 1. deps as layer
        layer = aws_lambda.LayerVersion(
            self,
            "App1Layer",
            code=aws_lambda.Code.from_asset(
                ".",
                bundling=BundlingOptions(
                    image=DockerImage.from_build(
                        ".",
                        build_args={"IMAGE": runtime.bundling_image.image},
                        file="docker/lambda.Dockerfile",
                    ),
                    command=[
                        "bash",
                        "-eux",
                        "-c",
                        "\n".join(
                            [
                                r"pip wheel --wheel-dir /tmp/wheelhouse --no-deps --requirement <(grep -E '^\-e' requirements.lock | sed 's/-e //g')",
                                "cd /tmp",
                                "uv pip compile --find-links /tmp/wheelhouse --constraint /asset-input/requirements.lock /asset-input/app/lambda-app/pyproject.toml --output-file /tmp/requirements.txt",
                                "pip install --find-links /tmp/wheelhouse --no-index --prefix /asset-output/python --requirement /tmp/requirements.txt",
                            ]
                        ),
                    ],
                    user="root",
                ),
            ),
        )

        app1 = aws_lambda.Function(
            self,
            "App1Function",
            code=aws_lambda.Code.from_asset(
                ".",
                bundling=BundlingOptions(
                    image=runtime.bundling_image,
                    command=[
                        "bash",
                        "-eux",
                        "-c",
                        "pip install --target /asset-output --no-deps app/lambda-app",
                    ],
                    user="root",
                ),
            ),
            handler="lambda_app.handler",
            runtime=runtime,
            layers=[layer],
        )
        aws_logs.LogGroup(
            self,
            "App1LogGroup",
            log_group_name=f"/aws/lambda/{app1.function_name}",
            removal_policy=RemovalPolicy.DESTROY,
        )

        # 2. deps with function
        app2 = aws_lambda.Function(
            self,
            "App2Function",
            code=aws_lambda.Code.from_asset(
                ".",
                bundling=BundlingOptions(
                    image=DockerImage.from_build(
                        ".",
                        build_args={"IMAGE": runtime.bundling_image.image},
                        file="docker/lambda.Dockerfile",
                    ),
                    command=[
                        "bash",
                        "-eux",
                        "-c",
                        "\n".join(
                            [
                                r"pip wheel --wheel-dir /tmp/wheelhouse --no-deps --requirement <(grep -E '^\-e' requirements.lock | sed 's/-e //g')",
                                r"pip install --find-links /tmp/wheelhouse --no-index --no-warn-conflicts --target /asset-output lambda-app",
                            ]
                        ),
                    ],
                    user="root",
                ),
            ),
            handler="lambda_app.handler",
            runtime=runtime,
            layers=[],
        )
        aws_logs.LogGroup(
            self,
            "App2LogGroup",
            log_group_name=f"/aws/lambda/{app2.function_name}",
            removal_policy=RemovalPolicy.DESTROY,
        )
