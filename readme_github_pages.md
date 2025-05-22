# Setting Up GitHub Pages for Container Farm Control System

This repository includes files for GitHub Pages to make the documentation easily accessible online. Follow these steps to enable GitHub Pages for your repository:

## Quick Setup

1. Push all repository files to GitHub, including the files in:
   - `_layouts/` directory
   - `assets/css/` directory
   - `pages/` directory
   - `_config.yml` file
   - `index.md` file

2. Go to your repository on GitHub

3. Click on "Settings"

4. Scroll down to the "GitHub Pages" section

5. Under "Source", select "main branch" or whichever branch contains your documentation

6. Click "Save"

Your documentation will be available at: `https://your-username.github.io/container-farm-control-system/`

## Customizing Your Site

Before enabling GitHub Pages, make these changes:

1. Update your repository information in `_config.yml`:
   - Change `your-username` to your actual GitHub username
   - Update any other information as needed

2. Add images to the `assets/images/` directory:
   - Create this directory if it doesn't exist
   - Add a header image named `header-image.jpg`
   - Add the wiring diagram as `wiring-diagram.svg`

3. Test links to ensure they work correctly

## Adding New Pages

To add a new documentation page:

1. Create a markdown file in the `pages/` directory:
   ```
   pages/your-new-page.md
   ```

2. Include the front matter at the top:
   ```yaml
   ---
   layout: default
   title: Your Page Title
   ---
   ```

3. Add the page to the navigation in `_config.yml`:
   ```yaml
   navigation:
     - title: Your Page Title
       url: /pages/your-new-page
   ```

## Local Testing

To test the site locally before deploying:

1. Install Jekyll and Ruby:
   ```bash
   gem install bundler jekyll
   ```

2. Create a `Gemfile` with:
   ```ruby
   source "https://rubygems.org"
   gem "github-pages", group: :jekyll_plugins
   ```

3. Run:
   ```bash
   bundle install
   bundle exec jekyll serve
   ```

4. View your site at: `http://localhost:4000`

## Need Help?

If you encounter issues with GitHub Pages, refer to:
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
