#stress-ng --cpu 1 --io 1 --vm 1 --vm-bytes 1G --timeout 5m
stress-ng --cpu 1 -d 1 --hdd-bytes 250M -m 1 --vm-bytes 256M --iomix 1 --iomix-bytes 256M --timeout 5m
#stress-ng --cpu 4 --io 2 --vm 1 --vm-bytes 1G --timeout 60s
