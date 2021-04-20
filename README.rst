|Logo|

A simple Python approach to `XAnimePorn.com <https://www.xanimeporn.com/>`_
===========================================================================

| |Py-Versions| |Versions| |LICENCE|
| |GitHub-Status| |GitHub-Updated| |GitHub-Stars| |GitHub-Forks| |GitHub-Commits| |GitHub-Contributions| |GitHub-Issues| |GitHub-PRs|

| `XAnimePorn.com <https://www.xanimeporn.com/>`_ is a website that publishes hentai (ero-anime) videos/movies.
| This package allows to easily get data from the website.

Get Started
***********

It's really easy to get started with XAnimePorn. No tokens, no API credentials, nothing will stay between you and your
work. The only thing you will need is importing the package into your project using :code:`import XAnimePorn`.

Remember to also import the requirements in your project:

* `BeautifulSoup <https://pypi.org/project/beautifulsoup4/>`_
* `certifi <https://pypi.org/project/certifi/>`_
* `colorama <https://pypi.org/project/colorama/>`_
* `tqdm <https://pypi.org/project/tqdm/>`_
* `urllib3 <https://pypi.org/project/urllib3/>`_

After installing all the requirements your project is ready to use XAnimePorn.
Just use :code:`pip3 install XAnimePorn` to install the package.

There aren't many things to explain as
this is a really simple package but documentation can be found inside the code.

Here an example of what can this package do:

.. code-block:: python

    import XAnimePorn


    search = XAnimePorn.search("love", 1)  # Executes a research using the given keyword and taking only one element
    link = search[0]  # Takes the first element from the research
    video = XAnimePorn.Video(link)  # Creates a Video object from which it is possible to get information
    print(video.title)  # Prints the title of the video.
    print(video.url)  # Prints the link to the video.
    Video(link).download()  # Downloads the video.


    search = XAnimePorn.search("love", 10)  # Executes a research using the given keyword

    for link in search:  # For every video found
        video = XAnimePorn.Video(link)  # Creates a Video object
        print(video.title + " -> " + video.url)  # Prints the video title and link


Made with |Heart| by Stefan Cucoranu aka elpideus (elpideus@gmail.com)

.. |Logo| image:: http://www.xanimeporn.com/wp-content/uploads/anime%20porn.png
.. |Py-Versions| image:: https://img.shields.io/pypi/pyversions/XAnimePorn.svg?logo=python&logoColor=white
.. |Versions| image:: https://img.shields.io/pypi/v/XAnimePorn.svg
.. |LICENCE| image:: https://img.shields.io/badge/License-GPLv3-blue.svg
.. |GitHub-Status| image:: https://img.shields.io/github/tag/elpideus/XAnimePorn.svg?logo=github&logoColor=white
   :target: https://github.com/elpideus/XAnimePorn/releases
.. |GitHub-Forks| image:: https://img.shields.io/github/forks/elpideus/XAnimePorn.svg?logo=github&logoColor=white
   :target: https://github.com/elpideus/XAnimePorn/network
.. |GitHub-Stars| image:: https://img.shields.io/github/stars/elpideus/XAnimePorn.svg?logo=github&logoColor=white
   :target: https://github.com/elpideus/XAnimePorn/stargazers
.. |GitHub-Commits| image:: https://img.shields.io/github/commit-activity/y/elpideus/XAnimePorn.svg?logo=git&logoColor=white
   :target: https://github.com/elpideus/XAnimePorn/graphs/commit-activity
.. |GitHub-Updated| image:: https://img.shields.io/github/last-commit/elpideus/XAnimePorn/master.svg?logo=github&logoColor=white&label=pushed
   :target: https://github.com/elpideus/XAnimePorn/pulse
.. |GitHub-Contributions| image:: https://img.shields.io/github/contributors/elpideus/XAnimePorn.svg?logo=github&logoColor=white
   :target: https://github.com/elpideus/XAnimePorn/graphs/contributors
.. |GitHub-Issues| image:: https://img.shields.io/github/issues-closed/elpideus/XAnimePorn.svg?logo=github&logoColor=white
   :target: https://github.com/elpideus/XAnimePorn/issues?q=
.. |GitHub-PRs| image:: https://img.shields.io/github/issues-pr-closed/elpideus/XAnimePorn.svg?logo=github&logoColor=white
   :target: https://github.com/elpideus/XAnimePorn/pulls
.. |Heart| image:: https://icons.iconarchive.com/icons/paomedia/small-n-flat/16/heart-icon.png