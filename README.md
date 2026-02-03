# TaUTus

A all-in-one development tool for Python Ubuntu Touch Applications

## How to get started

0. Install Python 3
1. Get an instance of TaUTus
2. Initialise a new project with the command `init`.  
   The full command would look like this:  
   `./tautus.pyz init <directory name>`
3. Answer all questions asked by TaUTus
4. Change directory into the new project
5. Do something with the new project [(see this)](#all-features)
6. Build for desktop with `./tautus.pyz build desktop`

## All features

Some of the features can be disabled by specifying `--basic` while project creation. This type of project will be called "basic project" further along. Normally a created project is a "TaUTus extended project".

A basic project can be converted into a TaUTus extended project with the subcommand `convert`

### Integrated main.cpp file

Any TaUTus extended project will come shipped with a `main.cpp` file inside `src/` with PyOtherSide still working.

This is especially useful when working with QtWebEngines or when you need features not available inside QML or via PyOtherSide.

### Python library support

Within any TaUTus extended project you can install (almost) any python library and use it in your code with little to no effort.

There are two types of dependencies:

1. Dev dependencies - This is where clickable will be installed. You can also install other dependencies here if you need some libraries for pre-build actions.
2. (normal) Dependencies - These are dependencies for within the apps.

Normal dependencies can be installed using `./tautus.pyz deps add <name>` while dev dependencies can be installed using `./tautus.pyz deps -d add <name>`.

Normal dependencies can be imported in any Python file after calling `tautus_libs.load_libs()` (only needed once)

[See more in Commands](#python-libraries)

### Pre-implemented PageStack

For anyone who goes insane, when you have to create a PageStack. This will be wonderful news.

## Commands

### Project management

#### Project creation - `init [dirname]`

Creates a project at the directory (defaults to the current directory). Errors out when target directory is not empty.

Optional arguments are:

- `-b` / `--basic`: Create a basic project instead of a TaUTus extended one
- `--title`: Specify an answer instead of asking for one
- `--name`: Specify an answer instead of asking for one
- `--namespace`: Specify an answer instead of asking for one
- `--description`: Specify an answer instead of asking for one
- `--maintainer`: Specify an answer instead of asking for one
- `--mail`: Specify an answer instead of asking for one
- `--license`: Specify an answer instead of asking for one
- `--clickable-version`: Install the specified version instead of the latest

#### Convert a project to a TaUTus extended - `convert`

Convert the project in the current directory to a TaUTus extended one. Some files will be overwritten after confirmation, but a backup will always be created.

### Python libraries

Global arguments are:

- `-d` / `--dev`: Perform actions for Dev Dependencies instead of normal Dependencies
- `-n` / `--noadd`: Perform actions, but not save the changes to `tautus.json`
- `-D` / `--dry-run`: Don't change anything, just print out what would've

#### Subcommand - `add <name>`

Add the specified package. A specific version can be specified using `name==1.2.3`.

#### Subcommand - `update [name]`

_To be implemented._

#### Subcommand - `remove <name>`

Removes the specified package.

### Install project dependencies - `install`

_Similar to `npm i(nstall)`_  
Optional arguments are:

- `-D` / `--dry-run`: Don't change anything, just print out what would've

Install all dependencies and set up the clickable venv.

Normally only required after cloning/downloading a project without the folders `python-libs`/`tautus-venv`.

### Build the project - `build <target>`

Target:

- `device`: Build and install the project on a Ubuntu Touch device
- `desktop`: Build and run the project on the desktop
- `publish`: Build the project and run review. Specify an OpenStore API key using `-a`/`--apikey`.

Before the build, pre-build actions specified in [tautus.json](#project-manifest--tautusjson) will be run. In TaUTus extended projects QRC-files can also be auto-generated.

## Project manifest / tautus.json

_See the `tautus.example.json` file for examples_  
The manifest file stores every needed information for your project, like your dependencies, build flags
