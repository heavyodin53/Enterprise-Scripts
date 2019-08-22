import psutil, argparse, sys, re, os, sys, csv, time, datetime, socket

parser = argparse.ArgumentParser(description='Get error and warning thresholds')
parser.add_argument("-w","--warning",help="Total percent of disk space free below which will generate a warning",type=float,required=True)
parser.add_argument("-c","--critical",help="Total percent of disk space free below which will generate a critical error",type=float,required=True)
parser.add_argument("-f","--file",help="location of the WizTree export csv",required=True)
parser.add_argument("-n","--number",help="Number of files to return",type=int,required=True)

args = parser.parse_args()

FileContents=[]

def ProcessData(severity, summary):
        with open(args.file, 'r') as csvfile:
                next(csvfile)
                csvreader = csv.DictReader(csvfile)
                FileContents = list(csvreader)
                #print(FileContents)
        FileContents = sorted(FileContents, key = lambda i: i['Size'], reverse = True)
        #FileContents[:5]
        numReturn = args.number
        output = ""
        for x in FileContents[:numReturn]:
                #print(x['File Name'], x['Size'])
                print("Disk_Check_All,Hostname:" + str(socket.gethostname()) + ",Summary:" + str(summary) + ",File Name:" + 
                        str(x['File Name']) + ",Size(bytes):" + 
                        str(['Size']) + 
                        ",Severity:" + 
                        severity)

        
        


crits = []
warns = []

disks = psutil.disk_partitions(all=False)

for disk in disks:
    ignoreDiskTypes = re.search('cdrom', disk.opts)
    ignoreMountPoints = re.search('(/var/lib/docker/containers|/snap.*)', disk.mountpoint)
    if not ignoreDiskTypes and not ignoreMountPoints:
        disk_usage = psutil.disk_usage(disk.mountpoint)
        disk_free_pct = 100 - disk_usage.percent
        if disk_free_pct <= args.warning and disk_free_pct > args.critical:
                warns.append("WARNING: Device {} at mount point {} has {}pct free space!".format(disk.device, disk.mountpoint, disk_free_pct))
        elif disk_free_pct <= args.critical:
                crits.append("CRITICAL: Device {} at mount point {} has {}pct free space!".format(disk.device, disk.mountpoint, disk_free_pct))
if crits and warns:
        for x in zip(crits,warns):
                print (x)
        sys.exit(2)
elif crits and not warns:
        ProcessData("Critical", crits)
        sys.exit(2)
elif warns and not crits:
        ProcessData("Warning", warns)
        sys.exit(1)
else:
        print ("OK")
        sys.exit(0)

#print (disks)