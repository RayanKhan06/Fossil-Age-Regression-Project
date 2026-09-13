output "load_balancer_url" {
  description = "Public URL for the API"
  value       = "http://${aws_lb.app.dns_name}"
}

output "ecr_repository_url" {
  description = "Where to push your Docker image"
  value       = aws_ecr_repository.app.repository_url
}
