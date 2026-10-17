import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";

const baseURL = "http://127.0.0.1:5173";
const output = "../docs/images";
await mkdir(output, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1440, height: 1100 },
  recordVideo: { dir: "/tmp/tennis-video", size: { width: 1100, height: 850 } },
});
const page = await context.newPage();

try {
  await page.goto(baseURL, { waitUntil: "networkidle", timeout: 60000 });
  await page.screenshot({ path: `${output}/tennis-predictor.png`, fullPage: true });
  await page.getByRole("button", { name: "Predict Winner" }).click();
  await page.getByRole("status").waitFor({ state: "visible", timeout: 180000 });
  await page.waitForTimeout(1800);
  await page.screenshot({ path: `${output}/tennis-prediction.png`, fullPage: true });
} finally {
  await context.close();
  await browser.close();
}
