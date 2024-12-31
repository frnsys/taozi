import re
import markdown
from xml.etree import ElementTree as etree
# from markdown.util import etree
from markdown.extensions import attr_list
from markdown.inlinepatterns import SimpleTagPattern, Pattern
from mdx_gfm import GithubFlavoredMarkdownExtension as GFM

AT = attr_list.AttrListTreeprocessor()


def compile_markdown(md):
    """compiles markdown to html"""
    extensions = [
        GFM(),
        ExtendedMD(),
        FigureCaptionExtension(),
        'markdown.extensions.footnotes',
        'markdown.extensions.attr_list',
        'markdown.extensions.headerid',
    ]
    return markdown.markdown(md, extensions=extensions, lazy_ol=False)


class VideoPattern(Pattern):
    def handleMatch(self, m):
        src = m.group(3)
        fig = etree.Element('figure')
        obj = etree.SubElement(fig, 'video')
        obj.set('src', src)

        attrs = m.group(5)
        caption = m.group(2)
        if caption:
            cap = etree.SubElement(fig, 'figcaption')
            cap.text = caption
        if attrs is not None:
            AT.assign_attrs(obj, attrs)
        return fig


class IFramePattern(Pattern):
    def handleMatch(self, m):
        src = m.group(3)
        obj = etree.Element('iframe')
        obj.set('src', src)

        attrs = m.group(5)
        if attrs is not None:
            AT.assign_attrs(obj, attrs)
        return obj


class ExtendedMD(markdown.Extension):
    """an extension that supports:
    - highlighting with the <mark> tag.
    """
    HIGHLIGHT_RE = r'(={2})(.+?)(={2})' # ==highlight==
    VID_RE = r'\!\[(.*)\]\(`?(?:<.*>)?([^`\(\)]+mp4)\)({:([^}]+)})?' # ![...](path/to/something.mp4){: autoplay}
    URL_RE = r'@\[(.*)\]\(`?(?:<.*>)?([^`\(\)]+)\)({:([^}]+)})?' # @[](http://web.site){: .fullscreen}

    def extendMarkdown(self, md):
        highlight_pattern = SimpleTagPattern(self.HIGHLIGHT_RE, 'mark')
        md.inlinePatterns.add('highlight', highlight_pattern, '_end')

        vid_pattern = VideoPattern(self.VID_RE)
        md.inlinePatterns.add('video_link', vid_pattern, '_begin')

        url_pattern = IFramePattern(self.URL_RE)
        md.inlinePatterns.add('iframe_link', url_pattern, '_begin')


"""
The below is from: <https://github.com/jdittrich/figureAltCaption>
(Not provided as a pypi package, so reproduced here)

Generates a Caption for Figures for each Image which stands alone in a paragraph,
similar to pandoc#s handling of images/figures

--------------------------------------------

Licensed under the GPL 2 (see LICENSE.md)

Copyright 2015 - Jan Dittrich by
building upon the markdown-figures Plugin by
Copyright 2013 - [Helder Correia](http://heldercorreia.com) (GPL2)
"""
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import IMAGE_LINK_RE, IMAGE_REFERENCE_RE
CLASS_RE = '(\{\.([A-Za-z-_]+)\})'
FIGURES = [u'^\s*'+IMAGE_LINK_RE+CLASS_RE+u'?\s*$', u'^\s*'+IMAGE_REFERENCE_RE+CLASS_RE+u'?\s*$'] #is: linestart, any whitespace (even none), image, any whitespace (even none), line ends.


# This is the core part of the extension
class FigureCaptionProcessor(BlockProcessor):
    FIGURES_RE = re.compile('|'.join(f for f in FIGURES))
    CLASS_RE = re.compile(CLASS_RE)
    def test(self, parent, block): # is the block relevant
        isImage = bool(self.FIGURES_RE.search(block))
        isOnlyOneLine = (len(block.splitlines())== 1)
        isInFigure = (parent.tag == 'figure')

        # print(block, isImage, isOnlyOneLine, isInFigure, "T,T,F")
        if (isImage and isOnlyOneLine and not isInFigure):
            return True
        else:
            return False

    def run(self, parent, blocks): # how to process the block?
        raw_block = blocks.pop(0)
        captionText = self.FIGURES_RE.search(raw_block).group(1)

        # create figure
        figure = etree.SubElement(parent, 'figure')

        cls = self.CLASS_RE.search(raw_block)
        if cls is not None:
            cls = cls.group(2)
            raw_block = self.CLASS_RE.sub('', raw_block)
            figure.attrib['class'] = cls

        # render image in figure
        figure.text = raw_block

        # create caption
        figcaptionElem = etree.SubElement(figure,'figcaption')
        figcaptionElem.text = captionText #no clue why the text itself turns out as html again and not raw. Anyhow, it suits me, the blockparsers annoyingly wrapped everything into <p>.


class FigureCaptionExtension(markdown.Extension):
    def extendMarkdown(self, md):
        """ Add an instance of FigcaptionProcessor to BlockParser. """
        md.parser.blockprocessors.add('figureAltcaption',
                                      FigureCaptionProcessor(md.parser),
                                      '<ulist')
