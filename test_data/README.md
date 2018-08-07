# Test Data
All data needed for testing the system in stored here.
Any file can be put here and committed however due to how git handles some files in directories (example: files on the ignore list) we can't simply commit directories.
Instead you should create a tarball of the directory and submit that.  
The `pack.sh` script will automatically create a tarball of all the directories so they can be committed.  
The `unpack.sh` script is run at test time to unpack all tarballs so their files can be used.
