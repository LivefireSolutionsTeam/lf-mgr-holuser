# labstartup.py - version 2.1 - 15-April 2025

import datetime
import os
import lsfunctions as lsf
from pyVim import connect
import logging

# default logging level is WARNING (other levels are DEBUG, INFO, ERROR and CRITICAL)
logging.basicConfig(level=logging.DEBUG)

###
color = 'red'

# Run the module's init function (sets global start_time value to NOW)
# Sets vPod_SKU, max_minutes_before_fail and router statusnic to use
lsf.init(router=False)
lsf.write_output(f'labtype is {lsf.labtype}')
if lsf.labtype == 'HOL':
    lsf.init(router=True)

lsf.write_output(f'lsf.lab_sku: {lsf.lab_sku}')
lsf.parse_labsku(lsf.lab_sku)
lsf.postmanfix()  # update hosts file to prevent Postman paid upgrade

##############################################################################
#  User Variables
##############################################################################
# Edit /hol/config.ini on Main Console to set the vPod_SKU

##############################################################################
#  Main LabStartup
##############################################################################

# Please leave these lines here to enable scale testing automation
if lsf.start_autolab():
    exit(0)
else:
    lsf.write_output('No ' + lsf.autolab + ' found, continuing...')

# Report Initial State /hol/startup_status.txt
lsf.write_output('Beginning Main script')
lsf.write_vpodprogress('Not Ready', 'STARTING', color=color)  # recorded on desktop

# add custom preliminary tasks to /hol/Startup/prelim.py
lsf.startup('prelim')

##############################################################################
# Lab Startup - STEP #1 (vSphere Infrastructure)
##############################################################################

###
# verify ESXi hosts are ready
lsf.startup('ESXi')

# verify VCF components
lsf.startup('VCF')

# verify VCF components
lsf.startup('VVF')

# verify vCenter and start nested VMs
lsf.startup('vSphere')

##############################################################################
# Lab Startup - STEP #3 (Testing Pings)
##############################################################################

###
# Wait here for all hosts in the pings list to respond before continuing
lsf.startup('pings')

##############################################################################
# Lab Startup - STEP #4 (Start/Restart/Stop/Query Services and test ports)
##############################################################################

lsf.startup('services')

##############################################################################
#  Lab Startup - STEP #5 (Testing URLs, Kubernetes SSL and Tanzu
##############################################################################

###
# Testing Kubernetes SSL certificates (experimental)
lsf.startup('Kubernetes')
###
# Testing URLs
lsf.startup('urls')
# Start VCF Final
lsf.startup('VCFfinal')

##############################################################################
#  Lab Startup - STEP #6 (Final steps)
##############################################################################

###
# Add final checks in Startup/final.py that are required for your vPod to be marked READY
# Maybe you need to check something after the services are started/restarted.
###
lsf.startup('final')

##############################################################################
#  Lab Startup - STEP #7 (Odyssey)
##############################################################################

###
# Install the Odyssey client if indicated in the config.ini
###
lsf.startup('odyssey')

###
# Report current cloud using guestinfo provided by VLP
lsf.write_output(f'Hosting Cloud: {lsf.get_cloudinfo()}')

###
# Report final Ready state and duration of run
# NOTE: setting READY automatically marks the DesktopInfo badge GREEN
lsf.write_vpodprogress('Ready', 'READY', color='green')

# $readyTime = [Math]::Round((Get - RuntimeSeconds $startTime) / 60)
delta = datetime.datetime.now() - lsf.start_time
run_mins = "{0:.2f}".format(delta.seconds / 60)
lsf.write_output('LabStartup Finished - runtime was ' + str(run_mins) + ' minutes')
# Set - Content - Value($readyTime) -Path $readyTimeFile
tempfile = open(lsf.ready_time_file, "w+")
ready_mins = round(float(run_mins))
tempfile.write(str(ready_mins) + '\n')
tempfile.close()

##############################################################################
# Please leave this code here to enable vPod automated checking in HOL-DEV
if lsf.start_autocheck():
    lsf.write_output('Autocheck.ps1 complete.')

##############################################################################
