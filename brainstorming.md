# Motivation

I'm making a static site generator (SSG) for myself for fun.
I have not found an SSG that has the following properties:

- One can easily create new markup tags and apply transformations to those tags.
- The logic of how to generate a site is specified by user configuration.

## Custom transformations

I've thought of a few use cases for new markup tags, which could be server-side rendered:
numbered theorems (X.Y), images with attribution, spoilers, TODO lists, other interactive components.
Some of these are expressible in HTML and JavaScript, but I'd rather do the computation server-side and make JavaScript optional.
Conventional SSGs require a custom plugin for each thing, as in [Jekyll Katex].
One particularly neat application might be to a tag that specifies the language of the text it contains, and then a transformer that spell-checks the text in that language.
This would be especially useful for documents that mix different languages.

[Jekyll Katex]: https://github.com/linjer/jekyll-katex

## Push logic into configuration

How much of the logic is intrinsic the site-generator, and how much is specified by user configuration?
I think as much as possible should be left to the user.
This principle has been my Moby Dick: I don't need this for any practical reason, but I nonetheless want it anyway at the pain of great sacrifice.

There is an analogy with build systems:
the instructions of "how to invoke a compiler" can either be built in to the tool, resulting in a language-specific build-system like `maven`, or speciied by the user's configuration, resulting in a generic build-system like `make`.
You can find a `Makefile` "teaches" `make` how to compile each language, or you can make a new build-system for each language. Both have their advantages and disadvantages---I'm not saying everyone should use `make` for every language.

SSGs are like build systems that are specialized for generating HTML sites with a pre-defined format.
SSGs such as Jekyll, Hugo, Nikola, etc., can only generate HTML sites.
Jekyll requires a certain directory structure, where each file in `_posts` becomes a blog post HTML page.
They are somewhat configurable, but it would be difficult to generate a single-page web-application, a set of MediaWiki pages, or a LaTeX document.

[Pollen] makes strides more towards an analog `make`.
Each Pollen tag just calls a Racket function, which can be programmed to generate HTML, LaTeX, or anything else your heart desires.
However, Pollen still keeps an assumption where every file of content compiles to a file in the output.
It is constrained to generate sets of files, making it inappropriate for a single-page webapp.
One could write post-processor that glues all of the content together, but I feel that should be the job of the SSG.

[Pollen]: https://docs.racket-lang.org/pollen/

# My progress

An SSG needs:

- A language for authoring rich text
  - Markdown, could be others
    - Adding tags
      - Tags that interpret HTML
      - Tags that don't interpret HTML
	  - Image attributions
- A language for describing metadata
  - YAML, could be others
- A language for describing file operations
  - Python(?), could be others
- A language for templating
  - Jinja, could be others
  - Test if string too long

# Frontend language

- Top-down vs bottom-up
- Options:
  - Text + template invoke
    - This is what Pollen chooses.
    - This is what TeX is.
    - More verbose.
  - Text + Jinja
    - One-to-one template-to-output
    - Possible to mangle XML tags
    - Can't use XInclude
  - Markdown + template invoke
    - Less self-hosted.
  - XML
    - XML could also be the template invoking language.
    - Too verbose.
  - None, use backend language.
    - Too verbose.
    - Could be in addition to other option.

# Invoke template language

- Requirements
  - Support frontend language input. Pass front-end language objects into templates.
  - Support backend language input. Pass "programmatic" values into templates.
  - Modify control flow of document? Probably not.

# Backend language

- Top-down vs bottom-up
- Considerations:
  - Support frontend language input? This requires changing the language's reader. Probably not.
  - Support frontend language objects. 
  - Template substitution should be stateful.

# Engine

- Invoked from CLI or within program?
- Use framework to connect components or language?
- Nikola/Jekyll assumes tree-of-HTML output.
- Pollen assumes a one-to-one mapping between source files and output files.
- Output options:
  - Dynamic document: e.g. paragraph(blah, span(blah), blah)
  - Object IR
    - Why not use extended HTML?
  - HTML
    - Use Pandoc. Not necessarily complete.

# Others

- https://cjohansen.no/building-static-sites-in-clojure-with-stasis/
- https://nickgeorge.net/programming/custom-static-clojure-websites-an-update/
- https://metalsmith.io/

