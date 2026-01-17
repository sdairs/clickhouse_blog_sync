---
title: "Using ClickHouse Cloud and Terraform for CI/CD"
date: "2023-07-13T13:54:20.455Z"
author: "Dale McDiarmid"
category: "Engineering"
excerpt: "Read about how we used the recently released Terraform provider for ClickHouse Cloud to build a CI/CD pipeline for our Go client."
---

# Using ClickHouse Cloud and Terraform for CI/CD

## Introduction

At ClickHouse, we aspire to an API-first approach to development for ClickHouse Cloud. Every action that a user can perform through the user interface should also be possible via a scripting language and thus available for other systems to leverage. This means our recently released Cloud API is also a product with a contract (via swagger) on how it will behave and on which our users can depend. While our existing users much anticipated the release of this API to address requirements such as automated provisioning and de-provisioning, scheduled scaling, and flexible configuration management, it also allowed us to begin integrating with tooling: starting with Terraform.

In this blog post, we explore our new [Terraform provider](https://registry.terraform.io/providers/ClickHouse/clickhouse/latest/docs) and how this can be used to address a common requirement: CI/CD for systems needing to test against a ClickHouse instance. For our example, we look at how we migrated our go client tests away from a monolithic ClickHouse Cloud service to use Terraform and provision ephemeral services for the period of a test only. This not only allows us to reduce costs but also isolates our tests across clients and invocations. We hope others can benefit from this pattern and bring cost savings and simplicity to their test infrastructure!

## Terraform

Terraform is an open-source infrastructure-as-code software tool created by HashiCorp, which allows users to define infrastructure using a declarative configuration language known as HashiCorp Configuration Language (HCL) or, optionally, JSON.

<blockquote style="font-size:16px;">
<p>Infrastructure as code is the process of managing and provisioning computing resources through machine-readable definition files rather than physical hardware configuration or interactive configuration tools. This approach has achieved almost universal acceptance as the means of managing cloud computing resources. Terraform has gained a wide user base and broad adoption as a tool that implements this process declaratively.</p>
</blockquote>

In order to integrate with Terraform and allow users to provision ClickHouse Cloud services, a [provider plugin](https://developer.hashicorp.com/terraform/language/providers) must be implemented and ideally made available via the [Hashicorp registry](https://registry.terraform.io/providers/ClickHouse/clickhouse/latest/docs).

## Authentication

Since the ClickHouse provider relies on the ClickHouse API, an authentication key is required to provision and manage services. Users can create a token, along with a secret, via the ClickHouse Cloud interface. This simple process is shown below:

<a href="/uploads/create_api_key_0f1c1acf18.gif" target="_blank"><img src="/uploads/create_api_key_0f1c1acf18.gif"/></a>

Users should also record their organization id as shown.

## Using the provider

Once a token and secret have been created, users can create a `.tf` file and declare the usage of the provider. Wanting to avoid placing credentials in the main file, the `token_key`, `token_secret` and `organization_id` are replaced with [Terraform variables](https://developer.hashicorp.com/terraform/language/values/variables). These can in turn be specified in a `secret.tfvars` file, which should not be submitted to source control. 

**main.tf**
```yaml
terraform {
 required_providers {
   clickhouse = {
     source = "ClickHouse/clickhouse"
     version = "0.0.2"
   }
 }
}

variable "organization_id" {
  type = string
}

variable "token_key" {
  type = string
}

variable "token_secret" {
  type = string
}

provider clickhouse {
  environment 	= "production"
  organization_id = var.organization_id
  token_key   	= var.token_key
  token_secret	= var.token_secret
}
```

**secret.tfvars**
```yaml
token_key = "<token_key>"
token_secret = "<token_secret>"
organization_id = "<organization_id>"
```

Assuming users have [installed Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli), the provider can be installed with a `terraform init`.

```bash
terraform init

Initializing the backend...

Initializing provider plugins...
- Finding clickhouse/clickhouse versions matching "0.0.2"...
- Installing clickhouse/clickhouse v0.0.2...
- Installed clickhouse/clickhouse v0.0.2 (self-signed, key ID D7089EE5C6A92ED1)

Partner and community providers are signed by their developers.
If you'd like to know more about provider signing, you can read about it here:
https://www.terraform.io/docs/cli/plugins/signing.html

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

Terraform has been successfully initialized!
```

With our provider configured, we can deploy a ClickHouse Cloud service by adding a few lines of HCL to our above file. 

```yaml
variable "service_password" {
  type = string
}

resource "clickhouse_service" "service" {
  name       	= "example-service"
  cloud_provider = "aws"
  region     	= "us-east-2"
  tier       	= "development"
  idle_scaling   = true
  password  = var.service_password
  ip_access = [
	{
    	source  	= "0.0.0.0/0"
    	description = "Anywhere"
	}
  ]
}

output "CLICKHOUSE_HOST" {
  value = clickhouse_service.service.endpoints.0.host
}
```

Here we specify our desired cloud provider, region, and tier. The tier can either be development or production. A development tier represents the entry offering in ClickHouse Cloud, appropriate for smaller workloads and starter projects. For the above example, we enable idling, such that our service doesn’t consume costs if unused. 

<blockquote style="font-size:16px;">
<p>Enabling idle_scaling is the only valid value for development tier instances, i.e., it cannot be disabled. Future versions of the provider will validate this setting.</p>
</blockquote>
We must also specify a service name and list of IP addresses from which this service will be accessible (anywhere in our example), as well as a password for the service. We again abstract this as a variable to our secrets file.

Our output declaration captures the endpoint of our service in a `CLICKHOUSE_HOST` output variable, ensuring obtaining the connection details once the service is ready is simple. The full example main.tf file can be found [here](https://pastila.nl/?025ef1fd/d369943908f299267b8b8d488c230380).

Provisioning this service requires only a single command, `terraform apply`, with the option `-var-file` to pass our secrets.

```bash
terraform apply -var-file=secrets.tfvars

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

# clickhouse_service.service will be created
  + resource "clickhouse_service" "service" {
  	+ cloud_provider = "aws"
  	+ endpoints  	= (known after apply)
  	+ id         	= (known after apply)
  	+ idle_scaling   = true
  	+ ip_access  	= [
      	+ {
          	+ description = "Anywhere"
          	+ source  	= "0.0.0.0/0"
        	},
    	]
  	+ last_updated   = (known after apply)
  	+ name       	= "example-service"
  	+ password   	= (sensitive value)
  	+ region     	= "us-east-2"
  	+ tier       	= "development"
	}

Plan: 1 to add, 0 to change, 0 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

clickhouse_service.service: Creating...
clickhouse_service.service: Still creating... [10s elapsed]
clickhouse_service.service: Still creating... [20s elapsed]
clickhouse_service.service: Still creating... [30s elapsed]
clickhouse_service.service: Still creating... [40s elapsed]
clickhouse_service.service: Still creating... [50s elapsed]
clickhouse_service.service: Still creating... [1m0s elapsed]
clickhouse_service.service: Still creating... [1m10s elapsed]
clickhouse_service.service: Creation complete after 1m12s [id=fd72178b-931e-4571-a0d8-6fb1302cfd4f]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

Outputs:

CLICKHOUSE_HOST = "gx75qb62bi.us-east-2.aws.clickhouse.cloud"
```

As shown, Terraform constructs a plan based on the definition before provisioning the service. The hostname assigned to our service is also printed, thanks to our earlier output configuration. `terraform destroy` can be used to delete the above service.

<blockquote style="font-size: 16px">
<p>In order for Terraform to apply changes to a set of resources, it requires a means of obtaining its current state, including the resources that are provisioned and their configuration. This is described within a "state", which contains a full description of the resources. This allows changes to be made to resources over time, with each command able to determine the appropriate actions to take. In our simple case, we hold this state locally in the folder in which the above command was run. State management, however, is a <a href="https://developer.hashicorp.com/terraform/language/state">far more involved topic</a> with a number of means of maintaining it appropriate for real-world environments, including using <a href="https://developer.hashicorp.com/terraform/language/state/remote">HashiCorp's cloud offering</a>. This is particularly relevant when more than an individual, or system, is expected to operate on the state at any given time and concurrency control is required.</p>
</blockquote>

## CI/CD - a practical example

### Adding Terraform to Github actions

Testing against ClickHouse Cloud is essential to providing high-quality clients to our users. Until the availability of the Terraform provider, our ClickHouse clients were tested against a single service in ClickHouse Cloud with tests orchestrated by [Github actions](https://github.com/features/actions). This instance was shared amongst our clients, each creating their databases and tables whenever a PR or commit was made against the repository. While this was sufficient, it suffered from some limitations:

* **Central point of failure**. Any issues with this service, e.g., due to regional availability, would cause all tests to fail. 
* **Conflicting resources**. While avoided by ensuring all resources, e.g., tables, followed a naming convention using the client name and timestamp, this had consequences (see below).
* **Resource Growth & Test Complexity**. Ensuring tests could be run concurrently meant ensuring tables, databases, and users used by a specific test were unique to avoid conflicts - this needed consistent boilerplate code across clients. When combined with clients needing a [significant number of tests](https://github.com/ClickHouse/clickhouse-go/tree/main/tests) to ensure feature coverage in ClickHouse, this meant the creation of potentially hundreds of tables. Further testing orchestration was needed to ensure each client removed these on completion to avoid table explosion - maybe unsurprisingly, ClickHouse isn’t designed for 10k tables! 
* **Cost inefficiency** - While the query load of the above testing is not substantial, our service was effectively always active and subject to potentially high zookeeper load due to a significant number of concurrent DDL operations. This meant we used a production service. Furthermore, our tests needed to be robust to idling in the event the service was able to shut down.
* **Observability complexity** - With many clients, and multiple tests running, debugging test failures using server logs became more complex.

The Terraform provider promised to provide a simple solution to these problems, with each client simply creating a service at the start of testing, running its test suite, and destroying the service on completion. Our test services thus become ephemeral.

![github_actions_architectures.png](https://clickhouse.com/uploads/github_actions_architectures_80aab4421c.png)

This approach has a number of advantages:

* **Test isolation**- While the tests are still vulnerable to the unavailability of ClickHouse Cloud in a region, they have become robust to service issues, e.g., a client triggering a ClickHouse bug causing a service-wide issue or a client test making a service-wide configuration change. The tests for our clients are immediately isolated.
* **No resource growth and simpler tests** - Our services only exist for the lifetime of the test run. Client developers now only need to consider potential conflicts of resources as a result of their own test concurrency. They can also make configuration changes to entire services, potentially simplifying tests.
* **Cost inefficiency** - Smaller (dev) services can be created and exist for minutes (&lt;10 in most cases) only, minimizing cost.
* **Simple Observability** - While we destroy services on completion of the test, the service id is logged. This can be used to retrieve server logs in our Observability system if needed.

### Existing workflow

For our first client, we selected [Clickhouse Go](https://github.com/ClickHouse/clickhouse-go) with simple Github [actions ](https://github.com/ClickHouse/clickhouse-go/blob/f476287762b28be1de5f7996a775c882c1aa0dd5/.github/workflows/run-tests.yml#L1)and a lot of the test complexity encapsulated in the code’s testing suite.

<blockquote style="font-size: 16px">
<p>Github actions provide a simple workflow-based CI/CD platform. With tight integration into Github, users simply create workflows declaratively in yml files beneath a <code>.github/workflow</code> directory, with each containing jobs to run. These jobs, which consist of steps, can be configured to <a href="https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows">run on schedules or for specific events</a>, e.g., PRs.</p>
</blockquote>

The existing Cloud tests consisted of a job configured to run against the monolithic service described above. The test suite already supported specifying a ClickHouse instance on which tests should be executed via the environment variables `CLICKHOUSE_HOST` and `CLICKHOUSE_PASSWORD`. These are populated through Github secrets. This also requires the environment variable `CLICKHOUSE_USE_DOCKER` to be set to false to disable existing docker-based testing.

Other than these specific changes, the cloud tests are similar to the docker-based single node testing - using a matrix to test the client against different go versions and steps to check out the code and install go prior to the tests being run.

<pre style="font-size: 12px;"><code class="hljs language-yaml"><span class="hljs-attr">integration-tests-cloud:</span>
  <span class="hljs-attr">runs-on:</span> <span class="hljs-string">ubuntu-latest</span>
  <span class="hljs-attr">strategy:</span>
	<span class="hljs-attr">max-parallel:</span> <span class="hljs-number">1</span>
	<span class="hljs-attr">fail-fast:</span> <span class="hljs-literal">true</span>
	<span class="hljs-attr">matrix:</span>
  	<span class="hljs-attr">go:</span>
    	<span class="hljs-bullet">-</span> <span class="hljs-string">"1.19"</span>
    	<span class="hljs-bullet">-</span> <span class="hljs-string">"1.20"</span>
  <span class="hljs-attr">steps:</span>
	<span class="hljs-bullet">-</span> <span class="hljs-attr">uses:</span> <span class="hljs-string">actions/checkout@main</span>

	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Install</span> <span class="hljs-string">Go</span> <span class="hljs-string">${{</span> <span class="hljs-string">matrix.go</span> <span class="hljs-string">}}</span>
  	<span class="hljs-attr">uses:</span> <span class="hljs-string">actions/setup-go@v2.1.5</span>
  	<span class="hljs-attr">with:</span>
    	<span class="hljs-attr">stable:</span> <span class="hljs-literal">false</span>
    	<span class="hljs-attr">go-version:</span> <span class="hljs-string">${{</span> <span class="hljs-string">matrix.go</span> <span class="hljs-string">}}</span>

	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Run</span> <span class="hljs-string">tests</span>
  	<span class="hljs-attr">env:</span>
    	<span class="hljs-attr">CLICKHOUSE_HOST:</span> <span class="hljs-string">${{</span> <span class="hljs-string">secrets.INTEGRATIONS_TEAM_TESTS_CLOUD_HOST</span> <span class="hljs-string">}}</span>
    	<span class="hljs-attr">CLICKHOUSE_PASSWORD:</span> <span class="hljs-string">${{</span> <span class="hljs-string">secrets.INTEGRATIONS_TEAM_TESTS_CLOUD_PASSWORD</span> <span class="hljs-string">}}</span>
    	<span class="hljs-attr">CLICKHOUSE_USE_DOCKER:</span> <span class="hljs-literal">false</span>
    	<span class="hljs-attr">CLICKHOUSE_USE_SSL:</span> <span class="hljs-literal">true</span>
  	<span class="hljs-attr">run:</span> <span class="hljs-string">|
    	CLICKHOUSE_DIAL_TIMEOUT=20 CLICKHOUSE_TEST_TIMEOUT=600s CLICKHOUSE_QUORUM_INSERT=3 make test
</span></code></pre>

### New workflow

Prior to migrating our workflow, we need a simple Terraform resource definition for the Clickhouse service. The following builds on the same example earlier, creating a service in the development tier, but introduces variables for the `organization_id`, `token_key`, `token_secret`, `service_name`, and `service_password`. We also output the service id to assist with later debugging and allow our service to be available from anywhere - the ephemeral nature means the security risk is low. The following `main.tf` file is stored in the [root directory of the `clickhouse-go` client](https://github.com/ClickHouse/clickhouse-go/blob/main/main.tf).

```yaml
terraform {
  required_providers {
	clickhouse = {
  	source = "ClickHouse/clickhouse"
  	version = "0.0.2"
	}
  }
}

variable "organization_id" {
  type = string
}

variable "token_key" {
  type = string
}

variable "token_secret" {
  type = string
}

variable "service_name" {
  type = string
}

variable "service_password" {
  type = string
}

provider clickhouse {
  environment 	= "production"
  organization_id = var.organization_id
  token_key   	= var.token_key
  token_secret	= var.token_secret
}

resource "clickhouse_service" "service" {
  name       	= var.service_name
  cloud_provider = "aws"
  region     	= "us-east-2"
  tier       	= "development"
  idle_scaling   = true
  password  = var.service_password

  ip_access = [
	{
    	source  	= "0.0.0.0/0"
    	description = "Anywhere"
	}
  ]
}

output "CLICKHOUSE_HOST" {
  value = clickhouse_service.service.endpoints.0.host
}

output "SERVICE_ID" {
  value = clickhouse_service.service.id
}
```

Terraform supports specifying variable values through environment variables prefixed with `TF_VAR_`. For example, to populate the organization id, we simply need to set `TF_VAR_organization_id`.

Similar to our previous workflow, the values of these environment variables can be populated with [Github encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets). In our case, we create these at an organizational level so they can be shared across clients and services created in the same ClickHouse Cloud account for simple administration.

![repo_secrets.png](https://clickhouse.com/uploads/repo_secrets_7d10bed607.png)

Note: we don’t have a value here for the service name. As well as not being sensitive, we want to make sure these are unique for the test run, so we can identify the origin and creation time of the service.

To make Terraform available on the runner, we use the [`hashicorp/setup-terraform`](https://github.com/hashicorp/setup-terraform) action. This installs Terraform on the Github actions CLI runner and exposes its CLI so we can make calls like we would from a terminal.

Our final workflow is shown below:

<pre style="font-size: 12px;"><code class="hljs language-yaml"><span class="hljs-attr">integration-tests-cloud:</span>
  <span class="hljs-attr">runs-on:</span> <span class="hljs-string">ubuntu-latest</span>
  <span class="hljs-attr">defaults:</span>
	<span class="hljs-attr">run:</span>
  	<span class="hljs-attr">shell:</span> <span class="hljs-string">bash</span>
  <span class="hljs-attr">strategy:</span>
	<span class="hljs-attr">max-parallel:</span> <span class="hljs-number">1</span>
	<span class="hljs-attr">fail-fast:</span> <span class="hljs-literal">true</span>
	<span class="hljs-attr">matrix:</span>
  	<span class="hljs-attr">go:</span>
    	<span class="hljs-bullet">-</span> <span class="hljs-string">"1.19"</span>
    	<span class="hljs-bullet">-</span> <span class="hljs-string">"1.20"</span>
  <span class="hljs-attr">steps:</span>
	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Check</span> <span class="hljs-string">Out</span> <span class="hljs-string">Code</span>
  	<span class="hljs-attr">uses:</span> <span class="hljs-string">actions/checkout@v3</span>

	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Setup</span> <span class="hljs-string">Terraform</span>
  	<span class="hljs-attr">uses:</span> <span class="hljs-string">hashicorp/setup-terraform@v2.0.3</span>
  	<span class="hljs-attr">with:</span>
    	<span class="hljs-attr">terraform_version:</span> <span class="hljs-number">1.3</span><span class="hljs-number">.4</span>
    	<span class="hljs-attr">terraform_wrapper:</span> <span class="hljs-literal">false</span>

	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Terraform</span> <span class="hljs-string">Init</span>
  	<span class="hljs-attr">id:</span> <span class="hljs-string">init</span>
  	<span class="hljs-attr">run:</span> <span class="hljs-string">terraform</span> <span class="hljs-string">init</span>

	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Terraform</span> <span class="hljs-string">Validate</span>
  	<span class="hljs-attr">id:</span> <span class="hljs-string">validate</span>
  	<span class="hljs-attr">run:</span> <span class="hljs-string">terraform</span> <span class="hljs-string">validate</span> <span class="hljs-string">-no-color</span>

	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Set</span> <span class="hljs-string">Service</span> <span class="hljs-string">Name</span>
  	<span class="hljs-attr">run:</span> <span class="hljs-string">echo</span> <span class="hljs-string">"TF_VAR_service_name=go_client_tests_$(date +'%Y_%m_%d_%H_%M_%S')"</span> <span class="hljs-string">&gt;&gt;</span> <span class="hljs-string">$GITHUB_ENV</span>

	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Terraform</span> <span class="hljs-string">Apply</span>
  	<span class="hljs-attr">id:</span> <span class="hljs-string">apply</span>
  	<span class="hljs-attr">run:</span> <span class="hljs-string">terraform</span> <span class="hljs-string">apply</span> <span class="hljs-string">-no-color</span> <span class="hljs-string">-auto-approve</span>
  	<span class="hljs-attr">env:</span>
    	<span class="hljs-attr">TF_VAR_organization_id:</span> <span class="hljs-string">${{</span> <span class="hljs-string">secrets.INTEGRATIONS_TEAM_TESTS_ORGANIZATION_ID</span> <span class="hljs-string">}}</span>
    	<span class="hljs-attr">TF_VAR_token_key:</span>  <span class="hljs-string">${{</span> <span class="hljs-string">secrets.INTEGRATIONS_TEAM_TESTS_TOKEN_KEY</span> <span class="hljs-string">}}</span>
    	<span class="hljs-attr">TF_VAR_token_secret:</span>  <span class="hljs-string">${{</span> <span class="hljs-string">secrets.INTEGRATIONS_TEAM_TESTS_TOKEN_SECRET</span> <span class="hljs-string">}}</span>
    	<span class="hljs-attr">TF_VAR_service_password:</span> <span class="hljs-string">${{</span> <span class="hljs-string">secrets.INTEGRATIONS_TEAM_TESTS_CLOUD_PASSWORD</span> <span class="hljs-string">}}</span>

	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Set</span> <span class="hljs-string">Host</span>
  	<span class="hljs-attr">run:</span> <span class="hljs-string">echo</span> <span class="hljs-string">"CLICKHOUSE_HOST=$(terraform output -raw CLICKHOUSE_HOST)"</span> <span class="hljs-string">&gt;&gt;</span> <span class="hljs-string">$GITHUB_ENV</span>

	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Service</span> <span class="hljs-string">Id</span>
  	<span class="hljs-attr">run:</span> <span class="hljs-string">terraform</span> <span class="hljs-string">output</span> <span class="hljs-string">-raw</span> <span class="hljs-string">SERVICE_ID</span>

	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Install</span> <span class="hljs-string">Go</span> <span class="hljs-string">${{</span> <span class="hljs-string">matrix.go</span> <span class="hljs-string">}}</span>
  	<span class="hljs-attr">uses:</span> <span class="hljs-string">actions/setup-go@v2.1.5</span>
  	<span class="hljs-attr">with:</span>
    	<span class="hljs-attr">stable:</span> <span class="hljs-literal">false</span>
    	<span class="hljs-attr">go-version:</span> <span class="hljs-string">${{</span> <span class="hljs-string">matrix.go</span> <span class="hljs-string">}}</span>

	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Run</span> <span class="hljs-string">tests</span>
  	<span class="hljs-attr">env:</span>
    	<span class="hljs-attr">CLICKHOUSE_PASSWORD:</span> <span class="hljs-string">${{</span> <span class="hljs-string">secrets.INTEGRATIONS_TEAM_TESTS_CLOUD_PASSWORD</span> <span class="hljs-string">}}</span>
    	<span class="hljs-attr">CLICKHOUSE_USE_DOCKER:</span> <span class="hljs-literal">false</span>
    	<span class="hljs-attr">CLICKHOUSE_USE_SSL:</span> <span class="hljs-literal">true</span>
  	<span class="hljs-attr">run:</span> <span class="hljs-string">|
    	CLICKHOUSE_DIAL_TIMEOUT=20 CLICKHOUSE_TEST_TIMEOUT=600s CLICKHOUSE_QUORUM_INSERT=2 make test
</span>
	<span class="hljs-bullet">-</span> <span class="hljs-attr">name:</span> <span class="hljs-string">Cleanup</span>
  	<span class="hljs-attr">if:</span> <span class="hljs-string">always()</span>
  	<span class="hljs-attr">run:</span> <span class="hljs-string">terraform</span> <span class="hljs-string">destroy</span> <span class="hljs-string">-no-color</span> <span class="hljs-string">-auto-approve</span>
  	<span class="hljs-attr">env:</span>
    	<span class="hljs-attr">TF_VAR_organization_id:</span> <span class="hljs-string">${{</span> <span class="hljs-string">secrets.INTEGRATIONS_TEAM_TESTS_ORGANIZATION_ID</span> <span class="hljs-string">}}</span>
    	<span class="hljs-attr">TF_VAR_token_key:</span>  <span class="hljs-string">${{</span> <span class="hljs-string">secrets.INTEGRATIONS_TEAM_TESTS_TOKEN_KEY</span> <span class="hljs-string">}}</span>
    	<span class="hljs-attr">TF_VAR_token_secret:</span>  <span class="hljs-string">${{</span> <span class="hljs-string">secrets.INTEGRATIONS_TEAM_TESTS_TOKEN_SECRET</span> <span class="hljs-string">}}</span>
    	<span class="hljs-attr">TF_VAR_service_password:</span> <span class="hljs-string">${{</span> <span class="hljs-string">secrets.INTEGRATIONS_TEAM_TESTS_CLOUD_PASSWORD</span> <span class="hljs-string">}}</span>
</code></pre>

In summary, this workflow consists of the following steps:

1. Checks out existing code to the runner via `uses: actions/checkout@v3`.
2. Installs terraform on the runner via `uses: hashicorp/setup-terraform@v2.0.3`.
3. Invokes `terraform init` to install the ClickHouse provider.
4. Validates the terraform resource definition file in the root of the checked-out code via the`terraform validate` command.
5. Sets the environment variable `TF_VAR_service_name` to a date string prefixed with `go_client_tests_`. This ensures our services have unique names across clients and test runs and assists with debugging.
6. Run `terraform apply` to create a Cloud service with a specified password, with the organization id, token, and key passed via environment variables.
7. Sets the CLICKHOUSE_HOST environment variable to the value of the output from the previous apply step.
8. Captures the service id for debugging purposes.
9. Installs go based on the current matrix version.
10. Run the tests - note the `CLICKHOUSE_HOST` has been set above. An astute reader will notice we pass environment variables to `make test` like our earlier workflow, to increase timeouts. However, we lower `CLICKHOUSE_QUORUM_INSERT` to `2`. This is required as some tests need data to be present on all nodes prior to querying. While our previous monolithic service had three nodes, our smaller development service has only two.
11. Destroys the service irrespective of the success (`if: always()`) of the workflow via the `terraform destroy` command.

These changes are now live! Whenever a PR or commit is issued to the repository, changes will be tested against an ephemeral ClickHouse Cloud cluster!

![git_actions.png](https://clickhouse.com/uploads/git_actions_a428225503.png)

<blockquote style="font-size:16px">
<p>Currently, these tests do not run for PRs raised from forks and only branches (this requires members of the ClickHouse organization). This is a <a href="https://securitylab.github.com/research/github-actions-preventing-pwn-requests/">standard Github policy</a> for pull_request events, as it potentially allows secrets to be leaked. We plan to address this with future enhancements.</p>
</blockquote>

## Conclusion

In this blog post, we have used the new Terraform provider for ClickHouse Cloud to build a CI/CD workflow in Github actions which provisions ephemeral clusters for testing. We use this approach to reduce the cost and complexity of our client testing with ClickHouse Cloud.

