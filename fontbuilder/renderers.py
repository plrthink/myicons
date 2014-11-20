import tempfile
import fontforge

from django.template.loader import render_to_string

from rest_framework import renderers

class FontCSSRenderer(renderers.BaseRenderer):
    media_type = 'text/css'
    format = 'css'
    charset = 'utf8'
    production = False

    def render(self, data, media_type=None, render_context=None):
        data['production'] = self.production
        icons = data['icons']
        data['classnames'] = ', '.join('.' + icon['classname'] for icon in icons)
        return render_to_string('fontcss.css', data)

class FontCheatSheetRenderer(renderers.BaseRenderer):
    media_type = 'text/html'
    format = 'html'
    charset = 'utf8'

    def render(self, data, media_type=None, render_context=None):
        return render_to_string('fontcheatsheet.html', data)


class SVGFontRenderer(renderers.BaseRenderer):
    media_type = 'text/svg+xml'
    format = 'svg'
    
    def render(self, data, media_type=None, render_context=None):
        return render_to_string('svgfont.svg', data)


class BinaryFontRenderer(SVGFontRenderer):
    media_type = 'application/octet-stream'
    charset = None
    render_style = 'binary'
    svgfile = None
    
    def get_svgfile(self, data):
        if self.svgfile: return self.svgfile
        svgtext = SVGFontRenderer.render(self, data)

        svgfile = tempfile.NamedTemporaryFile(suffix='.svg')
        svgfile.write(svgtext)
        svgfile.flush()

        self.svgfile = svgfile
        return self.svgfile

    def get_ttffile(self, data):
        if self.ttffile: return self.get_ttffile
        svtfile = self.get_svgfile()
        svgfont = fontforge.open(svgfile.name)
        ttffile = tempfile.NamedTemporaryFile(suffix='.ttf')
        svgfont.generate(ttffile.name)
        svgfont.close()
        self.ttffile = ttffile
        return self.ttffile

    def gen_binaryfont(self, fileformat, font):
        fontdata = ''
        tempfontfile = tempfile.NamedTemporaryFile(suffix=('.' + fileformat))
        with tempfontfile:
            font.generate(tempfontfile.name)
            fontdata = tempfontfile.read()
        return fontdata

    def render(self, data, media_type=None, render_context=None):
        svgfile = self.get_svgfile(data)
        font = fontforge.open(svgfile.name)
        fontdata = self.gen_binaryfont(self.format, font)
        font.close()
        svgfile.close()
        return fontdata


class WOFFRenderer(BinaryFontRenderer):
    format = 'woff'