# Problems

- Pollen assumes one-to-one mapping between source files and output files.
- SSG assume tree-of-HTML output.
- Do SSG support extending templates?
- SSG have no easy in-language way of creating output elements.
- Template languages are not complex enough.

## Favicons

TODO[2]: Implement full favicon

Implementation:
- https://caniuse.com/?search=svg%20favicon
- https://medium.com/swlh/are-you-using-svg-favicons-yet-a-guide-for-modern-browsers-836a6aace3df
- https://lookout.dev/rules/use-svg-favicon
- https://developers.google.com/search/docs/advanced/structured-data/logo

## Helper functions

- Typography (smarten quotes, dashes, soft hyphens)
  - Subsumed by pandoc
- TODO[2]: Spell check

## Pages

- TODO[2]: home page
  - Content Bio, CV, research interest, adviser, hire me, publications, blog highlights, projects, contact me, linktree
  - https://indieweb.org/rel-me
  - https://indieweb.org/homepage
- TODO[1]: Redirections to old blog links
- TODO[2]: Sitemap: https://developers.google.com/search/docs/advanced/sitemaps/build-sitemap
- TODO[2]: RSS and Atom feeds: https://developers.google.com/search/docs/advanced/sitemaps/build-sitemap

## SEO

- https://indieweb.org/IndieMark
- https://indiewebify.me/
- https://developers.google.com/search/docs/beginner/search-console
- Google Webmaster
- Yahoo tools
- Yahoo YSlow, Google Web Admin
- https://sindice.com/developers/inspector.html
- https://developers.google.com/web/tools/lighthouse/
- https://developers.facebook.com/tools/debug/
- https://developers.google.com/search/docs/advanced/structured-data/search-gallery
- https://search.google.com/test/rich-results?utm_source=support.google.com/webmasters/
- https://support.google.com/webmasters/answer/7552505
- https://developers.google.com/search/docs/advanced/guidelines/get-started
- https://rdfa.info/tools
- https://cards-dev.twitter.com/validator
- https://www.opengraphcheck.com/
- https://validator.w3.org/
- https://www.greengeeks.com/blog/13-awesome-backlink-tools-that-will-benefit-your-seo/

## Structured data

- Title tag: https://developers.google.com/search/docs/advanced/appearance/title-link
- Meta description: https://developers.google.com/search/docs/advanced/appearance/snippet
- Google RDFa vs JSON-LD: https://developers.google.com/search/docs/advanced/structured-data/intro-structured-data
- Article: https://developers.google.com/search/docs/advanced/structured-data/article#non-amp
- TODO[1]: Use microdata, RDFa, JSON-LD, or microformats2.
  - https://www.techulator.com/resources/19112-json-ld-or-microdata-which-schema-format-is-better-for-ranking
  - What about microformats2?
  - https://mincong.io/2018/08/22/create-json-ld-structured-data-in-jekyll/
  
## Tests

- https://developer.chrome.com/docs/lighthouse/overview/
- http://rdfa.info/tools
- https://developers.google.com/search/docs/advanced/structured-data
- https://www.google.com/webmasters/markup-helper/u/0/
- https://microformats.org/wiki/validators

## Themes for inspiration

- https://practicaltypography.com/why-you-should-pay.html
- https://beautifulracket.com/bf/intro.html
- http://proselint.com/
- https://beautifuljekyll.com/2020-02-26-flake-it-till-you-make-it/
- https://www.w3schools.com/w3css/default.asp
- https://blog.ysndr.de/

## Other academic websites

- https://tianyin.github.io/
- http://www.cs.cmu.edu/~dskarlat/#
- http://danielskatz.org

## Other considerations

- TODO[2]: skip to main content
- TODO[3]: Asset bundling
- TODO[3]: GZIP compression
- TODO[3]: Minify HTML, CSS, and JS
- TODO[3]: Strip EXIF data from images
- TODO[3]: Server-side rendered code
- TODO[3]: Watchman + Simple HTTP server + trigger refresh
- TODO[3]: https://www.sitemaps.org/protocol.html#informing
- TODO[2]: push to github pages
- TODO[2]: Popout notes
- TODO[2]: Link anchor for headers
- TODO[2]: Check links for liveness, esp internal links
- TODO[1]: Sort essays somehow
