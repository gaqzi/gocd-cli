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
$ gocd pipeline trigger <name> [fingerprint=<git sha>] [upstream=new/upstream]
$ gocd pipeline status <name> [--json]
Pipeline <name> status:
  locked: false
  paused: true
  schedulable: false
$ gocd pipeline history <name>
{ … json document … }
$ gocd pipeline retrigger-failed <name> [--counter default last] [--stage only retrigger if this stage failed] [--retrigger stage|pipeline, default pipeline] 

```


[gocd]: http://go.cd/
