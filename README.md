# Thebacknd

Thebacknd is a proof-of-concept to run a NixOS system as an ephemeral
DigitalOcean virtual machine in a single command:

```
$ thebacknd run -A toplevels.example
```

This builds, signs, and pushes to a binary cache the Nix attribute
`toplevels.example` defined in the `default.nix` file present in the current
working directory. It then creates a DigitalOcean virtual machine, and switches
its base NixOs system to the given toplevel.

# Variants

```
$ thebacknd run /nix/store/qqzn1jfjgxipzz4g4qqvv5cilk0x0hy7-nixos-system-unnamed-23.05pre-git
$ thebacknd run /nix/store/r7cylmrxj0nj2901vy33wqnfdflaf7fb-program-0.1.0/bin/program
$ thebacknd run
$ thebacknd run --A toplevels.base
$ thebacknd run --attr toplevels.example
$ thebacknd run default.nix --attr toplevels.nginx
```

The first call doesn't build or sign anything. It only takes a Nix store path
that is expected to be existing (and signed) in the binary cache, and uses it
as the desired system.

It can also be given a path to a binary within the Nix store. Again, this uses
the base image, and it runs the binary once the machine has booted.

It can also be run without an argument. The resulting virtual machine uses the
base image without switching to a new toplevel. This is similar to `thebacknd
run -A toplevels.base`, except it picks a pre-made base image from DigitalOcean
custom images, instead of building it.

In the future, I'd like to experiment with loading a Nix shell, or to build a
toplevel from a Git repository. In that case, building it could be done either
locally or within the VM. When it's built within the VM, a Nix binary cache
becomes optional.

# Components

Thebacknd stitches together a few pieces:

- A set of "serverless" "functions" for creating ephemeral virtual machines
  within DigitalOcean. This acts as a service that can talk to the DigitalOcean
  API. This is the only place where a DigitalOcean API token is required. Such a
  token can act on all your DigitalOcean infrastructure and thus is quite
  sensitive. DigitalOcean is in the process of adding finer-grained access rights
  to tokens, so seggregating such a token in its own specialized service might be
  less necessary in the future.

  This could easily be replaced by a small virtual machine. One advantage the
  "serverless" "functions" have is that they can "scale to zero" (they don't
  incur any costs when they are unused), while still being ready to accept
  calls.

  Another advantage "functions" have is that they can also be scheduled, which
  is not possible with standard virtual machine creation.

  In particular, one such function is scheduled to destroy virtual machines
  regularly (currently after 1 hour).

- A custom base image. This is a fairly standard NixOS image with one
  difference: it reads some data to know to which toplevel it should switch to,
  and switches to it at startup.

- An S3-compatible Nix binary cache. The custom image fetches the toplevel from
  the cache instead of building it.

Note: Importing the base image to DigitalOcean must be done before it is
possible to create a virtual machine that uses it. The import is done from a
URL, so the image is first uploaded to an S3-compatbile bucket (this could be
done elsewhere, or re-use the binary cache and make that specific path public).

Note: In our example scripts, we use a different set of credentials to push to
the binary cache after building the toplevel, than to pull from it within the
virtual machines.

Note: The current proof-of-concept passes the read-only credentials to the
virtual machine using the cloud-init user-data mechanism. This is easily
readable by any code running in the virtual machine, so a better mechanism
should be used. Unfortunately this would involve adding another state to the
service.

# Usage

The basic usage of the "serverless" "functions" looks like this (assuming you
already have `doctl` with "serverless" support):

```
$ doctl serverless deploy .
$ doctl serverless functions invoke thebacknd/list
$ doctl serverless functions invoke thebacknd/create
$ doctl serverless functions invoke thebacknd/destroy-all
$ doctl serverless functions invoke thebacknd/destroy-old
$ doctl serverless functions list
```

There is also a `thebacknd/destroy-self` that is intended to be called by a
virtual machine to destroy itself.

Virtual machines are named `thebacknd-xxx`, where `xxx` is a number. The
numbers are reused when virtual machines are destroyed. The virtual machines
are also tagged with "thebacknd". The `list` and `destroy-all` operations only
work on those machines.

The notion of "old" machines is currently set to 60 minutes. The current
hard-coded machine type costs less than $0.01 for one hour.

`destroy-old` is scheduled every 20 minutes. This is about 2200 activations per
month. Scheduled triggers are a free feature of DigitalOcean during the beta
period, but this may change afterwards.

It can take less than 300ms to run, but will sometimes reach its 3000ms
timeout. Maybe it would be wise to increase it a bit.

# Configuration

They're is two parts to the configuration: the part that mimics the described
components above, involving access rights so those components can communicate
together, and the part where you decide what you want to run (e.g. the Nix
store path to the toplevel, or the virtual machine size).

The `.env` file contains an API token for the `pydo` client library. It is not
versioned and looks like:

```
$ cat .env
# Access to the DigitalOcean API.
DIGITALOCEAN_ACCESS_TOKEN=

# Secret to generate/verify self destruction codes for VMs.
THEBACKND_SECRET=

# S3 credentials to read from a private binary cache.
NIX_CACHE_KEY_ID=
NIX_CACHE_KEY_SECRET=

# The corresponding Nix binary cache to download the toplevel from.
NIX_CACHE=

# Public key to verify Nix store paths from the above cache.
NIX_TRUSTED_KEY=
```

Its values are templated into the `project.yml` file during the build and
deployment of the serverless functions.

# Development

Writing Python code locally to run it as serverless functions is a very bad
development experience. I'm trying to wrap those functions in a normal Python
project to more easily develop it locally. It means in practice that we have to
both accomodate the structure required by the `doctl serverless` tool, and what
`poetry` wants.

To list what is deployed (this can show for instance that we failed to include
the right files):

```
$ unzip -l packages/thebacknd/create/__deployer__.zip
```

Note: this might also show unwanted files, e.g.
`thebacknd/__pycache__/__init__.cpython-310.pyc`. This is why we have to be
carefull to clean our workspace before deploying.

Note: the build system supports `.include` files. When using them, you can't
use `.ignore` files. If we want to include our library, we have to use
`../../../lib/thebackend`. Unfortunately this will pick up
`../../../lib/thebacknd/__pycache__` if it exists, and we can't use
`../../../lib/thebacknd/__init__.py` to be more explicit because then it drops
the leading `thebacknd/` path.

To run the same Python code that is used in the serverless functions locally:

```
$ poetry install
$ poetry run thebacknd --help
$ poetry run thebacknd list
$ poetry run thebacknd create
$ poetry run thebacknd destroy-all
```

# Virtual machine

Within a virtual machine deployed using thebacknd base image, there are four
helper scripts:

```
# current-system
# desired-system
# destroy-system
# update-system
```

Those will be replaced by symlinks to `thewithn`.

# Local binary

The `scripts/thebacknd-run.sh` script tries to provide a user-friendly way to
spin a VM. Some code living in `src/` is supposed to replace it in the future.

```
$ nix-shell -p cargo
$ cargo run --bin thebacknd
$ cargo doc
```

Note: the documentation is built at `target/doc/thebacknd/index.html`.
