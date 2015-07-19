# A command line interface for common [Go Continuous Delivery][gocd] maintenance tasks

For work I and colleagues have for the last nine months been writing a lot of different small shell scripts with curl that interacts with the Go api.
 
Most of them are quick works but they aren't very robust, and we keep repeating the same work and discovery every time we need to do it.

The goal of this project is to make these and similar tasks super simple to do and repeatable without having to write a so-so reliable bash script.

## Usage

This is something I'm writing down before even starting to code, so until this line is gone this is just an idea of how I imagine a good interaction would be like.

```shell
$ gocd pipeline unlock <name>
$ gocd pipeline pause <name>
$ gocd pipeline unpause <name>
$ gocd pipeline trigger <name> [--fingerprint=<git sha>] [--upstream=new/upstream]
$ gocd pipeline status <name> [--json]
Pipeline <name> status:
  locked: false
  paused: true
  schedulable: false
$ gocd pipeline history <name>
{ … json document … }
$ gocd pipeline retrigger-failed <name> [--counter default last] [--stage only retrigger if this stage failed] [--retrigger stage|pipeline, default pipeline] 

```

## Writing your own commands

The way the cli searches for commands is quite straightforward:

* The first argument is the package the command belongs to
* The second argument is the class to call
* Any unnamed parameters are passed in the same order as on the cli
* Any --parameters gets the dashes stripped and sent as keyword arguments

To make it work this way there's a pattern to keep to.
For each package the `__init__.py` file will have to provide all the 
subcommands in the `__all__` variable. Each command is a class and it's 
the name of those classes that are in the `__all__` variable.

The subcommands will on the command line be divided by dashes, meaning that  
`RetriggerFailed` will become `retrigger-failed` on the command line.

```bash
$ gocd <command> <subcommand> posarg1 --kwarg1
# or how it's referred to in code
$ gocd <package> <command class> posarg1 --kwarg1
# or when used
$ gocd pipeline retrigger-failed Simple-with-lock --stage=firstStage --retrigger=stage
```

Calling help for a command or subcommand will list all available commands, 
for more information about each command ask for help on each in turn.


[gocd]: http://go.cd/
