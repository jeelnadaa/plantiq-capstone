import { expect, test, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const LEAF = path.resolve(__dirname, "../../backend/tests/fixtures/leaves/rust_sample.jpg");
const PASSWORD = "Estate-Coffee-2026";
let counter = 0;

async function signUp(page: Page, name = "Ravi Gowda") {
  counter += 1;
  const username = `e2e_${Date.now().toString(36)}_${counter}`;
  const phone = `9${String(Date.now()).slice(-8)}${counter % 10}`;
  await page.goto("/#/signup");
  await page.locator("#su-name").fill(name);
  await page.locator("#su-user").fill(username);
  await page.locator("#su-phone").fill(phone);
  await page.locator("#su-pw").fill(PASSWORD);
  await page.locator("#su-confirm").fill(PASSWORD);
  await page.getByTestId("terms").check();
  await page.getByTestId("signup-submit").click();
  await expect(page.getByTestId("scanner")).toBeVisible();
  return { username, phone };
}

async function noHorizontalScroll(page: Page) {
  const [sw, vw] = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
  expect(sw).toBeLessThanOrEqual(vw);
}

test.describe("auth", () => {
  test("redirects to sign-in, validates sign-up, signs up, signs out and back in", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveURL(/#\/signin/);
    await page.getByTestId("tab-signup").click();
    await page.getByTestId("signup-submit").click();
    await expect(page.getByText("Enter your full name.")).toBeVisible();
    await expect(page.getByText("Please accept the terms.")).toBeVisible();
    await page.locator("#su-pw").fill("password123");
    await expect(page.getByText("Weak", { exact: true }).or(page.getByText("Too weak"))).toBeVisible();

    const { username } = await signUp(page);
    await page.getByTestId("nav-navProfile").click();
    await expect(page.getByTestId("profile-name")).toHaveText("Ravi Gowda");
    await page.getByTestId("sign-out").click();
    await expect(page).toHaveURL(/#\/signin/);

    await page.locator("#login-id").fill(username);
    await page.locator("#login-pw").fill("wrong-pass-1");
    await page.getByTestId("signin-submit").click();
    await expect(page.getByText("Incorrect login details. Check and try again.")).toBeVisible();
    await page.locator("#login-pw").fill(PASSWORD);
    await page.getByTestId("signin-submit").click();
    await expect(page.getByTestId("scanner")).toBeVisible();
  });

  test("username availability check", async ({ page }) => {
    const { username } = await signUp(page);
    await page.getByTestId("nav-navProfile").click();
    await page.getByTestId("sign-out").click();
    await expect(page).toHaveURL(/#\/signin/);
    await page.getByTestId("tab-signup").click();
    await page.locator("#su-user").fill(username);
    await expect(page.getByTestId("username-taken")).toBeVisible();
    await page.locator("#su-user").fill(`${username}x`);
    await expect(page.getByTestId("username-ok")).toBeVisible();
  });
});

test.describe("farmer journey", () => {
  test("scan a leaf → diagnosis → ask in chat → history undo", async ({ page }) => {
    await signUp(page);
    await page.getByTestId("file-input").setInputFiles(LEAF);
    await page.getByRole("button", { name: "When to spray?" }).click();
    await page.getByTestId("analyze").click();
    await expect(page.getByTestId("diagnosis")).toBeVisible();
    await expect(page.getByText("What to do")).toBeVisible();
    await expect(page.getByText("How sure is PlantIQ?")).toBeVisible();
    await noHorizontalScroll(page);

    await page.getByTestId("ask-in-chat").click();
    await expect(page.getByTestId("chat")).toBeVisible();
    await expect(page.getByTestId("msg-user").first()).toContainText("I just diagnosed");
    await expect(page.getByTestId("msg-assistant").first()).toBeVisible();
    await page.getByTestId("chat-input").fill("Any organic option?");
    await page.getByTestId("send").click();
    await expect(page.getByTestId("msg-assistant")).toHaveCount(2);
    await page.getByTestId("open-threads").click();
    await expect(page.getByTestId("thread-item")).toHaveCount(1);
    await page.keyboard.press("Escape");

    await page.getByTestId("nav-navHistory").click();
    await expect(page.getByTestId("scan-item")).toHaveCount(1);
    await page.getByTestId("delete-scan").click();
    await expect(page.getByText("No scans yet")).toBeVisible();
    await page.getByRole("button", { name: /Undo/ }).click();
    await expect(page.getByTestId("scan-item")).toHaveCount(1);
    await page.getByTestId("scan-item").click();
    await expect(page.getByTestId("scan-details")).toBeVisible();
  });

  test("chat with a photo picked from scan history", async ({ page }) => {
    await signUp(page);
    await page.getByTestId("file-input").setInputFiles(LEAF);
    await page.getByTestId("analyze").click();
    await expect(page.getByTestId("diagnosis")).toBeVisible();
    await page.getByTestId("nav-navAsk").click();
    await page.getByTestId("attach").click();
    await page.getByTestId("picker-scan").first().click();
    await expect(page.getByTestId("attach-strip")).toBeVisible();
    await page.getByTestId("chat-input").fill("What is this?");
    await page.getByTestId("send").click();
    await expect(page.getByTestId("msg-assistant")).toHaveCount(1);
    await expect(page.locator(".msg.me img")).toHaveCount(1);
  });
});

test.describe("marketplace", () => {
  test("validation modal, publish, filter, edit, delete", async ({ page }) => {
    await signUp(page);
    await page.getByTestId("nav-navMarket").click();
    await page.getByTestId("sell-fab").click();
    await page.getByTestId("publish").click();
    await expect(page.getByTestId("validation-sheet")).toBeVisible();
    await expect(page.getByTestId("validation-issue").first()).toContainText("Crop title");
    await page.getByTestId("validation-issue").first().click();
    await expect(page.locator("#lf-title")).toBeFocused();

    await page.locator("#lf-title").fill("Robusta Cherry");
    await page.locator("#lf-variety").fill("Robusta CXR");
    await page.locator("#lf-quantity").fill("40");
    await page.locator("#lf-quantity").locator("xpath=../select").selectOption("bag (50kg)");
    await page.locator("#lf-price").fill("9500");
    await page.locator("#lf-price").locator("xpath=../select").selectOption("per 50kg bag");
    await expect(page.getByText("= ₹190 per kg")).toBeVisible();
    await page.locator("#lf-address").fill("Sakleshpur, Hassan");
    await page.getByTestId("listing-photos").setInputFiles(LEAF);
    await page.getByPlaceholder("Caption (e.g. drying yard, Feb harvest)").fill("Fresh cherry");
    await page.getByTestId("publish").click();
    await expect(page.getByText("Your crop is listed!")).toBeVisible();
    await expect(page.getByTestId("listing-card")).toHaveCount(1);
    await expect(page.getByText("≈ ₹190/kg")).toBeVisible();

    await page.getByTestId("tab-all").click();
    await page.getByTestId("open-filters").click();
    await page.getByTestId("variety-Liberica").click();
    await expect(page.getByTestId("apply-filters")).toHaveText("Show 0 lots");
    await page.getByTestId("reset-filters").click();
    await expect(page.getByTestId("apply-filters")).toHaveText("Show 1 lots");
    await page.getByTestId("apply-filters").click();

    await page.getByTestId("market-search").fill("sakleshpur");
    await expect(page.getByTestId("listing-card")).toHaveCount(1);
    await page.getByTestId("edit-listing").click();
    await page.locator("#lf-price").fill("9000");
    await page.getByTestId("publish").click();
    await expect(page.getByText("Listing updated.")).toBeVisible();
    await page.getByTestId("delete-listing").click();
    await page.getByTestId("confirm-delete").click();
    await expect(page.getByText("Listing deleted.")).toBeVisible();
    await noHorizontalScroll(page);
  });

  test("buyer sees another farmer's lot and can report it once", async ({ page, browser }) => {
    await signUp(page, "Seller One");
    await page.getByTestId("nav-navMarket").click();
    await page.getByTestId("sell-fab").click();
    await page.locator("#lf-title").fill("Arabica Parchment");
    await page.locator("#lf-variety").fill("Arabica");
    await page.locator("#lf-quantity").fill("500");
    await page.locator("#lf-price").fill("420");
    await page.locator("#lf-address").fill("Mudigere");
    await page.getByTestId("publish").click();
    await expect(page.getByText("Your crop is listed!")).toBeVisible();

    const buyer = await (await browser.newContext({ ...(await import("@playwright/test")).devices["Pixel 7"] })).newPage();
    await signUp(buyer, "Buyer Two");
    await buyer.getByTestId("nav-navMarket").click();
    await expect(buyer.getByText("Arabica Parchment")).toBeVisible();
    await buyer.getByTestId("report-btn").first().click();
    await buyer.getByTestId("send-report").click();
    await expect(buyer.getByText("Thanks — the listing will be reviewed.")).toBeVisible();
    await expect(buyer.getByTestId("report-btn").first()).toBeDisabled();
  });
});

test.describe("settings, language and accessibility", () => {
  test("Kannada toggle, palette, dark mode, server ping", async ({ page }) => {
    await signUp(page);
    await page.getByTestId("lang-toggle").click();
    await expect(page.getByText("ಎಲೆ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ")).toBeVisible();
    await page.getByTestId("lang-toggle").click();
    await page.getByRole("button", { name: "Colour theme" }).click();
    await page.getByTestId("palette-monsoon").click();
    await page.getByTestId("mode-dark").click();
    expect(await page.evaluate(() => [document.documentElement.dataset.palette, document.documentElement.dataset.theme])).toEqual(["monsoon", "dark"]);
    await page.keyboard.press("Escape");
    await page.getByTestId("server-button").click();
    await page.getByRole("button", { name: "Test" }).click();
    await expect(page.getByTestId("server-ok")).toBeVisible();
    await page.locator("#server-url").fill("127.0.0.1:1");
    await page.getByRole("button", { name: "Test" }).click();
    await expect(page.getByTestId("server-down")).toBeVisible();
  });

  test("change password signs out other devices; devices list", async ({ page }) => {
    await signUp(page);
    await page.getByTestId("nav-navProfile").click();
    await page.getByTestId("menu-devices").click();
    await expect(page.getByText("This device")).toBeVisible();
    await page.keyboard.press("Escape");
    await page.getByTestId("menu-password").click();
    await page.locator("#cp-cur").fill(PASSWORD);
    await page.locator("#cp-new").fill("New-Estate-2027");
    await page.locator("#cp-conf").fill("New-Estate-2027");
    await page.getByRole("button", { name: "Save" }).click();
    await expect(page.getByText("Password changed. Other devices were signed out.")).toBeVisible();
    await page.reload();
    await expect(page.getByTestId("profile")).toBeVisible();
  });

  test("every screen: no horizontal scroll, labelled buttons, ≥40px tap targets", async ({ page }) => {
    await signUp(page);
    for (const nav of ["navScan", "navAsk", "navMarket", "navHistory", "navProfile"]) {
      await page.getByTestId(`nav-${nav}`).click();
      await page.waitForTimeout(300);
      await noHorizontalScroll(page);
      const problems = await page.evaluate(() => {
        const out: string[] = [];
        document.querySelectorAll<HTMLElement>("button, a[href], input:not([type=hidden]), select, textarea").forEach((el) => {
          const r = el.getBoundingClientRect();
          if (!r.width || !r.height || getComputedStyle(el).visibility === "hidden") return;
          const label = el.getAttribute("aria-label") || el.textContent?.trim() || (el as HTMLInputElement).placeholder ||
            (el.id && document.querySelector(`label[for="${el.id}"]`)?.textContent) || el.getAttribute("title");
          if (!label && (el as HTMLInputElement).type !== "checkbox" && (el as HTMLInputElement).type !== "file" && (el as HTMLInputElement).type !== "range") out.push(`unlabelled ${el.tagName}`);
          if (el.tagName === "BUTTON" && r.height < 40 && !el.closest(".thumbs")) out.push(`small ${el.textContent?.trim() || el.getAttribute("aria-label")} ${Math.round(r.height)}px`);
        });
        return out;
      });
      expect(problems, nav).toEqual([]);
    }
  });

  test("first-run server setup screen is shown for the APK (native) case", async ({ page }) => {
    // Simulate the bridge object the Android WebView injects, so Capacitor reports a native platform.
    await page.addInitScript(() => { (window as any).androidBridge = { postMessage: () => undefined }; });
    await page.goto("/#/");
    await expect(page.getByTestId("server-setup")).toBeVisible();
    await page.locator("#setup-url").fill("127.0.0.1:8200");
    await page.getByTestId("setup-continue").click();
    await expect(page).toHaveURL(/#\/signin/);
  });
});

test("static assets: Satoshi font bundled (works offline in the APK)", async () => {
  const dist = path.resolve(__dirname, "../dist/assets");
  expect(fs.readdirSync(dist).some((f) => f.startsWith("Satoshi-Bold"))).toBeTruthy();
});
