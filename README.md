# Thebacknd

Thebacknd is a set of "serverless" "functions" for creating ephemeral virtual
machines within DigitalOcean.

Using "functions" makes it possible to scale to zero: we gain the ability to
create virtual machines without having to rely on an always-on bastion machine.
It also centralizes the place where we have code that can act on the
DigitalOcean infrastructure (rather than running such powerful code on an
existing production machine).

"Functions" can also be scheduled, which is not possible with standard virtual
machine creation.

Because the virtual machines created are handled by thebacknd, they are also
destroyed even if we forget about them.

# Usage

The basic usage looks like this (assuming you already have `doctl` with
"serverless" support):

```
$ doctl serverless deploy .
$ doctl serverless functions invoke thebacknd/list
$ doctl serverless functions invoke thebacknd/create
$ doctl serverless functions invoke thebacknd/destroy-all
```

Virtual machines are named `thebacknd-xxx`, where `xxx` is a number. The
numbers are reused when virtual machines are destroyed. The virtual machines
are also tagged with "thebacknd". The `list` and `destroy-all` operations only
work on those machines.

# Configuration

The `.env` file contains an API token for the `pydo` client library. It is not
versioned and looks like:

```
$ cat .env
DIGITALOCEAN_ACCESS_TOKEN=xxxx
```

Its values are templated into the `project.yml` file during the build.
