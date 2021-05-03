import geni.util

def get_context():
    try:
        return geni.util.loadContext()
    except IOError as e: # File not found. No credentials loaded?
        print('ERROR: Could not load context: ', e)
        print('''Are there any credentials available? If not, check
    https://docs.emulab.net/geni-lib/intro/credentials.html

Specifically, for cloudlab users, use:
  build-context --type cloudlab --cert <cert> --pubkey <pubkey> --project <name>
With e.g:
  <cert> = ~/.ssh/cloudlab.pem    (Cert must not be protected by a password!)
  <pubkey> = ~/.ssh/geni.rsa.pub  (Preferably without a password.)
  <name> = skyhook                (Note: must be all lowercase!)
''')
        return None
