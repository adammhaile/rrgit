# rrgit

`rrgit` is a command line utility to aid in the process of editing RepRapFirmware / Duet controller configuration files over a network connection. It is designed to be as git-like as possible in order to provide a familiar interface. Of course, however, the RepRapFirmware interface is far less extensive compared to git, so `rrgit` handles just the basics. It will allow you to clone, pull, push, and diff between the controller and local copies of the files.

## Installation

The simplest way to install is:

`pip install rrgit`

Alternatively:

```
git clone https://github.com/adammhaile/rrgit.git
cd rrgit
python setup.py install
```

This will install the necessary packages and make available the `rrgit` and `rrg` (simply an alias) commands.

## Usage

The following base commands are available. With the exception of `clone` all commands must be called from the root of the `rrgit` cloned directory.

### Clone

`rrgit clone HOSTNAME [DIRECTORY]`

Clone the config from `HOSTNAME` to `DIRECTORY`

The intent is to use `rrgit` much like you would `git` by starting from an existing set of configuration files, already on a remote machine. 

`HOSTNAME` can be an IP address or local network hostname and can include http/https but it is not required. The base network address is the important item here.

`DIRECTORY` is optional if you simply want to clone down to the current working directy. Note that this is only an option if the current directory is completely empty. Otherwise provide an absolute or relative directory path. That directory need not exist as it will be created.

One cloned, the directory specified will be populated with all non-ignored (see more below on `.rrgitignore`) files from the specified remote machine.

Note that RepRapFirmware has very specific directories (such as `sys`, `gcodes`, and `macros`) that it uses. Anything other than the official directory names (which are pulled from the remote system at connection time) will be ignored. Therefore you could add any other files or directories into your `rrgit` directory and they will be ignored by `rrgit`.

### Status

`rrgit status`

Query both the remote machine and the local directory to automatically discover and report on any differences between the two. Note that, unlike `git`, this is only able to detect if files have a different timestamp or are a different size. The report will be broken down into the following categories:

- Remote only: files that only exist on remote
- Remote newer: files that are newer on remote than local
- Local only: files that only exist on local
- Local newer: files that are newer on local than remote
- Different size: files that have the same timestamp but differ in size. This is extremely unlikely. Typically all change detection is timestamp based.

### Pull

`rrgit pull [--force/-f] [--yes/-y] [file_patterns ...]`

Pulls remote files to local. Must be run from the root of the `rrgit` clone directory. With no options specified, it will only pull remote files that differ from local. Note that since there is no concept of history or commits as with actual git, this acts a little different. If you have made changes on both remote and local and then choose to pull, it will overwrite local with remote. There is no automatic conflict resolution.

However, it will ask you to confirm the overwrite if the local files are newer than remote or if they only exist on local (in which case they would be deleted locally). You can use the `--yes` option to suppress this confirmation request.

Using the `--force` option is effectively like re-cloning the configuration files. It will pull down all remote files to local, regardless of local state. This includes deletions locally.

Finally, you can optionally provide any number of relative file paths or [git pathspec](https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddefpathspecapathspec) style file patterns. It will then only act upon files that match those patterns.

Be aware that on Linux or Mac systems bash will provide file path expansion on any wildcard file patterns provided. This is fine when acting upon local files but with pull, the pattern matching is purely for remote files. If you let bash do the path expansion for you it will *only* match files that are also local. To get around this, it is recommended to wrap all file patterns in single quotes like this:

`rrgit pull 'sys/*.g'`

Which would pull all `.g` files from the `sys` directory on the remote system.

There is no need to use the single quote wrapping on Windows systems as `rrgit` will always handle wildcard file patterns internally.

### Push

`rrgit push [--force/-f] [--yes/-y] [file_patterns ...]`

The `push` command functions identically to the `pull` command, just in the other direction, local to remote.


### Diff

`rrgit diff [file_patterns ...]`

Show a diff report of all files that do not match between remote and local, if called with no file patterns. It will, by default, diff any files that would be shown in the `status` command report.

If file patterns are provided (which follow the same rules as described in the `pull` command) it will only show diffs for those files specified.

It will always show the diff output in a format with remote as file A and local as file B.

### Watch

`rrgit watch`

Watch the local `rrgit` directory tree and automatically push all changes to the remote machine. This is useful if you will be making many changes and runnings tests after each. Instead of running the `push` command each time the files will be pushed as soon as they are saved locally.

## `.rrgitignore` file

`rrgit` will automatically create a file called `.rrgitignore` in the root of the cloned directory which can be used to filter out what is pulled and pushed. The format is identical to the [`.gitignore` file format](https://git-scm.com/docs/gitignore).

By default this file includes the following lines:

```
/www/
/gcodes/
/scans/
/menu/
*.uf2
*.bin
```

- `www` is the location of the DuetWebControl files and are unlikely that you will ever need to pull/push changes to those files.
- `gcodes` is the location of uploaded job files. These files can be quite large.
- `scans` is used for depth probe scanning in RepRapFirmware which is infrequently used.
- `menu` provides configuration files for older-style monochrome LCD displays.
- `*.uf2` and `*.bin` files are the binary firmware files for your controller and are often large files which really don't need to be synced in most cases.

These are simply defaults which make the initial clone fast and likely to include everything most people will want. If you would like these files, simple edit the file to remove those lines and call `rrg pull` to pull down the files that were filtered out during the itial clone.

## Usage with git

The entire intent of `rrgit` is to use it as a companion to `git` itself to provide backups and history for your RepRapFirmware / Duet configs. You can do this in a couple ways:

- Create an empty remote git repo, clone it down locally, and then use `rrgit clone` to pull the configuration files into the local git repo directory. 
- Use `rrgit clone` to create a local `rrgit` directory, then use `git init` and `git remote add` inside of that directory to associate it with a remote git repo.

Once one of those options is done, you will be able to use all your normal `add`, `commit`, `push`, etc. commands with `git` to backup your configuration files. You basically will always want to use the opposite pull/push command in `rrgit` that you used with `git`. If you pull from the git back, use `rrgit push` to send that update to the remote machine, and vice versa.
