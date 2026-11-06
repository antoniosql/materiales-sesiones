# tflint: errores y malas prácticas de Terraform que 'terraform validate' no detecta.
config {
  call_module_type = "local"
}

plugin "terraform" {
  enabled = true
  preset  = "all"
}
