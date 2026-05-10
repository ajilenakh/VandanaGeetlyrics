module.exports = function (eleventyConfig) {
  // Copy CSS and JS files to output
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/js");

  // Create collections for each language
  eleventyConfig.addCollection("bengali", function (collection) {
    return collection.getFilteredByGlob("src/bengali/*.md").sort(function (a, b) {
      return a.data.number - b.data.number;
    });
  });

  eleventyConfig.addCollection("hindi", function (collection) {
    return collection.getFilteredByGlob("src/hindi/*.md").sort(function (a, b) {
      return a.data.number - b.data.number;
    });
  });

  eleventyConfig.addCollection("english", function (collection) {
    return collection.getFilteredByGlob("src/english/*.md").sort(function (a, b) {
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
    templateFormats: ["njk", "md"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
  };
};
