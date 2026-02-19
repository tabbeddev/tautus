# Project Types

TaUTus can work with two types of project:

- TaUTus project
- (TaUTus) extended project

They all base on the same Clickable App Template and you can generally do the same stuff with both projects.  
The only difference is who is in charge of handling some tasks.

## TaUTus projects

- Is based on the Clickable Python Template
- Updates some manifest files for you upon build
- Supports build hooks
- Supports build for Desktop, an UT device and for release
- Doesn't come with a working QRC structure bundled
- Can't update QRC files
- Doesn't support python libraries through TaUTus

## TaUTus extended projects

Same as [TaUTus projects](#tautus-projects), but:

- Comes with a working QRC structure bundled
- Can update QRC files upon build
- Supports python libraries
- Comes with a working main.cpp file bundled, in case you need it
