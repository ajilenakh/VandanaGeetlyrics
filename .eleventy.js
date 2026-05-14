const crypto = require('crypto');
const path = require('path');
const fs = require('fs');

module.exports = function (eleventyConfig) {
  // Copy CSS and JS files to output
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/js");
  eleventyConfig.addPassthroughCopy("src/assets");

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

  // Add content hash to versioned assets
  eleventyConfig.addTransform('cache-bust', function(content, outputPath) {
    if (!outputPath) return content;
    const ext = path.extname(outputPath);
    if (['.css', '.js', '.ico', '.png', '.jpg'].includes(ext)) {
      const fullPath = path.join(__dirname, '_site', outputPath);
      if (fs.existsSync(fullPath)) {
        const data = fs.readFileSync(fullPath);
        const hash = crypto.createHash('md5').update(data).digest('hex').slice(0, 8);
        const dir = path.dirname(outputPath);
        const base = path.basename(outputPath, ext);
        const newName = `${base}.${hash}${ext}`;
        const newPath = path.join(dir, newName);
        // Rename the file
        fs.renameSync(fullPath, path.join(__dirname, '_site', newPath));
        // Update the reference in HTML
        return content.replace(outputPath, newPath);
      }
    }
    return content;
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
