
locals {
  files = {
    file0 = 0
    file2 = 2
    file3 = 3
    file4 = 4
  }
}

resource "local_file" "foo" {
  for_each = local.files

  content  = "# Some content for file ${each.value}"
  filename = "${each.key}.txt"
}
