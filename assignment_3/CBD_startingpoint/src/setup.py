from setuptools import setup, find_packages

setup(name="CBD",
      version="0.1.0",
      description="Python CBD simulator",
      author=", ".join([
	      "Marc Provost <Marc.Provost@mail.mcgill.ca>",
	      "Hans Vangheluwe <Hans.Vangheluwe@uantwerpen.be>",
	      "Joachim Denil <Joachim.Denil@uantwerpen.be>",
	      "Claudio Gomes",
	      "Randy Paredis <Randy.Paredis@uantwerpen.be>"
      ]),
      url="http://msdl.cs.mcgill.ca/people/rparedis",
      packages=find_packages(include=('CBD.*',)),
      package_data={
	      '': ['*.c', '*.h', '*.lark']
      },
)
