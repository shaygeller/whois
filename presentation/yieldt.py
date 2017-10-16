bashCommand = "whois biohaus-stiftung.de"
import subprocess
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print output
print error