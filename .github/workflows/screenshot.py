name: Take Webpage Screenshot

on:
  schedule:
    - cron: '0 * * * *'  # Runs every hour at the top of the hour
  workflow_dispatch:
    inputs:
      url:
        description: 'URL of the webpage to screenshot'
        required: false
        default: 'https://benjennings.design'

permissions:
  contents: write  # Allows the workflow to commit to the repository

jobs:
  capture_screenshot:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Dependencies
        run: npm install puppeteer sharp

      - name: Create Screenshots Directory
        run: mkdir -p screenshots

      - name: Take Screenshot
        run: |
          node -e '
          const puppeteer = require("puppeteer");
          const fs = require("fs");
          const sharp = require("sharp");

          (async () => {
            try {
              const browser = await puppeteer.launch({ args: ["--no-sandbox"] });
              const page = await browser.newPage();

              // Set viewport size to 480x800 pixels
              await page.setViewport({ width: 480, height: 800 });

              const url = process.env.INPUT_URL || "https://benjennigns.design";
              await page.goto(url, { waitUntil: "networkidle2" });

              const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
              const pngFilePath = `screenshots/screenshot.png`;
              const bmpFilePath = `screenshots/screenshot.bmp`;

              // Ensure the screenshots directory exists
              if (!fs.existsSync("screenshots")) {
                fs.mkdirSync("screenshots");
              }

              // Take the screenshot in PNG format
              await page.screenshot({ path: pngFilePath });

              // Convert PNG to BMP using sharp
              await sharp(pngFilePath)
                .toFormat("bmp")
                .toFile(bmpFilePath);

              // Delete the PNG file if you only want the BMP file
              fs.unlinkSync(pngFilePath);

              await browser.close();
              console.log("Screenshot saved to", bmpFilePath);
            } catch (error) {
              console.error("Error taking screenshot:", error);
              process.exit(1);
            }
          })();
          '

      - name: Commit Screenshot
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: 'Add new screenshot [skip ci]'
          file_pattern: screenshots/*.bmp
