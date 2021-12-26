<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
	version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:xi="http://www.w3.org/2001/XInclude"
	xmlns:py="py"
	>
  <xsl:preserve-space elements="code script style" />
  <xsl:template match="/site">
	<py:filesystem>
	  <xsl:for-each select="./blog/blog_post">
		<py:directory path="blog">
		  <xsl:variable name="slug">
			<xsl:value-of select="concat(py:slugify(./title/text()), '.html')" />
		  </xsl:variable>
		  <xsl:variable name="self-url">
			<xsl:value-of select="py:replace(py:join(../../@host, ../../@path, 'blog', $slug), '//', '/')" />
		  </xsl:variable>
		  <py:file path="{$slug}" type="text">
			<!-- <py:minify type="html"> -->
			<py:serialize encoding="unicode" method="html" doctype="&lt;!doctype html&gt;">
			  <html lang="{./lang/text()}">
				<head>
				  <meta charset="UTF-8" />

				  <!-- Tags for search engines -->
				  <title>
					<xsl:value-of select="./title/text()"/> - <xsl:value-of select="../../sitename"/>
				  </title>
				  <meta name="description" content="{normalize-space(./teaser)}" />
				  <link rel="canonical" href="{../../@host}" />
				  <meta name="robots" content="index, follow" />
				  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

				  <!-- Opengraph tags for Facebook and others -->
				  <meta property="og:title" content="{./title}" />
				  <meta property="og:type" content="website" />
				  <meta property="og:url" content="{$self-url}" />
				  <meta property="og:image" content="{./header_image/@src}" />
				  <meta property="og:description" content="{normalize-space(./teaser)}" />
				  <meta property="og:locale" content="{py:replace(./lang/text(), '-', '_')}" />
				  <meta property="og:sitename" content="{../../sitename/text()}" />

				  <!-- Twitter card -->
				  <meta property="twitter:card" content="summary" />
				  <meta property="twitter:site" content="{../../twitter}" />
				  <meta property="twitter:creator" content="{./author/twitter}" />
				  <meta property="twitter:description" content="{normalize-space(./teaser)}" />
				  <meta property="twitter:title" content="{./title}" />
				  <meta property="twitter:image" content="{./header_image/@src}" />
				  <meta property="twitter:image:alt" content="{./header_image/@alt}" />

				  <!-- TOOD: favicons -->

				  <script>
					<py:minify type="js">
					  <xi:include href="main.js" parse="text" />
					</py:minify>
				  </script>
				  <style>
					<py:minify type="css">
					  <xi:include href="main.css" parse="text" />
					</py:minify>
				  </style>
				</head>
				<body>
				  <xi:include href="nav.html" parse="xml" />
				  <main id="column">
					<article>
					  <header>
						<!-- TOOD: Microdata
							 https://developers.google.com/search/docs/advanced/structured-data/search-gallery
						-->
						<h1>
						  <xsl:value-of select="./title" />
						</h1>
						<p class="byline">
						  by <xsl:value-of select="./author/name" /> on <xsl:value-of select="./date" />
						</p>
						<figure>
						  <img src="{./header_image/@src}" alt="{normalize-space(./header_image/@alt)}" />
						  <figcaption>
							<xsl:value-of select="./header_image/source" />
						  </figcaption>
						</figure>
						<xsl:if test="string-length(normalize-space(./title)) &gt; 70">
						  Title is too long for Twitter.
						</xsl:if>
						<xsl:if test="string-length(normalize-space(./teaser)) &gt; 200">
						  Teaser is too long for Twitter.
						</xsl:if>
					  </header>
					  <py:fixtext lang="{./lang/text()}">
						<xsl:copy-of select="./content/*" />
					  </py:fixtext>
					  <p>
						∎
					  </p>
					  <footer>
						<xi:include href="license.html" parse="xml" />
					  </footer>
					</article>
				  </main>
				</body>
			  </html>
			</py:serialize>
			<!-- </py:minify> -->
		  </py:file>
		</py:directory>
	  </xsl:for-each>
	</py:filesystem>
  </xsl:template>
</xsl:stylesheet>
