const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/chromium',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  
  console.log('Navigating to http://localhost:5173/styles...');
  await page.goto('http://localhost:5173/styles', { waitUntil: 'networkidle0' });
  
  console.log('Taking initial screenshot...');
  await page.screenshot({ path: '/tmp/styles-page-initial.png', fullPage: true });
  console.log('Screenshot saved to /tmp/styles-page-initial.png');
  
  // Wait for content to load
  await page.waitForSelector('.styles-page', { timeout: 5000 });
  
  // Check if "Страница" tab exists
  const tabs = await page.$$eval('.tab-btn', buttons => 
    buttons.map(btn => btn.textContent.trim())
  );
  console.log('Available tabs:', tabs);
  
  // Click on "Страница" tab if it exists
  if (tabs.includes('Страница')) {
    console.log('Clicking on "Страница" tab...');
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('.tab-btn'));
      const pageTab = buttons.find(btn => btn.textContent.trim() === 'Страница');
      if (pageTab) pageTab.click();
    });
    await page.waitForTimeout(500);
    await page.screenshot({ path: '/tmp/styles-page-tab.png', fullPage: true });
    console.log('Screenshot saved to /tmp/styles-page-tab.png');
  }
  
  // Click on "Текст и абзац" tab if it exists
  if (tabs.includes('Текст и абзац')) {
    console.log('Clicking on "Текст и абзац" tab...');
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('.tab-btn'));
      const textTab = buttons.find(btn => btn.textContent.trim() === 'Текст и абзац');
      if (textTab) textTab.click();
    });
    await page.waitForTimeout(500);
    await page.screenshot({ path: '/tmp/styles-text-tab.png', fullPage: true });
    console.log('Screenshot saved to /tmp/styles-text-tab.png');
    
    // Check for nested tabs
    const nestedTabs = await page.$$eval('.tab-btn', buttons => 
      buttons.map(btn => btn.textContent.trim())
    );
    console.log('Nested tabs:', nestedTabs);
    
    // Click on "Текст" nested tab if visible
    if (nestedTabs.includes('Текст')) {
      console.log('Clicking on "Текст" nested tab...');
      await page.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll('.tab-btn'));
        const textSubTab = buttons.find(btn => btn.textContent.trim() === 'Текст');
        if (textSubTab) textSubTab.click();
      });
      await page.waitForTimeout(500);
      await page.screenshot({ path: '/tmp/styles-text-fields.png', fullPage: true });
      console.log('Screenshot saved to /tmp/styles-text-fields.png');
    }
  }
  
  // Get all form fields
  const fields = await page.evaluate(() => {
    const labels = Array.from(document.querySelectorAll('label'));
    return labels.map(label => label.textContent.trim());
  });
  console.log('Form fields visible:', fields);
  
  await browser.close();
  console.log('Done!');
})();
