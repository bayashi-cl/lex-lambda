# rye-lambda-cdk

## start
```sh
cdk init app --language python
rm -rf .venv
rye init --script
rye add aws-cdk-lib

rye init --lib app/lambda-app
```
