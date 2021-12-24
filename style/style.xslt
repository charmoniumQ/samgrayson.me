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
		  <py:file path="{py:slugify(./title/text())}.html" type="text">
			<!-- <py:minify type="html"> -->
			  <py:serialize encoding="unicode" method="html" doctype="&lt;!doctype html&gt;">
				<html lang="{./lang/text()}">
				  <head>
					<!-- https://ahrefs.com/blog/seo-meta-tags/ -->
					<title>
					  <xsl:value-of select="./title/text()"/> - <xsl:value-of select="/sitename"/>
					</title>
					<meta charset="UTF-8" />
					<meta name="description" content="{normalize-space(./teaser/text())}" />
					<meta name="robots" content="index, follow" />
					<meta name="viewport" content="width=device-width, initial-scale=1.0" />
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
					<div id="column">
					  <main>
						<article>
						  <header>
							<h1>
							  <xsl:value-of select="./title" />
							</h1>
							<p class="byline">
							  by <xsl:value-of select="./author" /> on <xsl:value-of select="./date" />
							</p>
							<figure>
							  <img src="{./header_image/url}" alt="{normalize-space(./header_image/alt)}"/>
							  <figcaption>
								<xsl:value-of select="./header_image/source" />
							  </figcaption>
							</figure>
						  </header>
						  <py:fixtext lang="{./lang/text()}">
							<xsl:copy-of select="./content/*" />
						  </py:fixtext>
						</article>
					  </main>
					  </div>
					  <footer>
						<a href="{./path}"><xsl:value-of select="/sitename" /></a><br />
						<xsl:value-of select="./license" />
					  </footer>
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
