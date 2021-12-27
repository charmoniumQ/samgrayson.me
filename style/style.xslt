<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
	version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:xi="http://www.w3.org/2001/XInclude"
	xmlns:py="py"
	>

  <xsl:template match="/site">
	<py:filesystem>
	  <xsl:for-each select="./blog/blogPost">
		<py:directory path="blog">
		  <xsl:variable name="slug">
			<xsl:value-of select="concat(py:slugify(./title/text()), '.html')" />
		  </xsl:variable>
		  <xsl:variable name="self-url">
			<xsl:value-of select="py:replace(py:join(../../@host, ../../@path, 'blog', $slug), '//', '/')" />
		  </xsl:variable>
		  <py:file path="{$slug}" type="text">
			<py:minify type="html">
			  <py:serialize encoding="unicode" method="html" doctype="&lt;!doctype html&gt;">
				<html lang="{./inLanguage/text()}">
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
					<meta property="og:image" content="{./image/url}" />
					<meta property="og:description" content="{normalize-space(./teaser)}" />
					<meta property="og:locale" content="{py:replace(./inLanguage/text(), '-', '_')}" />
					<meta property="og:sitename" content="{../../sitename/text()}" />

					<!-- Twitter card -->
					<meta property="twitter:card" content="summary" />
					<meta property="twitter:site" content="{../../twitter}" />
					<meta property="twitter:creator" content="{./author/person/extra/twitter}" />
					<meta property="twitter:description" content="{normalize-space(./teaser)}" />
					<meta property="twitter:title" content="{./title}" />
					<meta property="twitter:image" content="{./image/url}" />
					<meta property="twitter:image:alt" content="{./image/caption}" />

					<!-- TOOD: favicons -->

					<script>
					  <xi:include href="main.js" parse="text" />
					</script>
					<style>
					  <xi:include href="main.css" parse="text" />
					</style>
				  </head>
				  <body vocab="http://schema.org/">
					<xi:include href="nav.html" parse="xml" />
					<main id="column">
					  <article typeof="BlogPosting">
						<header>
						  <h1 property="name">
							<xsl:value-of select="./title" />
						  </h1>
						  <p class="byline">
							by
							<span property="author">
							  <xsl:apply-templates select="./author" />
							</span>
							on
							<meta property="datePublished" content="{./datePublished}" />
							<py:date>
							  <xsl:value-of select="./datePublished" />
							</py:date>
						  </p>
						  <div property="image">
							<xsl:apply-templates select="./image" />
						  </div>
						  <xsl:if test="string-length(normalize-space(./title)) &gt; 70">
							<py:warn>Title of "<xsl:value-of select="./title"/>" is too long for Twitter.</py:warn>
						  </xsl:if>
						  <xsl:if test="string-length(normalize-space(./teaser)) &gt; 200">
							<py:warn>Teaser of "<xsl:value-of select="./title"/>" is too long for Twitter.</py:warn>
						  </xsl:if>
						</header>
						<div property="text">
						  <py:fixtext lang="{./inLanguage/text()}">
							<xsl:copy-of select="./articleBody/*" />
						  </py:fixtext>
						</div>
						<footer>
						  <xi:include href="license.html" parse="xml" />
						  <p class="cite-as">
							Cite as:
							<span property="creditText">
							  “<a href="{$self-url}">
							  <xsl:value-of select="./title" />
							</a>
							by
							<xsl:apply-templates select="./author/person" />”
							</span>.
						  </p>
						</footer>
					  </article>
					</main>
				  </body>
				</html>
			  </py:serialize>
			</py:minify>
		  </py:file>
		</py:directory>
	  </xsl:for-each>
	</py:filesystem>
  </xsl:template>

  <xsl:template match="person">
	<span typeof="Person">
	  <a rel="url" href="{./url}" >
		<span property="givenName">
		  <xsl:value-of select="./givenName" />
		</span>
		<!-- TODO: insert space -->
		<span property="familyName">
		  <xsl:value-of select="./familyName" />
		</span>
	  </a>
	</span>
  </xsl:template>

  <xsl:template match="image">
	<figure typeof="ImageObject">
	  <img property="contentUrl" src="{./url}" alt="{normalize-space(./caption)}" />
	  <figcaption>
		<p class="caption" property="caption">
		  <xsl:value-of select="./caption" />
		</p>
		<p class="attribution" property="creditText">
		  Attribution:
		  <a href="{./originalMediaLink}">
			<xsl:value-of select="./name" />
		  </a>
		  by
		  <xsl:value-of select="./creator" />;
		  licensed as
		  <span typeof="CreativeWork">
			<a property="url" href="{./license/url}">
			  <span property="name">
				<xsl:value-of select="./license/name" />
			  </span>
			</a>.
		  </span>
		</p>
	  </figcaption>
	</figure>
  </xsl:template>

</xsl:stylesheet>
