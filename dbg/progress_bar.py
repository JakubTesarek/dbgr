from progress.spinner import *

state = False
spinner = MoonSpinner('Loading ')
while state != 'FINISHED':
    # Do some work
    spinner.next()
