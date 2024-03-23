provider "google" {
  credentials = file("../service_account.json")
  project     = "fourth-ability-324823"
  region      = "us-east1"
}
