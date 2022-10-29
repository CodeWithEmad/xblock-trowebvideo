from urllib.parse import urlparse

import pkg_resources
import requests
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String


class TrowebVideoXBlock(XBlock):
    """
    An XBlock providing oEmbed capabilities for video
    """

    href = String(
        help="URL of the video page at the provider", default=None, scope=Scope.content
    )
    maxwidth = Integer(
        help="Maximum width of the video", default=800, scope=Scope.content
    )
    maxheight = Integer(
        help="Maximum height of the video", default=450, scope=Scope.content
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        Create a fragment used to display the XBlock to a student.
        `context` is a dictionary used to configure the display (unused).

        Returns a `Fragment` object specifying the HTML, CSS, and JavaScript
        to display.
        """
        provider, embed_code = self.get_embed_code_for_url(self.href)
        # Load the HTML fragment from within the package and fill in the template
        html = self.resource_string("static/html/trowebvideo.html")
        frag = Fragment(html.format(self=self, embed_code=embed_code))
        frag.add_css(self.resource_string("static/css/trowebvideo.css"))
        frag.add_javascript(self.resource_string("static/js/src/trowebvideo.js"))
        frag.initialize_js("TrowebVideoXBlock")
        return frag

    def get_embed_code_for_url(self, url):
        """
        Get the code to embed from the oEmbed provider.
        """
        hostname = url and urlparse(url).hostname
        # Check that the provider is supported
        if hostname == "vimeo.com":
            oembed_url = "http://vimeo.com/api/oembed.json"
        else:
            return hostname, "<p>Unsupported video provider ({0})</p>".format(hostname)

        params = {
            "url": url,
            "format": "json",
            "maxwidth": self.maxwidth,
            "maxheight": self.maxheight,
            "api": True,
        }

        try:
            r = requests.get(oembed_url, params=params, timeout=10)
            r.raise_for_status()
        except Exception as e:
            return (
                hostname,
                "<p>Error getting video from provider ({error})</p>".format(error=e),
            )
        response = r.json()

        return hostname, response["html"]

    def studio_view(self, context):
        """
        Create a fragment used to display the edit view in the Studio.
        """
        html_str = pkg_resources.resource_string(__name__, "static/html/trowebvideo_edit.html")
        href = self.href or ''
        frag = Fragment(html_str.format(self=self, href=href, maxwidth=self.maxwidth, maxheight=self.maxheight))
        frag.add_javascript(self.resource_string("static/js/src/trowebvideo_edit.js"))
        frag.initialize_js("TrowebVideoEditBlock")
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.href = data.get('href')
        self.maxwidth = data.get('maxwidth')
        self.maxheight = data.get('maxheight')

        return {'result': 'success'}

    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            (
                "TrowebVideoXBlock",
                """<trowebvideo  href="https://vimeo.com/46100581" maxwidth="800"/>
             """,
            ),
            (
                "Multiple TrowebVideoXBlock",
                """<vertical_demo>
                <trowebvideo  href="https://vimeo.com/46100581" maxwidth="800"/>
                <trowebvideo  href="https://vimeo.com/46100581" maxwidth="800"/>
                <trowebvideo  href="https://vimeo.com/46100581" maxwidth="800"/>
                </vertical_demo>
             """,
            ),
        ]
