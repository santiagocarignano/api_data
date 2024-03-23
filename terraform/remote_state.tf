terraform {
  backend "gcs" {
    bucket = "api-data-terraform-state"
    prefix    = "vpc/terraform.tfstate"
  }
}