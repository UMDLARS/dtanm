# This file is included in the application config for both the UI and workers.

# This is the executable that is run to test the application. If the user does
# not either provide an executable with this name or a makefile to create one,
# the user's program will not be run.
SCORING_BIN_NAME = "echo"

# This is the name of the gold executable. You should either provide this file
# or a makefile configured to create it.
SCORING_GOLD_NAME = "gold"

# This is the email/password of the initially created admin user
# Because the password is stored in plain text, we recommend leaving it as
# 'password' or similar and then changing it with the Reset Password function
# in the application (which will bcrypt the password properly).
ADMIN_USER_EMAIL = "swift106@d.umn.edu"
ADMIN_USER_PASSWORD = "password"

# Maximum resources allotted to a single run of a scoring process
SCORING_MAX_CPUS = 2
SCORING_MAX_MEMORY = "512M"
SCORING_MAX_PROCESSES = 100
SCORING_MAX_TIME = 5

# If you want network access, uncomment this.
# CAUTION! This may allow access to the internal scoring network, so
# anyone with knowledge of DTANM's architecture could modify scores.
#SCORING_DISABLE_NETWORK = False

# Time zone that times should be displayed in on the Web UI.
# American time zones, from east to west, are America/New_York,
# America/Chicago, America/Denver, America/Los_Angeles, America/Anchorage,
# America/Honolulu. A complete list can be found here:
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE="America/Chicago"

# Attack submissions can be limited to RATE_LIMIT_QUANTITY submissions per
# RATE_LIMIT_SECONDS seconds. Set RATE_LIMIT_QUANTITY to 0 to disable. The
# count is done based on a rolling interval (i.e. on submit, has the user
# submitted more than m attacks in the last n seconds?).
RATE_LIMIT_QUANTITY = 6
RATE_LIMIT_SECONDS = 60
