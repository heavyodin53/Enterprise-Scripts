import psutil
import argparse
import sys
import re

parser = argparse.ArgumentParser(description='Get error and warning thresholds')
parser.add_argument("-w","--warning",help="Total percent of disk space free below which will generate a warning",type=float, required=True)
parser.add_argument("-c","--critical",help="Total percent of disk space free below which will generate a critical error",type=float, required=True)

args = parser.parse_args()

crits = []
warns = []

disks = psutil.disk_partitions(all=False)

for disk in disks:
    ignoreDiskTypes = re.search('cdrom', disk.opts)
    ignoreMountPoints = re.search('(/var/lib/docker/containers|/snap.*)', disk.mountpoint)
    if not ignoreDiskTypes and not ignoreMountPoints:
        disk_usage = psutil.disk_usage(disk.mountpoint)
        disk_free_pct = 100 - disk_usage.percent
        
        print (disk_free_pct)
        
        if disk_free_pct <= args.warning and disk_free_pct > args.critical:
                disk_info = {
                        "Summary": "WARNING: Device {} at mount point {} has {} pct free space!".format(disk.device, disk.mountpoint, disk_free_pct),
                        "Class": "High Disk",
                        "Component": "disk_space"
                }
                warns.append(disk_info)
        elif disk_free_pct <= args.critical:
                disk_info = {
                        "Summary": "CRITICAL: Device {} at mount point {} has {} pct free space!".format(disk.device, disk.mountpoint, disk_free_pct),
                        "Class": "High Disk",
                        "Component": "disk_space"
                }
                crits.append(disk_info)

if crits and warns:
        for x in zip(crits,warns):
                print (x)
        sys.exit(2)

elif crits and not warns:
        print (crits)
        sys.exit(2)

elif warns and not crits:
        print (warns)
        sys.exit(1)

else:
        print (crits)
        print (warns)
        print ("OK")
        sys.exit(0)

print (disks)