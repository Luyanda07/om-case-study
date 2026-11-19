# Add steps/actions here:

The original Terraform configuration used count to manage five local_file resources (file0.txt to file4.txt).

The requirement was to remove the second resource (file1.txt) without affecting the other four resources.


1. step 1


 Back up the Terraform state

Created a backup of the current state before making changes:

terraform state pull > terraform.tfstate.before-migration



2. step 2

 Replace count with for_each

Updated main.tf to use a map with stable keys:

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

This allows individual resources to be identified by stable keys instead of numerical indexes.


3.

Used terraform state mv to associate the four existing resources with their new addresses:

terraform state mv 'local_file.foo[0]' 'local_file.foo["file0"]'
terraform state mv 'local_file.foo[2]' 'local_file.foo["file2"]'
terraform state mv 'local_file.foo[3]' 'local_file.foo["file3"]'
terraform state mv 'local_file.foo[4]' 'local_file.foo["file4"]'

Index 1 was intentionally excluded because it represented file1.txt, the resource to be removed.


4. 

Ran:

terraform plan

The plan showed:

Plan: 0 to add, 0 to change, 1 to destroy.

Only local_file.foo[1] (file1.txt) was scheduled for destruction.

Applied the change using:

terraform apply

5. 

Confirmed that Terraform tracked only the four retained resources:

terraform state list

Confirmed that only the four expected files remained:

ls -l file*.txt

Finally, ran:

terraform plan

Terraform returned:

No changes. Your infrastructure matches the configuration.

removed file1.txt while preserving file0.txt, file2.txt, file3.txt and file4.txt.

All four retained resources remained tracked by Terraform, and the final plan reported no further changes.