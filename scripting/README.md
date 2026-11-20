Terraform Plan Validator



`script.py` validates Terraform plan JSON files to identify potentially unsafe infrastructure changes.



The validator allows:

\- Resource creation.

\- Resource modification only when the changes are limited to the `tags.GitCommitHash` value.



It rejects other modifications and resource deletions.



Requirements



\- Python 3

\- Terraform plan files converted to JSON using `terraform show -json`


Usage



From the `scripting` directory, run:



```bash

python script.py tfplan-1.json tfplan-2.json tfplan-3.json

```



The script accepts one or more Terraform plan JSON filenames as command-line arguments.





\- `PROCEED`: The plan contains only permitted changes.

\- `DO NOT PROCEED`: The plan contains changes that violate the validation rules. Review and revert the reported changes before generating a new plan.





The supplied test files produce the following results:



| tfplan-1.json | PROCEED |

| tfplan-2.json | PROCEED |

| tfplan-3.json | DO NOT PROCEED |



The validator reports the resource and the specific changes responsible for rejecting a plan.

