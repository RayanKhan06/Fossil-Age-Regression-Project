# Deploying to AWS

This provisions: an ECR repository (holds your Docker image), an ECS Fargate
service (runs the container, no servers to manage), and an Application Load
Balancer (gives you a public URL).

## One-time setup
Make sure you've already done, from earlier steps:
- `aws configure` (with a working IAM user, verified via `aws sts get-caller-identity`)
- Terraform installed (verified via `terraform -version`)

## Phase 1: create the image registry only

From the `terraform/` folder:

    cd terraform
    terraform init
    terraform apply -target=aws_ecr_repository.app

Type `yes` when prompted. This creates ONLY the ECR repository — nothing
else yet — because ECS needs a real image to exist before it can start a
task, and we haven't pushed one yet.

## Phase 2: build and push your image to ECR

Get the repository URL Terraform just created:

    terraform output ecr_repository_url

Then, from your project root (one level up, where the Dockerfile is):

    cd ..
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

    docker build -t fossil-age-api .
    docker tag fossil-age-api:latest <ECR_REPOSITORY_URL>:latest
    docker push <ECR_REPOSITORY_URL>:latest

Replace `<ACCOUNT_ID>` and `<ECR_REPOSITORY_URL>` with the real values from
the `terraform output` above (the repo URL already contains your account ID
and region, so you can copy-paste most of this from it directly).

## Phase 3: create everything else (ALB, ECS cluster/service)

    cd terraform
    terraform apply

Type `yes` when prompted. This takes a few minutes — Fargate needs to pull
the image, start the container, and the ALB needs to mark it healthy.

## Get your public URL

    terraform output load_balancer_url

Open that URL + `/health` and `/docs` in your browser, same checks as
locally — except now it's a real public address anyone can hit.

## IMPORTANT: tear it down when you're not actively using it

This costs a small amount per hour while running (Fargate + ALB). When
you're done demoing it for now:

    terraform destroy

Type `yes` to confirm. This deletes everything Terraform created. Re-running
`terraform apply` later brings it all back (you'll need to redo Phase 2's
image push only if the ECR repo itself was also destroyed — if you skip
`-target` on destroy it deletes ECR too, so you'd re-push the image next time).
