variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "cloudsoc"
}

variable "alert_email" {
  description = "Email address for security alerts"
  type        = string
  default     = ""
}
