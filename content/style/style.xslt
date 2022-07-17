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
		<xsl:variable name="self-url">
		  <xsl:value-of select="../../@host" />
		</xsl:variable>
		<py:minify type="html">
		  <py:serialize encoding="unicode" method="html" doctype="&lt;!doctype html&gt;">
			<xi:include href="blog_index.html" />
		  </py:serialize>
		</py:minify>
	  </py:file>
	  <py:directory path="blog">
		<xsl:for-each select="./blog/blogPost">
		  <xsl:variable name="slug">
			<xsl:value-of select="py:slugify(./name/text())" />
		  </xsl:variable>
		  <xsl:variable name="self-url">
			<xsl:value-of select="py:join(../../@host, 'blog', $slug)" />
		  </xsl:variable>
		  <py:file path="{$slug}" type="text">
			<py:minify type="html">
			  <py:serialize encoding="unicode" method="html" doctype="&lt;!doctype html&gt;">
				<xi:include href="blog_post.html" parse="xml" />
			  </py:serialize>
			</py:minify>
		  </py:file>
		</xsl:for-each>
	  </py:directory>
	  <xsl:for-each select="./redirects/redirect"
					xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
					xmlns:xi="http://www.w3.org/2001/XInclude"
					xmlns:py="py"
					>
		<py:file path="{./@source}" type="text">
		  <py:minify type="html">
			<py:serialize encoding="unicode" method="html" doctype="&lt;!doctype html&gt;">
			  <xi:include href="moved.html" parse="xml" />
			</py:serialize>
		  </py:minify>
		</py:file>
	  </xsl:for-each>
	  <py:file path="404.html" type="text">
		<py:minify type="html">
		  <py:serialize encoding="unicode" method="html" doctype="&lt;!doctype html&gt;">
			<xi:include href="404.html" parse="xml" />
		  </py:serialize>
		</py:minify>
	  </py:file>
	  <py:file path="robots.txt" type="text">
		Sitemap: <xsl:value-of select="./@host" />/sitemap.xml
	  </py:file>
	  <py:file path="sitemap.xml" type="xml">
		<xi:include href="sitemap.xml" type="xml" />
	  </py:file>
	</py:filesystem>
  </xsl:template>

  <xsl:template match="person">
	<span typeof="Person">
	  <a rel="url" href="{./url}" >
		<span property="givenName">
		  <xsl:value-of select="./givenName" />
		</span>
		<xsl:text> </xsl:text>
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

  <!-- TODO[2]: at a "last updated" watermark -->

  <!-- TODO[2]: contact page -->

</xsl:stylesheet>
