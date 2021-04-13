
from octoprint.plugins.softwareupdate.version_checks import github_release

result = github_release._is_current(dict(
										local=dict(value="1.11.1-dev"),
										remote=dict(value="1.12.dev1")),
									"python", force_base=False )
if (result):
	print("Locale Version is newer or equal")
else:
	print("Remote Version is newer, update available")
