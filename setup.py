from setuptools.command.install import install
class CustomInstallCommand(install):
    def run(self):
        print("from test 1 PWNNNNN")

setup(
    name='malicious',
    version='0.1.0',
    cmdclass={
        'install': CustomInstallCommand,
    },
)
