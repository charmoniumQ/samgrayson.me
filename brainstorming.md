
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
- A language for describing metadata
  - YAML, could be others
- A language for describing file operations
  - Python(?), could be others
- A language for templating
  - Jinja, could be others

# Frontend language

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

# Problems

- Pollen assumes one-to-one mapping between source files and output files.
- SSG assume tree-of-HTML output.
- Do SSG support extending templates?
- SSG have no easy in-language way of creating output elements.
- Template languages are not complex enough.

# Considerations

- Incremental builds

## Helper functions

- Typography (smarten quotes, dashes, soft hyphens)
- Spell check

## Theme considerations

- Yahoo YSlow, Google Web Admin
- Semantic tags
- Asset bundling
- GZIP compression
- RSS and Atom feeds
- Comments
- Sitemap
- Strip EXIF data
- Server-side rendered code
- Navigation
