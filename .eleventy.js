const path = require('path');

module.exports = function (eleventyConfig) {
  // Copy static assets to output (templates handle CSS/JS dynamically)
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/assets");

  // Add json filter for Nunjucks templates (e.g., manifest.json.njk)
  eleventyConfig.addFilter("json", function (value) {
    return JSON.stringify(value);
  });

  // Create collections for each language
  eleventyConfig.addCollection("bengali", function (collection) {
    return collection
      .getFilteredByGlob("src/bengali/*.md")
      .sort(function (a, b) {
        return a.data.number - b.data.number;
      });
  });

  eleventyConfig.addCollection("hindi", function (collection) {
    return collection.getFilteredByGlob("src/hindi/*.md").sort(function (a, b) {
      return a.data.number - b.data.number;
    });
  });

  eleventyConfig.addCollection("english", function (collection) {
    return collection
      .getFilteredByGlob("src/english/*.md")
      .sort(function (a, b) {
        return a.data.number - b.data.number;
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
