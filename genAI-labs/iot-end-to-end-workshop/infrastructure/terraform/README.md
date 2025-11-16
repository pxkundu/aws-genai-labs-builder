Terraform entrypoint for the AWS IoT end-to-end workshop.

Usage:

1) Copy `terraform.tfvars.example` to `terraform.tfvars` and edit values.
2) `terraform init`
3) `terraform apply -auto-approve`
4) Follow `../../docs/workshop.md` for hands-on steps.

Modules provision IoT Core, streaming, data lake, analytics, events, defender, and monitoring. Optional OpenSearch can be enabled via variables.


