
# from octoprint.plugins.softwareupdate.version_checks import github_release
#
# result = github_release._is_current(dict(
# 										local=dict(value="1.11.1-dev"),
# 										remote=dict(value="1.12.dev1")),
# 									"python", force_base=False )
# if (result):
# 	print("Locale Version is newer or equal")
# else:
# 	print("Remote Version is newer, update available")


v1 = '1.4.3rc1'
v2 = '1.4.2'



def _get_comparable_version_semantic(version_string, force_base=False):
    import semantic_version

    version = semantic_version.Version.coerce(version_string, partial=False)

    if force_base:
        version_string = "{}.{}.{}".format(version.major, version.minor, version.patch)
        version = semantic_version.Version.coerce(version_string, partial=False)

    return version


# try:
# 	import semantic_version
#
# 	canBeUsed = semantic_version.Version(v2) >= semantic_version.Version(v1)
# except (ValueError) as error:
# 	print("BOOOMMMM !!!!Something is wrong with the costestimation version numbers")

myVersion1 = _get_comparable_version_semantic(v1)
myVersion2 = _get_comparable_version_semantic(v2)
import semantic_version
canBeUsed = myVersion1 >= myVersion2
print(canBeUsed)
