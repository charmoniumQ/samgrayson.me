<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
	version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:xi="http://www.w3.org/2001/XInclude"
	xmlns:py="py"
	>

  <xsl:template match="site">
	<py:filesystem>
	  <py:file path="index.html" type="text">
		<py:minify type="html">
		  <py:serialize encoding="unicode" method="html" doctype="&lt;!doctype html&gt;">
			<xi:include href="site_index.html" />
		  </py:serialize>
		</py:minify>
	  </py:file>
	  <xsl:apply-templates select="./blog" />
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

  <xsl:template match="blogPost">
	<xsl:variable name="slug">
	  <xsl:value-of select="concat(py:slugify(./name/text()), '.html')" />
	</xsl:variable>
	<xsl:variable name="self-url">
	  <xsl:value-of select="py:replace(py:join(../../@host, ../../@path, 'blog', $slug), '//', '/')" />
	</xsl:variable>
	<py:file path="{$slug}" type="text">
	  <py:minify type="html">
		<py:serialize encoding="unicode" method="html" doctype="&lt;!doctype html&gt;">
		  <xi:include href="blog_post.html" parse="xml" />
		</py:serialize>
	  </py:minify>
	</py:file>
  </xsl:template>

  <xsl:template match="blog">
	<py:directory path="blog">
	  <py:file path="index.html" type="text">
		<xsl:variable name="self-url">
		  <xsl:value-of select="py:replace(py:join(../@host, ../@path, 'blog/index.html'), '//', '/')" />
		</xsl:variable>
		<py:minify type="html">
		  <py:serialize encoding="unicode" method="html" doctype="&lt;!doctype html&gt;">
			<xi:include href="blog_index.html" parse="xml" />
		  </py:serialize>
		</py:minify>
	  </py:file>
	  <xsl:for-each select="./blogPost">
		<xsl:apply-templates select="." />
	  </xsl:for-each>
	</py:directory>
  </xsl:template>

</xsl:stylesheet>
