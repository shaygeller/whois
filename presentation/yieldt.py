import subprocess
# print subprocess.Popen("whois biohaus-stiftung.de")

bashCommand = "whois biohaus-stiftung.de"
output = subprocess.check_output(['bash','-c', bashCommand])
print output