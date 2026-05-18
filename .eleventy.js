const path = require("path");
const markdownIt = require("markdown-it");

module.exports = function (eleventyConfig) {
  // Disable inline HTML in markdown for XSS prevention
  // Song content (committed Markdown) does not need raw HTML.
  eleventyConfig.setLibrary("md", markdownIt({
    html: false,
    breaks: false,
    linkify: true,
    typographer: true,
  }));

  // Copy static assets to output (templates handle CSS/JS dynamically)
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/assets");

  // Respects BASE_URL pathPrefix for GitHub Pages builds.
  eleventyConfig.addShortcode("crossref", function (lang, number) {
    const langMap = { E: "english", H: "hindi", B: "bengali" };
    const slug = langMap[lang] || lang.toLowerCase();
    const prefix = (process.env.BASE_URL || "").replace(/\/$/, "");
    const safeSlug = slug.charAt(0).toUpperCase() + slug.slice(1);
    const safeTitle = `${safeSlug} song ${number}`.replace(/"/g, '&quot;');
    return `<a href="${prefix}/${slug}/${number}/" class="crossref" title="${safeTitle}">${lang}-${number}</a>`;
  });

  // Add json filter for Nunjucks templates (e.g., manifest.json.njk)
  eleventyConfig.addFilter("json", function (value) {
    return JSON.stringify(value);
  });

  // Create collections for each language
  eleventyConfig.addCollection("bengali", function (collection) {
    return collection
      .getFilteredByGlob("src/bengali/*.md")
      .sort(function (a, b) {
        return (a.data.number || 0) - (b.data.number || 0);
      });
  });

  eleventyConfig.addCollection("hindi", function (collection) {
    return collection.getFilteredByGlob("src/hindi/*.md").sort(function (a, b) {
      return (a.data.number || 0) - (b.data.number || 0);
    });
  });

  eleventyConfig.addCollection("english", function (collection) {
    return collection
      .getFilteredByGlob("src/english/*.md")
      .sort(function (a, b) {
        return (a.data.number || 0) - (b.data.number || 0);
      });
  });

  // Set input and output directories
  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      layouts: "_includes/layouts",
    },
    pathPrefix: process.env.BASE_URL || "/",
    templateFormats: ["njk", "md"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
  };
};
